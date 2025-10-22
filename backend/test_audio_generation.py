#!/usr/bin/env python
"""
Quick test script to manually generate an audio segment.
Run this to test the audio generation workflow without waiting for Celery.
"""
import os
import django
import sys

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'genienews_backend.settings')
django.setup()

from news.tasks import generate_audio_segment_task
from news.models import AudioSegment
from datetime import date

def main():
    print("=" * 60)
    print("Audio Segment Generation Test")
    print("=" * 60)
    print()
    
    # Check for existing audio today
    today = date.today()
    existing = AudioSegment.objects.filter(date=today).first()
    
    if existing:
        print(f"⚠️  Audio segment already exists for {today}")
        print(f"   - Audio file: {existing.audio_file}")
        print(f"   - Articles: {len(existing.article_ids)}")
        print(f"   - Duration: {existing.duration_seconds}s")
        print()
        response = input("Delete and regenerate? (y/n): ")
        if response.lower() == 'y':
            existing.delete()
            print("✅ Deleted existing segment")
        else:
            print("❌ Cancelled")
            return
    
    print()
    print("🚀 Starting audio generation...")
    print("   This will take 20-30 seconds")
    print()
    
    # Run the task synchronously (not via Celery)
    try:
        result = generate_audio_segment_task()
        
        print()
        print("=" * 60)
        if result['status'] == 'success':
            print("✅ SUCCESS!")
            print()
            print(f"📅 Date: {result['date']}")
            print(f"📁 File: {result['filename']}")
            print(f"📰 Articles: {result['article_count']}")
            print(f"⏱️  Duration: {result['duration_seconds']}s")
            print(f"⚡ Generation time: {result['execution_time']}s")
            print()
            print("🎧 Audio is ready! Refresh your frontend to listen.")
        else:
            print("❌ FAILED!")
            print()
            print(f"Error: {result['message']}")
        print("=" * 60)
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERROR!")
        print(f"   {str(e)}")
        print("=" * 60)
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

