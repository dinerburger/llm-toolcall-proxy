#!/usr/bin/env python3
"""
GLM model specific tool call converter
"""

import json
import re
from typing import Dict, Any, List
from .base import ToolCallConverter, StreamingToolCallHandler


class GLMToolCallConverter(ToolCallConverter):
    """Converts GLM tool call format to standard OpenAI format"""
    
    # GLM model patterns
    GLM_MODEL_PATTERNS = [
        r'glm-.*',
        r'chatglm-.*', 
        r'.*glm.*'
    ]
    
    def can_handle_model(self, model_name: str) -> bool:
        """Check if this converter can handle GLM models"""
        if not model_name:
            return False
            
        model_lower = model_name.lower()
        for pattern in self.GLM_MODEL_PATTERNS:
            if re.match(pattern, model_lower):
                return True
        return False
    
    def parse_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        """Parse GLM format tool calls from content"""
        tool_calls = []
        
        # Pattern to match GLM tool call format (multiline with whitespace)
        pattern = r'<tool_call>\s*(.*?)\s*<arg_key>\s*(.*?)\s*</arg_key>\s*<arg_value>\s*(.*?)\s*</arg_value>\s*</tool_call>'
        matches = re.findall(pattern, content, re.DOTALL)
        
        for i, (function_name, arg_key, arg_value) in enumerate(matches):
            tool_call = {
                "id": str(hash(f"{function_name}_{i}") % 1000000000),
                "type": "function",
                "function": {
                    "name": function_name.strip(),
                    "arguments": json.dumps({arg_key.strip(): arg_value.strip()})
                }
            }
            tool_calls.append(tool_call)
        
        return tool_calls
    
    def has_partial_tool_call(self, content: str) -> bool:
        """Check if content contains partial GLM tool call markup"""
        glm_markers = ['<tool_call>', '</tool_call>', '<arg_key>', '</arg_key>', '<arg_value>', '</arg_value>']
        return any(marker in content for marker in glm_markers)
    
    def is_complete_tool_call(self, content: str) -> bool:
        """Check if content contains complete GLM tool call markup"""
        return bool(re.search(r'<tool_call>.*?</tool_call>', content, re.DOTALL))
    
    def _clean_content(self, content: str) -> str:
        """Remove GLM tool call markup from content"""
        return re.sub(r'<tool_call>.*?</tool_call>', '', content, flags=re.DOTALL).strip()


class GLMStreamingHandler(StreamingToolCallHandler):
    """GLM-specific streaming tool call handler"""
    
    def __init__(self):
        super().__init__(GLMToolCallConverter())