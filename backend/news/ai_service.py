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
        # TTS settings
        self.tts_voice = settings.TTS_VOICE
        self.tts_speed = settings.TTS_SPEED
        self.tts_model = settings.TTS_MODEL
        
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
    
    def generate_structured_summary(self, article_data: Dict) -> Dict[str, str]:
        """
        Generate a structured summary with keypoints format.
        
        Args:
            article_data: Dict containing article info (title, summary_detailed, url, source)
            
        Returns:
            Dict with 'keypoints' key containing structured bullet points
        """
        title = article_data.get('title', '')
        content = article_data.get('summary_detailed', '') or article_data.get('summary_short', '')
        
        # Truncate content if too long
        truncated_content = self._truncate_text(content, max_tokens=4000)
        
        prompt = f"""You are an expert AI news analyst. Analyze this article and provide a structured summary organized by themes/categories.

Article Title: {title}
Article Content: {truncated_content}

Create a structured summary organized into 3-4 thematic categories. Each category should have 2-3 key points.

Use these category types (choose the most relevant):
- 📰 WHAT'S NEW: Main announcement, development, or breakthrough
- ⚙️ TECHNICAL DETAILS: Key innovations, features, or specifications
- 💼 BUSINESS IMPACT: Market implications, industry effects, competitive landscape
- 🎯 WHY IT MATTERS: Significance to AI/tech community, future implications
- 🔮 LOOKING AHEAD: Future developments, next steps, or predictions

Format your response EXACTLY like this:

CATEGORY: [Choose appropriate category name]
• [Key point 1]
• [Key point 2]

CATEGORY: [Choose appropriate category name]
• [Key point 1]
• [Key point 2]

CATEGORY: [Choose appropriate category name]
• [Key point 1]
• [Key point 2]

Keep each point concise (1-2 sentences) and highly informative."""

        def _call_api():
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert AI and technology news analyst who creates clear, structured keypoint summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            return response.choices[0].message.content
        
        try:
            result = self._retry_with_backoff(_call_api)
            
            # Parse the keypoints response
            structured = self._parse_keypoints_summary(result)
            
            logger.info(f"Generated keypoints summary for: {title[:50]}...")
            return structured
            
        except Exception as e:
            logger.error(f"Error generating keypoints summary: {str(e)}")
            # Return fallback keypoints summary
            return {
                'categories': [
                    {
                        'name': '📰 SUMMARY',
                        'points': [
                            title[:150] if len(title) > 150 else title,
                            "This article covers important developments in AI and technology"
                        ]
                    }
                ]
            }
    
    def _parse_keypoints_summary(self, response: str) -> Dict[str, List[str]]:
        """Parse the API response to extract categorized keypoints."""
        categories = []
        
        # Split by lines and parse categories
        lines = response.split('\n')
        current_category = None
        current_points = []
        
        for line in lines:
            line = line.strip()
            
            # Check if this is a category header
            if line.upper().startswith('CATEGORY:'):
                # Save previous category if exists
                if current_category and current_points:
                    categories.append({
                        'name': current_category,
                        'points': current_points
                    })
                
                # Start new category
                category_name = line.split(':', 1)[1].strip()
                current_category = category_name
                current_points = []
            
            # Check if this is a bullet point
            elif line.startswith(('•', '-', '*')) or re.match(r'^\d+\.', line):
                if current_category:  # Only add if we have a category
                    # Clean up the bullet point
                    clean_point = re.sub(r'^[•\-*]\s*', '', line)
                    clean_point = re.sub(r'^\d+\.\s*', '', clean_point)
                    if clean_point and len(clean_point) > 10:
                        current_points.append(clean_point)
        
        # Save last category
        if current_category and current_points:
            categories.append({
                'name': current_category,
                'points': current_points
            })
        
        # If no categories found, fallback to simple keypoints format
        if not categories:
            keypoints = []
            for line in lines:
                line = line.strip()
                if line.startswith(('•', '-', '*')) or re.match(r'^\d+\.', line):
                    clean_point = re.sub(r'^[•\-*]\s*', '', line)
                    clean_point = re.sub(r'^\d+\.\s*', '', clean_point)
                    if clean_point and len(clean_point) > 10:
                        keypoints.append(clean_point)
            
            if keypoints:
                return {'keypoints': keypoints[:6]}
            else:
                return {
                    'keypoints': [
                        "This article covers important developments in AI and technology",
                        "Stay informed about the latest advancements in this field"
                    ]
                }
        
        # Return categorized format
        return {'categories': categories[:4]}  # Limit to 4 categories max
    
    def chat_with_context(self, user_message: str, articles_context: List[Dict], conversation_history: List[Dict] = None) -> str:
        """
        Generate AI chat response with context about top articles.
        
        Args:
            user_message: The user's question or message
            articles_context: List of article dicts with title, summary, url, source
            conversation_history: Optional list of previous messages [{'role': 'user'/'assistant', 'content': '...'}]
            
        Returns:
            AI-generated response string
        """
        # Build context summary of articles
        articles_text = self._build_articles_context(articles_context)
        
        system_prompt = f"""You are an intelligent AI assistant helping users understand the latest AI and technology news.

You have access to these TOP 8 CURATED ARTICLES:

{articles_text}

Your role:
- Answer questions about these articles clearly and concisely
- Cite specific articles by title when relevant
- Provide insights and connections between different articles
- Be helpful, informative, and engaging
- If asked about something not in the articles, politely indicate you're focused on the curated news

Keep responses conversational and under 200 words unless more detail is specifically requested."""

        # Build messages array with conversation history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Keep last 6 messages for context
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        def _call_api():
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=500
            )
            return response.choices[0].message.content
        
        try:
            result = self._retry_with_backoff(_call_api)
            logger.info(f"Generated chat response for message: {user_message[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."
    
    def _build_articles_context(self, articles: List[Dict]) -> str:
        """Build a formatted context string from articles list."""
        context_parts = []
        
        for i, article in enumerate(articles[:8], 1):
            title = article.get('title', 'Untitled')
            source = article.get('source_name', 'Unknown Source')
            summary = article.get('summary_short', '') or article.get('summary_detailed', '')[:300]
            url = article.get('url', '')
            
            context_parts.append(
                f"{i}. \"{title}\" (Source: {source})\n"
                f"   Summary: {summary}\n"
                f"   URL: {url}"
            )
        
        return "\n\n".join(context_parts)
    
    def generate_news_script(self, articles: List[Dict]) -> str:
        """
        Generate a professional radio-style news script from articles.
        
        Args:
            articles: List of article dicts with title, summary, source, etc.
            
        Returns:
            Professional news script text (~4000-5000 characters for 5 minutes)
        """
        # Build articles context
        articles_text = []
        for i, article in enumerate(articles[:8], 1):
            title = article.get('title', 'Untitled')
            source = article.get('source_name', 'Unknown Source')
            summary = article.get('summary_detailed', '') or article.get('summary_short', '')
            
            articles_text.append(
                f"Article {i}:\n"
                f"Title: {title}\n"
                f"Source: {source}\n"
                f"Summary: {summary[:400]}"
            )
        
        articles_context = "\n\n".join(articles_text)
        
        prompt = f"""You are a charismatic and engaging news anchor writing a script for an AI news broadcast. Think NPR meets late-night comedy - professional but approachable, informative but entertaining.

Here are today's top 8 AI and technology stories:

{articles_context}

Create a compelling radio news script with personality and storytelling. The script should flow seamlessly from story to story without any labels or section markers.

STRUCTURE GUIDELINES (but don't label these in the script!):
- Strong opening: Hook listeners with personality and energy
- Story segments: Cover ALL 8 stories with engaging details, context, and why they matter
- Natural flow: Stories should blend into each other conversationally
- Memorable closing: Reflect on the bigger picture with warmth

STORYTELLING APPROACH:
- Lead each story with the "wow factor" - why should anyone care?
- Tell stories, not bullet points
- Add light humor, clever observations, and analogies
- Use rhetorical questions and reactions: "Wild, right?", "Get this..."
- Vary sentence length for natural rhythm
- Connect stories with seamless transitions: "Speaking of...", "And here's something that'll blow your mind...", "Now, this is interesting..."

CRITICAL REQUIREMENTS:
- Write ONLY the words that will be spoken aloud
- NO labels like "INTRO", "ARTICLE 1", "TRANSITION", "OUTRO" - these should NOT appear in the script
- Flow seamlessly from one story to the next without announcing sections
- Write as if talking to a smart friend over coffee
- Use natural pauses with periods and commas
- Cover ALL 8 stories - make sure each story is engaging with personality and context
- Each story should have substance - explain what happened, why it matters, and add your unique spin
- Keep the energy high and the content flowing naturally
- Don't just list facts - tell stories that listeners will remember
- Every word should sound authentic when spoken
- Create a continuous narrative, not separate segments

IMPORTANT:
- Make sure ALL 8 stories are covered in the script
- Each story should be engaging and informative
- Use natural transitions between all 8 stories
- Keep listeners interested throughout

EXAMPLE OF GOOD FLOW:
"Hey there! Microsoft just dropped something incredible with their new Copilot voice assistant... But that's just the beginning. Over at DeepSeek, they're doing something wild with text compression... And speaking of innovation, check out what Mila researchers discovered..."

Remember: Cover all 8 stories naturally and engagingly!"""

        def _call_api():
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an award-winning radio personality known for your detailed, in-depth storytelling. Your 5-minute news segments are COMPREHENSIVE and THOROUGH - you never rush through stories. You elaborate extensively, use vivid examples, provide context, and make every story feel important. Your scripts are LONG and DETAILED (3800-4000 characters minimum). You're verbose in the best way - every word adds value and keeps listeners engaged."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # Slightly lower for more focused, longer output
                max_tokens=4000  # Maximum to allow for full 5-minute scripts
            )
            return response.choices[0].message.content
        
        try:
            script = self._retry_with_backoff(_call_api)
            logger.info(f"Generated news script ({len(script)} characters)")
            return script
            
        except Exception as e:
            logger.error(f"Error generating news script: {str(e)}")
            # Return fallback script
            fallback = "Welcome to today's AI news briefing. "
            for i, article in enumerate(articles[:8], 1):
                title = article.get('title', 'Untitled')
                source = article.get('source_name', 'Unknown')
                fallback += f"{title}, from {source}. "
            fallback += "Thank you for listening to today's AI news update."
            return fallback
    
    def _enhance_script_pacing(self, script_text: str) -> str:
        """
        Enhance script with better pacing cues for TTS.
        Adds pauses after sentences and paragraphs for more natural delivery.
        Note: Must keep under 4096 characters for OpenAI TTS API.
        """
        # Check if script is close to limit (need to stay under 4096)
        if len(script_text) > 4000:
            # Script is too long, reduce it first
            logger.warning(f"Script is {len(script_text)} chars, truncating to fit TTS limit")
            script_text = script_text[:4000] + "... And that's today's AI news update. Thanks for listening!"
        
        # Add subtle pauses - be conservative to stay under 4096 char limit
        enhanced = script_text
        
        # Only add pauses after sentences (periods)
        enhanced = enhanced.replace('. ', '. ')  # Keep natural for now
        
        # Add brief pauses after exclamations and questions
        enhanced = enhanced.replace('! ', '!  ')
        enhanced = enhanced.replace('? ', '?  ')
        
        # Add pauses after paragraph breaks
        enhanced = enhanced.replace('\n\n', '.\n\n')
        
        # Ensure we're under the limit
        if len(enhanced) > 4096:
            enhanced = enhanced[:4090] + "..."
        
        return enhanced
    
    def generate_audio_from_script(self, script_text: str, output_path: str) -> str:
        """
        Generate audio file from script text using OpenAI TTS.
        
        Args:
            script_text: The news script to convert to speech
            output_path: Full path where audio file should be saved
            
        Returns:
            Path to the generated audio file
        """
        # Enhance script with better pacing cues
        enhanced_script = self._enhance_script_pacing(script_text)
        
        def _call_api():
            # Use TTS settings from Django settings
            # Available voices: alloy, echo, fable, onyx, nova, shimmer
            # Note: "maple" may be available in Advanced Voice Mode but might not be in standard TTS API
            try:
                response = self.client.audio.speech.create(
                    model=self.tts_model,
                    voice=self.tts_voice,
                    input=enhanced_script,
                    speed=self.tts_speed
                )
                logger.info(f"Generated audio with voice: {self.tts_voice}, speed: {self.tts_speed}")
                return response
            except Exception as e:
                # If configured voice doesn't work, fallback to nova
                if self.tts_voice != 'nova':
                    logger.warning(f"Voice '{self.tts_voice}' not available, falling back to 'nova': {str(e)}")
                    response = self.client.audio.speech.create(
                        model=self.tts_model,
                        voice="nova",
                        input=enhanced_script,
                        speed=self.tts_speed
                    )
                    return response
                else:
                    raise  # Re-raise if even nova fails
        
        try:
            logger.info(f"Generating audio from script ({len(script_text)} characters)")
            
            # Call OpenAI TTS API
            response = self._retry_with_backoff(_call_api)
            
            # Save audio to file
            response.stream_to_file(output_path)
            
            logger.info(f"Audio saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            raise AIServiceError(f"Failed to generate audio: {str(e)}")


# Global service instance
_ai_service = None


def get_ai_service() -> AIService:
    """Get or create global AI service instance."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service

