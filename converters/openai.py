#!/usr/bin/env python3
"""
OpenAI/GPT model specific tool call converter
OpenAI models already use standard format, so this is mostly pass-through
"""

import json
import re
from typing import Dict, Any, List
from .base import ToolCallConverter, StreamingToolCallHandler


class OpenAIToolCallConverter(ToolCallConverter):
    """Converter for OpenAI/GPT models (standard format)"""
    
    # OpenAI/GPT model patterns
    OPENAI_MODEL_PATTERNS = [
        r'gpt-.*',
        r'openai/gpt-.*',
        r'text-davinci-.*',
        r'code-davinci-.*'
    ]
    
    def can_handle_model(self, model_name: str) -> bool:
        """Check if this converter can handle OpenAI models"""
        if not model_name:
            return False
            
        model_lower = model_name.lower()
        for pattern in self.OPENAI_MODEL_PATTERNS:
            if re.match(pattern, model_lower):
                return True
        return False
    
    def parse_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        """OpenAI models already use standard format, so no parsing needed"""
        return []  # No conversion needed
    
    def has_partial_tool_call(self, content: str) -> bool:
        """OpenAI models don't use custom markup in content"""
        return False
    
    def is_complete_tool_call(self, content: str) -> bool:
        """OpenAI models don't use custom markup in content"""
        return False
    
    def _clean_content(self, content: str) -> str:
        """No cleaning needed for OpenAI format"""
        return content
    
    def convert_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """OpenAI responses are already in correct format"""
        return response_data  # Pass through without modification


class OpenAIStreamingHandler(StreamingToolCallHandler):
    """OpenAI-specific streaming tool call handler (pass-through)"""
    
    def __init__(self):
        super().__init__(OpenAIToolCallConverter())
    
    def process_chunk(self, chunk_data: Dict[str, Any]) -> Dict[str, Any]:
        """Pass through OpenAI chunks without modification"""
        return chunk_data  # No conversion needed