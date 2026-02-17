# ABOUTME: Orchestrates blog scraping pipeline
# ABOUTME: Loads sources, runs per-blog fetch, summarizes results, returns digest

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from src.blog.runner import BlogRunner
from src.blog.summarizer import BlogSummarizer

logger = logging.getLogger(__name__)


class BlogProcessor:
    """Orchestrates the blog scraping and summarization pipeline."""

    def __init__(self, sources_file: Path, base_dir: Path = None):
        self.sources_file = sources_file
        self.base_dir = base_dir or Path("tech-blog-summaries")
        self.runner = BlogRunner()
        self.summarizer = BlogSummarizer()

    def process(self) -> Dict[str, Any]:
        """
        Run complete blog scraping pipeline.

        Returns:
            Dict with:
            {
                "success": bool,
                "blog_count": int,
                "folder": str | None,
                "summary": str,
                "error": str (if failed)
            }
        """
        try:
            if not self.sources_file.exists():
                raise FileNotFoundError(f"Blog sources file not found: {self.sources_file}")

            sources = json.loads(self.sources_file.read_text())["sources"]

            week_num = datetime.now().isocalendar()[1]
            year = datetime.now().year
            folder_name = f"{week_num:02d}_{year}"
            output_dir = self.base_dir / folder_name
            output_dir.mkdir(parents=True, exist_ok=True)

            saved = []
            for source in sources:
                try:
                    path = self.runner.fetch_blog(
                        url=source["url"],
                        name=source["name"],
                        output_dir=output_dir
                    )
                    if path:
                        saved.append(path)
                except Exception as e:
                    logger.error(f"Failed to fetch {source['url']}: {e}")

            if not saved:
                return {
                    "success": True,
                    "blog_count": 0,
                    "folder": str(output_dir),
                    "summary": "No new blog posts this week."
                }

            summary = self.summarizer.summarize(output_dir)

            return {
                "success": True,
                "blog_count": len(saved),
                "folder": str(output_dir),
                "summary": summary
            }

        except Exception as e:
            logger.error(f"Blog processing failed: {e}", exc_info=True)
            return {
                "success": False,
                "blog_count": 0,
                "folder": None,
                "summary": None,
                "error": str(e)
            }
