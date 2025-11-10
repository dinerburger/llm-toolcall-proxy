#!/usr/bin/env python3
"""Devstral tool call converter.

The Devstral model emits tool calls in a custom markup format:

```
[TOOL_CALLS]COMMAND_NAME[ARGS]A_VALID_JSONOBJECT
```

Where ``COMMAND_NAME`` is a plain string and the JSON object contains
arguments for that command.  The converter extracts these calls and
transforms them into the OpenAI/ChatCompletions ``function`` format.

Only the core parsing logic is required for the tests – we keep the
implementation lightweight and similar in style to :mod:`qwen3_coder`.
"""

import json
import logging
import re
from typing import Dict, Any, List

from .base import ToolCallConverter, StreamingToolCallHandler
from config import Config

logger = logging.getLogger(__name__)


class DevstralToolCallConverter(ToolCallConverter):
    """Convert Devstral's custom tool call syntax to the standard format.

    The model's pattern is simple: a single marker ``[TOOL_CALLS]`` followed by
    the command name, then ``[ARGS]`` and a JSON payload.
    """

    # Simple model pattern for Devstral.  The factory will use it.
    DEVSTRAL_MODEL_PATTERNS = [r".*devstral.*", r".*devstral.*"]

    def __init__(self):
        self.config = Config()

    # ------------------------------------------------------------------
    # ToolCallConverter API
    # ------------------------------------------------------------------
    def can_handle_model(self, model_name: str) -> bool:
        if not model_name:
            return False
        return any(re.match(p, model_name.lower()) for p in self.DEVSTRAL_MODEL_PATTERNS)

    def parse_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        logger.debug("DEVSTRAL PARSING: %s", content)
        tool_calls: List[Dict[str, Any]] = []
        # Match each [TOOL_CALLS]... block.  Non-greedy until next marker or EOS.
        pattern = r"\[TOOL_CALLS\](.*?)\[ARGS\](.*?)(?=\[TOOL_CALLS\]|$)"
        for match in re.finditer(pattern, content, flags=re.DOTALL):
            command_name, json_part = match.groups()
            command_name = command_name.strip()
            json_part = json_part.strip()
            try:
                args = json.loads(json_part)
            except json.JSONDecodeError:
                args = json_part
            # Build standard OpenAI tool call structure
            tool_call = {
                "id": str(hash(f"{command_name}_{len(tool_calls)}") % 1_000_000_000),
                "type": "function",
                "function": {
                    "name": command_name,
                    "arguments": json.dumps(args, ensure_ascii=False),
                },
            }
            tool_calls.append(tool_call)
        return tool_calls

    def has_partial_tool_call(self, content: str) -> bool:
        # Consider partial if the start marker exists but the full pattern may not.
        return "[TOOL_CALLS]" in content

    def is_complete_tool_call(self, content: str) -> bool:
        pattern = r"\[TOOL_CALLS\](.*?)\[ARGS\](.*?)(?=\[TOOL_CALLS\]|$)"
        return bool(re.search(pattern, content, flags=re.DOTALL))

    def _clean_content(self, content: str) -> str:
        # Remove all [TOOL_CALLS] blocks.
        pattern = r"\[TOOL_CALLS\](.*?)\[ARGS\](.*?)(?=\[TOOL_CALLS\]|$)"
        content = re.sub(pattern, "", content, flags=re.DOTALL)
        # If config removes think tags, strip them.
        if self.config.REMOVE_THINK_TAGS:
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
        return content.strip()


class DevstralStreamingHandler(StreamingToolCallHandler):
    """Streaming handler for Devstral tool calls."""

    def __init__(self):
        super().__init__(DevstralToolCallConverter())
