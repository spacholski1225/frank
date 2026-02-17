# ABOUTME: Runs Claude CLI to summarize all blog posts collected in a folder
# ABOUTME: Analogous to newsletter ClaudeRunner but for tech blogs

import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class BlogSummarizer:
    """Summarizes all per-blog markdown files in a folder using Claude."""

    def __init__(self, prompt_file: str = ".claude/prompts/blog_summary_prompt.md"):
        self.prompt_file = Path(prompt_file)

    def summarize(self, folder: Path, timeout: int = 300) -> str:
        """
        Analyze all blog markdown files in folder and produce a summary.

        Args:
            folder: Path containing per-blog .md files
            timeout: Max execution time in seconds

        Returns:
            Summary text

        Raises:
            ValueError: If folder has no blog markdown files
            Exception: If Claude execution fails
        """
        md_files = [f for f in folder.glob("*.md") if f.name != "summary.md"]
        if not md_files:
            raise ValueError(f"No blog summaries found in {folder}")

        if not self.prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {self.prompt_file}")

        base_prompt = self.prompt_file.read_text()
        full_prompt = f"{base_prompt}\n\n---\n\nAnalizuj pliki w folderze: {folder}/"

        logger.info(f"Running blog summary on {folder} ({len(md_files)} files)")

        result = subprocess.run(
            [
                "claude", "-p", full_prompt,
                "--allowedTools", "Read,Glob,Write",
                "--output-format", "text"
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(Path.cwd())
        )

        if result.returncode != 0:
            logger.error(f"Claude summarizer failed: {result.stderr}")
            raise Exception(f"Claude execution failed: {result.stderr}")

        summary_path = folder / "summary.md"
        if summary_path.exists():
            return summary_path.read_text(encoding="utf-8")

        return result.stdout
