# ABOUTME: Runs Claude CLI per blog URL to fetch and summarize recent posts
# ABOUTME: Returns None when no new content, saves markdown file when content found

import subprocess
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

NO_NEW_CONTENT_MARKER = "NO_NEW_CONTENT"


class BlogRunner:
    """Fetches and summarizes a single blog using Claude with WebFetch."""

    def __init__(self, prompt_file: str = ".claude/prompts/blog_fetch_prompt.md"):
        self.prompt_file = Path(prompt_file)

    def fetch_blog(self, url: str, name: str, output_dir: Path, timeout: int = 300) -> Path | None:
        """
        Fetch recent posts from a blog using Claude.

        Args:
            url: Blog URL to fetch
            name: Human-readable blog name
            output_dir: Directory to save result markdown
            timeout: Max execution time in seconds

        Returns:
            Path to saved markdown file, or None if no new content
        """
        if not self.prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {self.prompt_file}")

        base_prompt = self.prompt_file.read_text()
        full_prompt = (
            f"{base_prompt}\n\n---\n\n"
            f"Blog do sprawdzenia:\n"
            f"- NAME: {name}\n"
            f"- URL: {url}"
        )

        logger.info(f"Fetching blog: {name} ({url})")

        result = subprocess.run(
            [
                "claude", "-p", full_prompt,
                "--allowedTools", "WebFetch,WebSearch,Read,Write",
                "--output-format", "text"
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(Path.cwd())
        )

        if result.returncode != 0:
            logger.error(f"Claude failed for {url}: {result.stderr}")
            raise Exception(f"Claude execution failed: {result.stderr}")

        output = result.stdout.strip()

        if NO_NEW_CONTENT_MARKER in output:
            logger.info(f"No new content for {name}")
            return None

        filename = _url_to_filename(url)
        file_path = output_dir / filename
        file_path.write_text(output, encoding="utf-8")
        logger.info(f"Saved blog summary: {file_path}")

        return file_path


def _url_to_filename(url: str) -> str:
    """Convert blog URL to safe filename."""
    domain = re.sub(r"https?://", "", url)
    domain = re.sub(r"[^\w.]", "_", domain)
    domain = re.sub(r"_+", "_", domain).strip("_")
    return f"{domain}.md"
