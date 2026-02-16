# ABOUTME: Executes Claude CLI to analyze newsletter emails
# ABOUTME: Loads prompt template, invokes subprocess, handles errors

import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ClaudeRunner:
    """Runs Claude CLI to analyze newsletters."""

    def __init__(self, prompt_file: str = ".claude/prompts/newsletter_analysis_prompt.md"):
        self.prompt_file = Path(prompt_file)

    def analyze_newsletters(self, folder_path: str, timeout: int = 300) -> str:
        """
        Analyze newsletters in folder using Claude.

        Args:
            folder_path: Path to folder containing .md files
            timeout: Max execution time in seconds (default 5 minutes)

        Returns:
            Claude's analysis output

        Raises:
            Exception: If Claude execution fails
        """
        # Load base prompt template
        if not self.prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {self.prompt_file}")

        base_prompt = self.prompt_file.read_text()

        # Add folder context to prompt
        full_prompt = f"{base_prompt}\n\n---\n\nAnalizuj pliki w folderze: {folder_path}/"

        logger.info(f"Running Claude analysis on {folder_path}")

        try:
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
                logger.error(f"Claude failed with exit code {result.returncode}")
                logger.error(f"stderr: {result.stderr}")
                raise Exception(f"Claude execution failed: {result.stderr}")

            logger.info("Claude analysis completed successfully")
            return result.stdout

        except subprocess.TimeoutExpired:
            logger.error(f"Claude execution timeout after {timeout}s")
            raise Exception(f"Claude execution timeout after {timeout}s")
        except FileNotFoundError:
            logger.error("Claude CLI not found - is it installed?")
            raise Exception("Claude CLI not found - ensure 'claude' is in PATH")
        except Exception as e:
            logger.error(f"Unexpected error running Claude: {e}")
            raise
