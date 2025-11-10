#!/usr/bin/env python3
"""Qwen3 tool call converter.

The Qwen3 model emits a single JSON‑encoded tool call wrapped in an
``<tool_call>`` tag.  Example:

```
<tool_call> {"name": "tool_calculate_post", "arguments": {"expression": "4 * 90"}} </tool_call>
```

This converter parses that payload and converts it to the OpenAI tool call
representation used throughout the proxy.
"""

import json
import logging
import re
from typing import Dict, Any, List

from .base import ToolCallConverter, StreamingToolCallHandler
from config import Config

logger = logging.getLogger(__name__)

class Qwen3ToolCallConverter(ToolCallConverter):
    """Convert Qwen3 tool calls to the standard OpenAI format."""

    QWEN3_MODEL_PATTERNS = [r".*qwen3.*", r".*jan[-_]nano.*"]

    def __init__(self):
        self.config = Config()

    def can_handle_model(self, model_name: str) -> bool:
        if not model_name:
            return False
        return any(re.match(p, model_name.lower()) for p in self.QWEN3_MODEL_PATTERNS)

    def parse_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        """Parse all ``<tool_call>…</tool_call>`` blocks.

        Each block is expected to contain a JSON object with a ``name`` field
        and an ``arguments`` mapping.  The JSON is parsed with ``json.loads``
        and used to build a standard OpenAI ``tool_call`` dictionary.
        """
        tool_calls: List[Dict[str, Any]] = []
        # Regex captures the JSON content inside the tags, including
        # surrounding whitespace.
        pattern = r"<tool_call>\s*(\{.*?\})\s*</tool_call>"
        for i, json_str in enumerate(re.findall(pattern, content, re.DOTALL)):
            try:
                payload = json.loads(json_str.strip())
                name = payload.get("name", "")
                args = payload.get("arguments", {})
                tool_call = {
                    "id": str(hash(f"{name}_{i}_{len(tool_calls)}") % 1000000000),
                    "type": "function",
                    "function": {
                        "name": name,
                        "arguments": json.dumps(args, ensure_ascii=False),
                    },
                }
                tool_calls.append(tool_call)
            except json.JSONDecodeError as e:
                # Invalid JSON – skip this block.
                continue
        return tool_calls

    def has_partial_tool_call(self, content: str) -> bool:
        # Look for either opening or closing tags.
        return "<tool_call>" in content or "</tool_call>" in content

    def is_complete_tool_call(self, content: str) -> bool:
        # A complete tool call contains both opening and closing tags.
        return bool(re.search(r"<tool_call>.*?</tool_call>", content, re.DOTALL))

    def _clean_content(self, content: str) -> str:
        # Remove all <tool_call>…</tool_call> blocks.
        content = re.sub(r"<tool_call>.*?</tool_call>", "", content, flags=re.DOTALL)
        # Handle <think> tags as the GLM converter does.
        if self.config.REMOVE_THINK_TAGS:
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
        else:
            logger.debug(f"Keeping complete <think>...</think> pairs (REMOVE_THINK_TAGS=false)")
        content = self._remove_orphaned_think_tags(content)
        return content.strip()

    def _remove_orphaned_think_tags(self, content: str) -> str:
        # Remove orphaned <think> tags that have no closing partner.
        result = []
        i = 0
        while i < len(content):
            if content[i:].startswith("<think>"):
                end = content.find("</think>", i + 7)
                if end == -1:
                    i += 7
                    continue
            result.append(content[i])
            i += 1
        return "".join(result)


class Qwen3StreamingHandler(StreamingToolCallHandler):
    """Streaming handler for Qwen3 tool calls."""

    def __init__(self):
        super().__init__(Qwen3ToolCallConverter())
