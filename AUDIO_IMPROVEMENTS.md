# Audio Generation Improvements

## Summary of Changes

We've enhanced the AI audio news generation to sound more like a real newscaster with personality, humor, and better pacing instead of just reading a list.

## What Was Changed

### 1. **Enhanced Script Generation Prompt** (`ai_service.py` - `generate_news_script()`)

**Old Approach:**
- Professional but dry news anchor tone
- Basic structure with intro/segments/outro
- Focused on clear facts

**New Approach:**
- **Storytelling Focus**: Scripts now lead with "wow factor" and tell stories, not lists
- **Personality & Humor**: Added light humor, clever observations, and conversational language
- **Natural Transitions**: Use phrases like "Now here's something wild...", "But wait, there's more..."
- **Varied Pacing**: Mix of short punchy statements with longer explanatory sentences
- **Engaging Style**: Think "NPR meets late-night comedy" - professional but entertaining
- **Better Prompts for AI**: Emphasizes dramatic pauses with ellipses (...), exclamations, rhetorical questions

### 2. **Improved System Prompt for Script Generation**

**Old:** "Professional news script writer"

**New:** "Award-winning radio personality and storyteller who captivates audiences with personality, humor, and natural delivery"

- Increased `temperature` from 0.7 to 0.8 for more creativity
- Increased `max_tokens` from 2000 to 2500 for longer, more conversational scripts

### 3. **Changed Voice & Audio Settings** (`ai_service.py` - `generate_audio_from_script()`)

**Voice Changes:**
- Attempting to use **"maple"** voice as requested (with fallback to **"nova"** if not available)
- Nova is warm, engaging, and has good personality
- Added speed adjustment: `speed=0.95` (5% slower for better clarity and natural pausing)

**Note:** "Maple" may only be available in ChatGPT's Advanced Voice Mode. If it's not available in the TTS API, the code will automatically fall back to "nova" which is the next best option.

### 4. **Added Automatic Pacing Enhancement** (New Method: `_enhance_script_pacing()`)

This method automatically enhances the script before sending to TTS:
- Adds pauses (...)  after sentences (periods)
- Adds longer pauses after exclamations and questions
- Adds pauses after paragraph breaks for better sectioning
- Adds slight pauses at commas for natural breathing points

This helps the TTS engine create more natural pauses between sentences and ideas.

## How to Test

### Generate New Audio

1. **Via Django Admin:**
   - Go to: `http://localhost:8000/admin/news/audiosegment/`
   - Delete any existing segments for today if you want to regenerate
   - Trigger the generation task

2. **Via Management Command:**
   ```bash
   cd backend
   python manage.py shell
   ```
   ```python
   from news.tasks import generate_audio_segment_task
   result = generate_audio_segment_task()
   print(result)
   ```

3. **Via Test Script:**
   ```bash
   cd backend
   python test_audio_generation.py
   ```

4. **Via API Endpoint:**
   ```bash
   curl -X POST http://localhost:8000/api/news/audio/generate/ \
        -H "Content-Type: application/json"
   ```

### Listen to Results

Audio files are saved to: `backend/media/audio_segments/YYYY-MM-DD.mp3`

Play them to hear:
- ✅ More personality and humor
- ✅ Storytelling instead of list-reading
- ✅ Better pacing with natural pauses
- ✅ Varied sentence structure and rhythm
- ✅ Engaging, conversational tone

## Voice Options & Configuration

### Easy Configuration via Environment Variables

You can now easily change voice and speed without editing code! Just set these in your `.env` file:

```bash
# Text-to-Speech Configuration
TTS_VOICE=nova          # Change to: alloy, echo, fable, onyx, nova, shimmer, maple
TTS_SPEED=0.95          # Speed: 0.25 to 4.0 (1.0 = normal, 0.95 = slightly slower)
TTS_MODEL=tts-1-hd      # Options: tts-1 (faster), tts-1-hd (higher quality)
```

### Available TTS API Voices

- **alloy** - Neutral, balanced voice
- **echo** - Male voice
- **fable** - Expressive, British-accented
- **onyx** - Deep, authoritative male voice
- **nova** - Warm, engaging female voice (current default) ⭐
- **shimmer** - Soft, gentle voice
- **maple** - May be available (will fallback to nova if not)

### Quick Voice Change

1. Edit `backend/.env`:
   ```bash
   TTS_VOICE=fable  # Try a different voice
   TTS_SPEED=1.0    # Normal speed
   ```

2. Restart Django server:
   ```bash
   # No need to restart if running via manage.py shell
   # But restart if using runserver
   ```

3. Generate new audio

## Expected Results

**Before:**
- Monotone delivery
- Sounded like reading a list of bullet points
- Minimal pausing between sentences
- Dry, robotic tone

**After:**
- Dynamic, engaging delivery
- Story-driven narratives with context
- Natural pauses and rhythm
- Personality, humor, and conversational style
- Sounds like talking to a friend about news

## Technical Details

**Files Modified:**
- `backend/news/ai_service.py`
  - Updated `generate_news_script()` method (lines ~633-674)
  - Enhanced system prompt (line 680)
  - Added `_enhance_script_pacing()` method (lines 704-722)
  - Updated `generate_audio_from_script()` method (lines 724-758)

**Key Parameters:**
- Script temperature: 0.8 (more creative)
- Max tokens: 2500 (longer scripts)
- TTS voice: "maple" (fallback to "nova")
- TTS speed: 0.95 (slightly slower)
- Automatic pause injection

## Troubleshooting

### If "maple" voice fails:
The code will automatically fall back to "nova". Check the logs:
```bash
cd backend
tail -f logs/django.log  # or wherever your logs are
```

Look for: `Voice 'maple' not available, falling back to 'nova'`

### If audio sounds too slow:
Change the speed parameter in `ai_service.py` line 746:
```python
speed=1.0  # Normal speed (was 0.95)
```

### If you want more/fewer pauses:
Adjust the `_enhance_script_pacing()` method (lines 704-722) to add or remove ellipses.

### If script is too casual:
Reduce temperature in line 683:
```python
temperature=0.7,  # Less creative, more professional (was 0.8)
```

## Next Steps

1. Generate a new audio segment with these changes
2. Listen and evaluate the improvements
3. Fine-tune voice, speed, or prompt as needed
4. Consider adding more specific voice instructions based on results

Enjoy your new AI newscaster with personality! 🎙️✨

