#!/usr/bin/env python3
"""Qwen3 Coder specific tool call converter.

This module mirrors the structure of :pymod:`converters.glm` but
parses the legacy XML‑style format used by the Qwen3 Coder model:

```
<tool_call>
  <function=search_products>
    <parameter=query>
      waterproof running shoes
    </parameter>
    <parameter=sort_by>
      price_low_to_high
    </parameter>
  </function>
</tool_call>
```

The converter transforms the above into an OpenAI‑compatible tool call.
"""

import json
import re
from typing import Dict, Any, List

from .base import ToolCallConverter, StreamingToolCallHandler
from config import Config


class Qwen3CoderToolCallConverter(ToolCallConverter):
    """Convert Qwen3 Coder tool calls to the standard OpenAI format."""

    QWEN3_MODEL_PATTERNS = [r".*qwen3[-_]coder.*"]

    def __init__(self):
        self.config = Config()

    def can_handle_model(self, model_name: str) -> bool:
        if not model_name:
            return False
        return any(re.match(p, model_name.lower()) for p in self.QWEN3_MODEL_PATTERNS)

    def parse_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        tool_calls: List[Dict[str, Any]] = []
        # Find all <tool_call>...</tool_call> blocks.
        for i, block in enumerate(re.findall(r"<tool_call>(.*?)</tool_call>", content, re.DOTALL)):
            # Extract function name and inner content.
            func_match = re.search(r"<function=([^>]+)>(.*?)</function>", block, re.DOTALL)
            if not func_match:
                continue
            function_name, inner = func_match.groups()
            function_name = function_name.strip()
            parameters: Dict[str, Any] = {}
            # Extract <parameter=key>value</parameter> pairs.
            for key, val in re.findall(r"<parameter=([^>]+)>(.*?)</parameter>", inner, re.DOTALL):
                key = key.strip()
                value = val.strip()
                try:
                    parsed = json.loads(value)
                except json.JSONDecodeError:
                    parsed = value
                parameters[key] = parsed
            # Build OpenAI tool call structure.
            tool_call = {
                "id": str(hash(f"{function_name}_{i}_{len(tool_calls)}") % 1000000000),
                "type": "function",
                "function": {
                    "name": function_name,
                    "arguments": json.dumps(parameters, ensure_ascii=False),
                },
            }
            tool_calls.append(tool_call)
        return tool_calls

    def has_partial_tool_call(self, content: str) -> bool:
        markers = ["<tool_call>", "</tool_call>", "<function=", "</function>", "<parameter=", "</parameter>"]
        return any(m in content for m in markers)

    def is_complete_tool_call(self, content: str) -> bool:
        return bool(re.search(r"<tool_call>.*?</tool_call>", content, re.DOTALL))

    def _clean_content(self, content: str) -> str:
        # Remove all <tool_call> blocks.
        content = re.sub(r"<tool_call>.*?</tool_call>", "", content, flags=re.DOTALL)
        # Remove orphaned tags.
        content = re.sub(r"</function>", "", content)
        content = re.sub(r"</parameter>", "", content)
        if self.config.REMOVE_THINK_TAGS:
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
        content = self._remove_orphaned_think_tags(content)
        return content.strip()

    def _remove_orphaned_think_tags(self, content: str) -> str:
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


class Qwen3CoderStreamingHandler(StreamingToolCallHandler):
    """Streaming handler for Qwen3 Coder tool calls."""

    def __init__(self):
        super().__init__(Qwen3CoderToolCallConverter())
