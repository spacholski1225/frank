"""Fetch recent blog content with Codex live web search."""
import re
from datetime import date
from pathlib import Path
from src.executor import PROJECT_ROOT, execute_codex

NO_NEW_CONTENT_MARKER = "NO_NEW_CONTENT"


class BlogRunner:
    def __init__(self, prompt_file: str | Path | None = None):
        self.prompt_file = Path(prompt_file) if prompt_file else PROJECT_ROOT / "prompts/blog_fetch_prompt.md"

    def fetch_blog(self, url: str, name: str, output_dir: Path,
                   timeout: int | None = None) -> Path | None:
        prompt = self.prompt_file.read_text(encoding="utf-8")
        prompt = prompt.replace("[WSTAW_DZISIEJSZĄ_DATĘ]", date.today().isoformat())
        prompt += f"\n\nBlog do sprawdzenia:\n- NAME: {name}\n- URL: {url}"
        output, _ = execute_codex(prompt, timeout=timeout, web_search=True)
        if output == NO_NEW_CONTENT_MARKER:
            return None
        if output == "FETCH_ERROR":
            raise RuntimeError(f"Cannot fetch blog: {url}")
        output_dir.mkdir(parents=True, exist_ok=True)
        file_path = output_dir / _url_to_filename(url)
        file_path.write_text(output, encoding="utf-8")
        return file_path


def _url_to_filename(url: str) -> str:
    domain = re.sub(r"https?://", "", url)
    domain = re.sub(r"[^\w.]", "_", domain)
    domain = re.sub(r"_+", "_", domain).strip("_")
    return f"{domain}.md"
