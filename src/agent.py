"""Frank Agent - Claude Agent SDK wrapper."""
from claude_agent_sdk import query, ClaudeAgentOptions
from typing import AsyncGenerator, Optional
from pathlib import Path


class FrankAgent:
    """Main agent class wrapping Claude Agent SDK."""

    def __init__(self, food_tool, system_prompt_path: str):
        """Initialize Frank Agent.

        Args:
            food_tool: FoodTool instance
            system_prompt_path: Path to system_prompt.md
        """
        self.food_tool = food_tool
        self.system_prompt = self._load_system_prompt(system_prompt_path)
        self.sessions: dict[str, dict] = {}

    def _load_system_prompt(self, path: str) -> str:
        """Load system prompt from markdown file.

        Args:
            path: Path to system_prompt.md

        Returns:
            System prompt content
        """
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    async def chat(
        self,
        user_message: str,
        session_id: Optional[str] = None
    ) -> AsyncGenerator[dict, None]:
        """Chat with Frank using Claude Agent SDK.

        Args:
            user_message: User's message
            session_id: Optional session ID for continuity

        Yields:
            Dict with message type, content, and session_id
        """
        # Configure Agent SDK options
        options = ClaudeAgentOptions(
            allowed_tools=["Read", "Write"],
            system_prompt=self.system_prompt,
            resume=session_id,
            model="claude-3-5-sonnet-20241022",
            permission_mode="bypassPermissions"  # Auto-execute tools
        )

        current_session_id = session_id

        # Stream messages from Agent SDK
        async for message in query(
            prompt=user_message,
            options=options
        ):
            # Capture session ID on init
            if hasattr(message, 'subtype') and message.subtype == 'init':
                current_session_id = message.session_id
                self.sessions[current_session_id] = {
                    "created_at": message.timestamp if hasattr(message, 'timestamp') else None
                }

            # Yield formatted message
            yield {
                "type": message.type,
                "content": getattr(message, 'result', None) or getattr(message, 'text', str(message)),
                "session_id": current_session_id
            }
