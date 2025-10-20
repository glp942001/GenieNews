"""
AI service for article curation using OpenAI API.

Provides methods for:
- Generating article summaries (short and detailed)
- Creating embeddings for vector search
- Extracting AI/tech tags
- Calculating relevance scores
"""
import logging
import time
from typing import Dict, List, Tuple, Optional
import re

from django.conf import settings
from openai import OpenAI, OpenAIError, RateLimitError, APIConnectionError
import tiktoken

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Custom exception for AI service errors."""
    pass


class AIService:
    """Service class for OpenAI API interactions."""
    
    def __init__(self):
        """Initialize OpenAI client with API key from settings."""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.AI_MODEL
        self.embedding_model = settings.EMBEDDING_MODEL
        self.temperature = settings.AI_TEMPERATURE
        self.max_tokens = settings.AI_MAX_TOKENS
        self.relevance_keywords = [kw.strip().lower() for kw in settings.AI_RELEVANCE_KEYWORDS]
        
    def _retry_with_backoff(self, func, max_attempts=3):
        """Execute function with exponential backoff retry logic."""
        for attempt in range(max_attempts):
            try:
                return func()
            except RateLimitError as e:
                if attempt == max_attempts - 1:
                    raise AIServiceError(f"Rate limit exceeded after {max_attempts} attempts: {str(e)}")
                wait_time = (2 ** attempt) * 2  # 2, 4, 8 seconds
                logger.warning(f"Rate limit hit, waiting {wait_time}s before retry {attempt + 1}/{max_attempts}")
                time.sleep(wait_time)
            except APIConnectionError as e:
                if attempt == max_attempts - 1:
                    raise AIServiceError(f"API connection failed after {max_attempts} attempts: {str(e)}")
                wait_time = (2 ** attempt) * 1
                logger.warning(f"Connection error, retrying in {wait_time}s")
                time.sleep(wait_time)
            except OpenAIError as e:
                raise AIServiceError(f"OpenAI API error: {str(e)}")
        
    def generate_summaries(self, article_text: str, title: str) -> Tuple[str, str]:
        """
        Generate both short and detailed summaries for an article.
        
        Args:
            article_text: Full article text (combination of summary_feed and raw_html if available)
            title: Article title
            
        Returns:
            Tuple of (summary_short, summary_detailed)
        """
        # Truncate text if too long (roughly 8000 tokens max)
        truncated_text = self._truncate_text(article_text, max_tokens=8000)
        
        prompt = f"""You are a news summarization assistant specializing in AI and technology news.

Article Title: {title}

Article Content:
{truncated_text}

Generate TWO summaries:

1. SHORT SUMMARY (1-2 sentences): A concise overview suitable for a news feed card.
2. DETAILED SUMMARY (3-4 paragraphs): A comprehensive summary covering key points, implications, and context.

Focus on:
- Key facts and findings
- Technical details and innovations
- Industry impact and implications
- Objective, neutral tone

Format your response EXACTLY as:
SHORT: [your 1-2 sentence summary]

DETAILED: [your 3-4 paragraph summary]"""

        def _call_api():
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert AI and technology news summarization assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        
        try:
            result = self._retry_with_backoff(_call_api)
            
            # Parse response
            short_summary, detailed_summary = self._parse_summaries(result)
            
            logger.info(f"Generated summaries for article: {title[:50]}...")
            return short_summary, detailed_summary
            
        except Exception as e:
            logger.error(f"Error generating summaries: {str(e)}")
            # Return fallback summaries
            return (
                f"{title[:200]}..." if len(title) > 200 else title,
                truncated_text[:1000] if truncated_text else title
            )
    
    def _parse_summaries(self, response: str) -> Tuple[str, str]:
        """Parse the API response to extract short and detailed summaries."""
        # Try to extract SHORT and DETAILED sections
        short_match = re.search(r'SHORT:\s*(.+?)(?=DETAILED:|$)', response, re.DOTALL | re.IGNORECASE)
        detailed_match = re.search(r'DETAILED:\s*(.+?)$', response, re.DOTALL | re.IGNORECASE)
        
        short_summary = short_match.group(1).strip() if short_match else ""
        detailed_summary = detailed_match.group(1).strip() if detailed_match else ""
        
        # Fallback: split by double newline if format not followed
        if not short_summary or not detailed_summary:
            parts = response.split('\n\n', 1)
            short_summary = parts[0].strip()
            detailed_summary = parts[1].strip() if len(parts) > 1 else parts[0].strip()
        
        # Ensure summaries are within length limits
        if len(short_summary) > 500:
            short_summary = short_summary[:497] + "..."
        
        return short_summary, detailed_summary
    
    def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings for text using OpenAI's embedding model.
        
        Args:
            text: Text to embed (typically the detailed summary)
            
        Returns:
            List of 1536 floats representing the embedding vector
        """
        # Truncate text if too long (8191 tokens max for embedding model)
        truncated_text = self._truncate_text(text, max_tokens=8000)
        
        def _call_api():
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=truncated_text
            )
            return response.data[0].embedding
        
        try:
            embedding = self._retry_with_backoff(_call_api)
            logger.info(f"Generated embedding vector (dim={len(embedding)})")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            # Return zero vector as fallback
            return [0.0] * 1536
    
    def generate_tags(self, article_text: str, title: str) -> List[str]:
        """
        Extract relevant AI/tech tags from article content.
        
        Args:
            article_text: Full article text
            title: Article title
            
        Returns:
            List of tags (e.g., ["GPT-4", "computer-vision", "OpenAI"])
        """
        truncated_text = self._truncate_text(article_text, max_tokens=4000)
        
        prompt = f"""Extract 3-8 relevant technical tags from this AI/technology article.

Title: {title}
Content: {truncated_text[:1000]}

Requirements:
- Tags should be specific and technical (e.g., "GPT-4", "computer-vision", "transformer-architecture")
- Focus on: AI models, techniques, companies, research areas, technologies
- Use kebab-case for multi-word tags
- Prioritize AI and machine learning topics
- Avoid generic tags like "technology" or "news"

Return ONLY a comma-separated list of tags, nothing else.
Example: GPT-4,natural-language-processing,OpenAI,large-language-models"""

        def _call_api():
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting technical tags from AI and technology articles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            return response.choices[0].message.content
        
        try:
            result = self._retry_with_backoff(_call_api)
            
            # Parse comma-separated tags
            tags = [tag.strip().lower() for tag in result.split(',')]
            tags = [tag for tag in tags if tag and len(tag) > 1][:8]  # Limit to 8 tags
            
            logger.info(f"Generated tags: {tags}")
            return tags
            
        except Exception as e:
            logger.error(f"Error generating tags: {str(e)}")
            # Return basic tags extracted from title
            return self._extract_basic_tags(title)
    
    def calculate_relevance_score(self, article_text: str, title: str) -> float:
        """
        Calculate relevance score (0-1) based on AI/tech focus.
        
        Uses a combination of:
        - Keyword matching with relevance keywords
        - AI-based semantic relevance assessment
        
        Args:
            article_text: Full article text
            title: Article title
            
        Returns:
            Float between 0 and 1 (higher = more relevant to AI/tech)
        """
        # Keyword-based score (quick check)
        keyword_score = self._calculate_keyword_score(title + " " + article_text)
        
        # If keyword score is very low, skip AI call to save costs
        if keyword_score < 0.1:
            logger.info(f"Low keyword score ({keyword_score:.2f}), skipping AI relevance check")
            return keyword_score
        
        # AI-based semantic relevance
        try:
            ai_score = self._calculate_ai_relevance(article_text, title)
            # Combine scores (weighted average: 30% keyword, 70% AI)
            final_score = (0.3 * keyword_score) + (0.7 * ai_score)
            logger.info(f"Relevance score: {final_score:.2f} (keyword: {keyword_score:.2f}, AI: {ai_score:.2f})")
            return round(final_score, 3)
        except Exception as e:
            logger.error(f"Error calculating AI relevance: {str(e)}")
            # Fallback to keyword score only
            return keyword_score
    
    def _calculate_keyword_score(self, text: str) -> float:
        """Calculate relevance score based on keyword matching."""
        text_lower = text.lower()
        matches = 0
        total_keywords = len(self.relevance_keywords)
        
        for keyword in self.relevance_keywords:
            if keyword in text_lower:
                matches += 1
        
        # Calculate score with diminishing returns
        score = min(1.0, matches / (total_keywords * 0.2))  # 20% keyword match = max score
        return round(score, 3)
    
    def _calculate_ai_relevance(self, article_text: str, title: str) -> float:
        """Use AI to assess semantic relevance to AI/tech topics."""
        truncated_text = self._truncate_text(article_text, max_tokens=2000)
        
        prompt = f"""Rate the relevance of this article to AI and emerging technology topics on a scale from 0 to 10.

Title: {title}
Content: {truncated_text[:800]}

Consider:
- AI research and breakthroughs
- New AI products or services
- Machine learning techniques and applications
- AI company news and developments
- AI ethics, policy, and societal impact
- Robotics, autonomous systems
- Natural language processing, computer vision
- Emerging tech closely related to AI

Rate from 0-10:
- 10: Highly relevant to AI/ML (e.g., major AI research, new AI model release)
- 7-9: Clearly AI-related (e.g., AI company news, AI applications)
- 4-6: Somewhat relevant (e.g., tech news with AI angle)
- 1-3: Tangentially related to AI
- 0: Not related to AI or technology

Return ONLY a single number from 0-10, nothing else."""

        def _call_api():
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at assessing AI and technology news relevance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=10
            )
            return response.choices[0].message.content
        
        try:
            result = self._retry_with_backoff(_call_api)
            
            # Extract number from response
            score_match = re.search(r'\d+', result)
            if score_match:
                score = int(score_match.group())
                # Normalize to 0-1 range
                return round(score / 10.0, 3)
            else:
                logger.warning(f"Could not parse AI relevance score: {result}")
                return 0.5
                
        except Exception as e:
            logger.error(f"Error in AI relevance calculation: {str(e)}")
            return 0.5
    
    def _truncate_text(self, text: str, max_tokens: int = 8000) -> str:
        """Truncate text to fit within token limit."""
        try:
            encoding = tiktoken.encoding_for_model(self.model)
            tokens = encoding.encode(text)
            
            if len(tokens) > max_tokens:
                truncated_tokens = tokens[:max_tokens]
                return encoding.decode(truncated_tokens)
            return text
        except Exception as e:
            logger.warning(f"Error truncating text with tiktoken: {str(e)}, using character-based truncation")
            # Fallback: rough character-based truncation (4 chars per token estimate)
            max_chars = max_tokens * 4
            return text[:max_chars]
    
    def _extract_basic_tags(self, title: str) -> List[str]:
        """Extract basic tags from title as fallback."""
        # Simple keyword extraction
        title_lower = title.lower()
        tags = []
        
        # Check for common AI/tech terms
        tag_keywords = {
            'ai': 'artificial-intelligence',
            'machine learning': 'machine-learning',
            'deep learning': 'deep-learning',
            'neural network': 'neural-networks',
            'gpt': 'gpt',
            'openai': 'openai',
            'google': 'google',
            'microsoft': 'microsoft',
            'llm': 'large-language-models',
            'chatgpt': 'chatgpt',
            'computer vision': 'computer-vision',
            'nlp': 'natural-language-processing',
            'robotics': 'robotics',
            'autonomous': 'autonomous-systems',
        }
        
        for keyword, tag in tag_keywords.items():
            if keyword in title_lower:
                tags.append(tag)
        
        return tags[:5] if tags else ['technology', 'ai']


# Global service instance
_ai_service = None


def get_ai_service() -> AIService:
    """Get or create global AI service instance."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service

