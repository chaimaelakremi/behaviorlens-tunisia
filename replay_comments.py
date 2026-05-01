#!/usr/bin/env python3
"""
Replay pre-scraped Facebook comments as a live stream
Perfect for hackathon demo
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime


def replay_comments(filename: str = "data/facebook_comments.json", speed: float = 1.0):
    """
    Replay saved comments at real-time pace
    
    speed: 1.0 = normal (2 sec per comment)
           2.0 = 2x faster (1 sec per comment)
           0.5 = half speed (4 sec per comment)
    """
    
    filepath = Path(filename)
    
    if not filepath.exists():
        print(f"❌ File not found: {filename}")
        print(f"   Run: python scrapy_facebook_spider.py")
        return
    
    # Load comments
    with open(filepath) as f:
        comments = json.load(f)
    
    if not comments:
        print(f"❌ No comments in {filename}")
        return
    
    print("\n" + "🔴 " * 30)
    print("  LIVE STREAM - FACEBOOK COMMENTS")
    print("🔴 " * 30 + "\n")
    
    print(f"📊 Streaming {len(comments)} comments...")
    print(f"⏱️  Speed: {speed}x")
    print(f"⏯️  Press Ctrl+C to stop\n")
    
    delay = (2.0 / speed)  # Base delay 2 seconds, adjusted by speed
    
    try:
        for idx, comment in enumerate(comments, 1):
            # Display comment
            print(f"{'─' * 70}")
            print(f"[{idx}/{len(comments)}] 💬 COMMENT")
            print(f"{'─' * 70}")
            print(f"\n{comment['text']}\n")
            print(f"👤 Source: {comment['source']}")
            print(f"📱 Platform: {comment['platform']}")
            print(f"🔗 From: {comment['url']}")
            print(f"⏰ Time: {comment['timestamp']}")
            
            # Calculate next comment time
            time_until_next = delay
            print(f"\n⏳ Next comment in {time_until_next:.1f}s...", end="", flush=True)
            
            # Wait with interruption check
            start = time.time()
            while time.time() - start < time_until_next:
                time.sleep(0.1)
            
            print("\r" + " " * 50 + "\r", end="", flush=True)  # Clear line
        
        print(f"\n{'=' * 70}")
        print("✅ STREAM COMPLETE")
        print(f"{'=' * 70}\n")
        print(f"📊 Streamed {len(comments)} comments")
        print(f"⏱️  Total time: {len(comments) * delay:.1f} seconds\n")
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️  Stream stopped by user")
        print(f"📊 Streamed {idx}/{len(comments)} comments")


def stats_only(filename: str = "data/facebook_comments.json"):
    """Show statistics about scraped data"""
    
    filepath = Path(filename)
    
    if not filepath.exists():
        print(f"❌ File not found: {filename}")
        return
    
    with open(filepath) as f:
        comments = json.load(f)
    
    if not comments:
        print(f"❌ No comments in {filename}")
        return
    
    print("\n📊 COMMENT STATISTICS")
    print("=" * 70)
    print(f"Total comments: {len(comments)}")
    print(f"Sources: {set(c['source'] for c in comments)}")
    print(f"Platforms: {set(c['platform'] for c in comments)}")
    print(f"Date range: {comments[0]['timestamp']} to {comments[-1]['timestamp']}")
    print(f"Average comment length: {sum(len(c['text']) for c in comments) // len(comments)} chars")
    print("\n🔝 TOP 3 LONGEST COMMENTS:")
    for i, comment in enumerate(sorted(comments, key=lambda c: len(c['text']), reverse=True)[:3], 1):
        print(f"\n{i}. ({len(comment['text'])} chars)")
        print(f"   {comment['text'][:80]}...")


def main():
    """Main CLI"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Replay pre-scraped Facebook comments for hackathon demo"
    )
    parser.add_argument(
        "--file",
        default="data/facebook_comments.json",
        help="JSON file with comments (default: data/facebook_comments.json)"
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Playback speed (1.0=normal, 2.0=2x faster, 0.5=slower)"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics only (don't stream)"
    )
    
    args = parser.parse_args()
    
    if args.stats:
        stats_only(args.file)
    else:
        replay_comments(args.file, args.speed)


if __name__ == "__main__":
    main()
