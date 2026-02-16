# ABOUTME: Unit tests for Claude subprocess execution
# ABOUTME: Tests prompt loading, subprocess invocation, and error handling

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.newsletter.claude_runner import ClaudeRunner


class TestClaudeRunner:
    @patch('src.newsletter.claude_runner.subprocess.run')
    @patch('src.newsletter.claude_runner.Path')
    def test_analyze_newsletters_success(self, mock_path, mock_subprocess):
        """Test successful newsletter analysis."""
        # Mock prompt file reading
        mock_prompt_file = MagicMock()
        mock_prompt_file.read_text.return_value = "Base prompt template"
        mock_path.return_value = mock_prompt_file

        # Mock subprocess success
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Analysis complete"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        runner = ClaudeRunner()
        result = runner.analyze_newsletters("newsletters/07_2026")

        assert result == "Analysis complete"
        mock_subprocess.assert_called_once()

        # Verify claude command structure
        call_args = mock_subprocess.call_args
        assert call_args[0][0][0] == "claude"
        assert call_args[0][0][1] == "-p"
        assert "newsletters/07_2026" in call_args[0][0][2]

    @patch('src.newsletter.claude_runner.subprocess.run')
    def test_analyze_newsletters_timeout(self, mock_subprocess):
        """Test timeout handling."""
        mock_subprocess.side_effect = TimeoutError("Process timeout")

        runner = ClaudeRunner()

        with pytest.raises(Exception) as exc_info:
            runner.analyze_newsletters("newsletters/07_2026")

        assert "timeout" in str(exc_info.value).lower()
