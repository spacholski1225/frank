"""Summarize collected blog posts with Codex and persist the final report."""
from pathlib import Path
from src.executor import PROJECT_ROOT, execute_codex


class BlogSummarizer:
    def __init__(self, prompt_file: str | Path | None = None):
        self.prompt_file = Path(prompt_file) if prompt_file else PROJECT_ROOT / "prompts/blog_summary_prompt.md"

    def summarize(self, folder: Path, timeout: int | None = None) -> str:
        folder = folder.resolve()
        if not any(f.name != "summary.md" for f in folder.glob("*.md")):
            raise ValueError(f"No blog summaries found in {folder}")
        prompt = self.prompt_file.read_text(encoding="utf-8")
        prompt += f"\n\nAnalizuj wpisy w folderze: {folder}/. Pomiń summary.md."
        summary, _ = execute_codex(prompt, timeout=timeout)
        (folder / "summary.md").write_text(summary, encoding="utf-8")
        return summary
