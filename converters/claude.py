#!/usr/bin/env python3
"""
Claude model specific tool call converter (example implementation)
"""

import json
import re
from typing import Dict, Any, List
from .base import ToolCallConverter, StreamingToolCallHandler


class ClaudeToolCallConverter(ToolCallConverter):
    """Converter for Claude models with custom tool call formats"""
    
    # Claude model patterns
    CLAUDE_MODEL_PATTERNS = [
        r'claude-.*',
        r'anthropic/claude-.*',
        r'.*claude.*'
    ]
    
    def can_handle_model(self, model_name: str) -> bool:
        """Check if this converter can handle Claude models"""
        if not model_name:
            return False
            
        model_lower = model_name.lower()
        for pattern in self.CLAUDE_MODEL_PATTERNS:
            if re.match(pattern, model_lower):
                return True
        return False
    
    def parse_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        """Parse Claude format tool calls from content
        
        Note: This is a placeholder implementation.
        Claude actually uses standard OpenAI format, but this shows
        how to add support for models with custom formats.
        """
        tool_calls = []
        
        # Example: Claude might use a different format like:
        # <invoke name="function_name">
        # <parameter name="param">value</parameter>
        # </invoke>
        
        pattern = r'<invoke name="([^"]+)">\s*<parameter name="([^"]+)">([^<]+)</parameter>\s*</invoke>'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for i, (function_name, param_name, param_value) in enumerate(matches):
            tool_call = {
                "id": str(hash(f"{function_name}_{i}") % 1000000000),
                "type": "function",
                "function": {
                    "name": function_name.strip(),
                    "arguments": json.dumps({param_name.strip(): param_value.strip()})
                }
            }
            tool_calls.append(tool_call)
        
        return tool_calls
    
    def has_partial_tool_call(self, content: str) -> bool:
        """Check if content contains partial Claude tool call markup"""
        claude_markers = ['<invoke', '</invoke>', '<parameter', '</parameter>']
        return any(marker in content for marker in claude_markers)
    
    def is_complete_tool_call(self, content: str) -> bool:
        """Check if content contains complete Claude tool call markup"""
        return bool(re.search(r'<invoke name="[^"]+">.*?</invoke>', content, re.DOTALL))
    
    def _clean_content(self, content: str) -> str:
        """Remove Claude tool call markup from content"""
        return re.sub(r'<invoke name="[^"]+">.*?</invoke>', '', content, flags=re.DOTALL).strip()


class ClaudeStreamingHandler(StreamingToolCallHandler):
    """Claude-specific streaming tool call handler"""
    
    def __init__(self):
        super().__init__(ClaudeToolCallConverter())