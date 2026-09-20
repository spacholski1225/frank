"""Analyze saved newsletter emails with Codex and persist the report."""
from pathlib import Path
from src.executor import PROJECT_ROOT, execute_codex


class CodexRunner:
    def __init__(self, prompt_file: str | Path | None = None):
        self.prompt_file = Path(prompt_file) if prompt_file else PROJECT_ROOT / "prompts/newsletter_analysis_prompt.md"

    def analyze_newsletters(self, folder_path: str, timeout: int | None = None) -> str:
        folder = Path(folder_path).resolve()
        if not any(f.name != "summary.md" for f in folder.glob("*.md")):
            raise ValueError("No newsletter files found")
        prompt = self.prompt_file.read_text(encoding="utf-8")
        prompt += f"\n\nAnalizuj wyłącznie maile w folderze: {folder}/. Pomiń summary.md."
        summary, _ = execute_codex(prompt, timeout=timeout)
        (folder / "summary.md").write_text(summary, encoding="utf-8")
        return summary
