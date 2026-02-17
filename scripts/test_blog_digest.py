#!/usr/bin/env python3
# ABOUTME: Manual test script for blog scraping pipeline
# ABOUTME: Runs pipeline without waiting for scheduler, optional dry-run mode

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.blog.processor import BlogProcessor
from src.config import BLOG_SOURCES_FILE


def main():
    parser = argparse.ArgumentParser(description="Test blog digest pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Process but don't send Telegram")
    parser.add_argument("--sources", type=Path, default=BLOG_SOURCES_FILE, help="Path to blog_sources.json")
    args = parser.parse_args()

    processor = BlogProcessor(sources_file=args.sources)
    result = processor.process()

    if result["success"]:
        print(f"\n✅ Success - {result['blog_count']} blogs processed")
        print(f"📁 Folder: {result['folder']}")
        print("\n--- SUMMARY ---\n")
        print(result["summary"])
    else:
        print(f"\n❌ Failed: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
