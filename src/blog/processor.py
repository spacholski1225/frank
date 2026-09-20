# ABOUTME: Orchestrates blog scraping pipeline
# ABOUTME: Loads sources, runs per-blog fetch, summarizes results, returns digest

import json
import logging
import tempfile
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
            errors = []
            run_dir = Path(tempfile.mkdtemp(prefix="run-", dir=output_dir))
            for source in sources:
                try:
                    path = self.runner.fetch_blog(
                        url=source["url"],
                        name=source["name"],
                        output_dir=run_dir
                    )
                    if path:
                        saved.append(path)
                except Exception as e:
                    logger.error(f"Failed to fetch {source['url']}: {e}")
                    errors.append(source["url"])

            if not saved and errors:
                raise RuntimeError("Blog fetching failed: " + ", ".join(errors))

            if not saved:
                return {
                    "success": True,
                    "blog_count": 0,
                    "folder": str(output_dir),
                    "summary": "No new blog posts this week."
                }

            summary = self.summarizer.summarize(run_dir)
            if errors:
                summary += "\n\n⚠️ Nie udało się odczytać źródeł: " + ", ".join(errors)
            (run_dir / "summary.md").write_text(summary, encoding="utf-8")
            (output_dir / "summary.md").write_text(summary, encoding="utf-8")

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
