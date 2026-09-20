#!/usr/bin/env python3
"""Generate a Codex report from saved files without IMAP or Telegram."""
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.executor import PROJECT_ROOT
from src.newsletter.codex_runner import CodexRunner
from src.blog.summarizer import BlogSummarizer

if __name__ == "__main__":
    load_dotenv(PROJECT_ROOT / ".env")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=["newsletter", "blog"])
    parser.add_argument("folder", type=Path)
    args = parser.parse_args()
    if args.kind == "newsletter":
        print(CodexRunner().analyze_newsletters(str(args.folder)))
    else:
        print(BlogSummarizer().summarize(args.folder))
