#!/usr/bin/env python3
"""
GLM model specific tool call converter
"""

import json
import re
from typing import Dict, Any, List
from .base import ToolCallConverter, StreamingToolCallHandler
from config import Config


class GLMToolCallConverter(ToolCallConverter):
    """Converts GLM tool call format to standard OpenAI format"""
    
    # GLM model patterns
    GLM_MODEL_PATTERNS = [
        r'glm-.*',
        r'chatglm-.*', 
        r'.*glm.*'
    ]
    
    def __init__(self):
        """Initialize GLM converter with config"""
        self.config = Config()
    
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
        
        print(f"[DEBUG] GLM Tool Call Parser - Input content:")
        print(f"[DEBUG] {repr(content)}")
        print(f"[DEBUG] Content preview: {content[:200]}...")
        
        # Method 1: Parse new [TOOL_REQUEST] format
        tool_request_pattern = r'\[TOOL_REQUEST\]\s*(\{.*?\})\s*\[END_TOOL_REQUEST\]'
        tool_request_matches = re.findall(tool_request_pattern, content, re.DOTALL)
        
        print(f"[DEBUG] TOOL_REQUEST matches found: {len(tool_request_matches)}")
        
        for i, json_str in enumerate(tool_request_matches):
            try:
                print(f"[DEBUG] Parsing TOOL_REQUEST {i}: {repr(json_str)}")
                tool_data = json.loads(json_str.strip())
                
                tool_call = {
                    "id": str(hash(f"{tool_data.get('name', 'unknown')}_{i}") % 1000000000),
                    "type": "function",
                    "function": {
                        "name": tool_data.get("name", ""),
                        "arguments": json.dumps(tool_data.get("arguments", {}), ensure_ascii=False)
                    }
                }
                tool_calls.append(tool_call)
                print(f"[DEBUG] Successfully parsed TOOL_REQUEST: {tool_call}")
                
            except json.JSONDecodeError as e:
                print(f"[DEBUG] Failed to parse TOOL_REQUEST JSON: {e}")
                print(f"[DEBUG] Invalid JSON: {repr(json_str)}")
        
        # Method 2: Parse legacy <tool_call> format - handle both single and multi parameters
        legacy_pattern = r'<tool_call>\s*(.*?)\s*((?:<arg_key>.*?</arg_key>\s*<arg_value>.*?</arg_value>\s*)+)\s*</tool_call>'
        legacy_matches = re.findall(legacy_pattern, content, re.DOTALL)
        
        print(f"[DEBUG] Legacy format matches found: {len(legacy_matches)}")
        
        for i, (function_name, args_section) in enumerate(legacy_matches):
            # Parse all arg_key/arg_value pairs  
            arg_pattern = r'<arg_key>\s*(.*?)\s*</arg_key>\s*<arg_value>\s*(.*?)\s*</arg_value>'
            arg_matches = re.findall(arg_pattern, args_section, re.DOTALL)
            
            print(f"[DEBUG] Found {len(arg_matches)} argument pairs for function {function_name.strip()}")
            
            arguments = {}
            for arg_key, arg_value in arg_matches:
                arguments[arg_key.strip()] = arg_value.strip()
                print(f"[DEBUG] Argument: {arg_key.strip()} = {arg_value.strip()}")
            
            tool_call = {
                "id": str(hash(f"{function_name}_{i}_{len(tool_calls)}") % 1000000000),
                "type": "function",
                "function": {
                    "name": function_name.strip(),
                    "arguments": json.dumps(arguments, ensure_ascii=False)
                }
            }
            tool_calls.append(tool_call)
            print(f"[DEBUG] Successfully parsed legacy format: {tool_call}")
        
        print(f"[DEBUG] Total tool calls parsed: {len(tool_calls)}")
        return tool_calls
    
    def has_partial_tool_call(self, content: str) -> bool:
        """Check if content contains partial GLM tool call markup"""
        # Check for legacy format markers
        legacy_markers = ['<tool_call>', '</tool_call>', '<arg_key>', '</arg_key>', '<arg_value>', '</arg_value>']
        # Check for new format markers
        new_markers = ['[TOOL_REQUEST]', '[END_TOOL_REQUEST]']
        
        return any(marker in content for marker in legacy_markers + new_markers)
    
    def is_complete_tool_call(self, content: str) -> bool:
        """Check if content contains complete GLM tool call markup"""
        # Check for complete legacy format
        legacy_complete = bool(re.search(r'<tool_call>.*?</tool_call>', content, re.DOTALL))
        # Check for complete new format
        new_complete = bool(re.search(r'\[TOOL_REQUEST\].*?\[END_TOOL_REQUEST\]', content, re.DOTALL))
        
        return legacy_complete or new_complete
    
    def _clean_content(self, content: str) -> str:
        """Remove GLM tool call markup and malformed think tags from content"""
        # Remove legacy format
        content = re.sub(r'<tool_call>.*?</tool_call>', '', content, flags=re.DOTALL)
        # Remove new format
        content = re.sub(r'\[TOOL_REQUEST\].*?\[END_TOOL_REQUEST\]', '', content, flags=re.DOTALL)
        
        # Remove complete <think>...</think> pairs based on config setting
        if self.config.REMOVE_THINK_TAGS:
            print(f"[DEBUG] Removing complete <think>...</think> pairs (REMOVE_THINK_TAGS=true)")
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        else:
            print(f"[DEBUG] Keeping complete <think>...</think> pairs (REMOVE_THINK_TAGS=false)")
        
        # Always remove orphaned </think> tags (closing tags without opening tags)
        orphaned_closing_count = len(re.findall(r'</think>', content))
        if orphaned_closing_count > 0:
            print(f"[DEBUG] Removing {orphaned_closing_count} orphaned </think> tags")
            content = re.sub(r'</think>', '', content)
        
        # Always remove orphaned <think> tags (opening tags without closing tags) 
        content = self._remove_orphaned_think_tags(content)
        
        return content.strip()
    
    def _remove_orphaned_think_tags(self, content: str) -> str:
        """Remove orphaned <think> tags that don't have matching </think> tags"""
        # This handles cases where <think> is opened but never closed
        result = []
        i = 0
        while i < len(content):
            if content[i:].startswith('<think>'):
                # Found opening tag, look for closing tag
                remaining = content[i+7:]  # Skip '<think>'
                if '</think>' not in remaining:
                    # No closing tag found, skip this opening tag
                    print(f"[DEBUG] Removing orphaned <think> tag at position {i}")
                    i += 7  # Skip '<think>'
                    continue
            result.append(content[i])
            i += 1
        return ''.join(result)


class GLMStreamingHandler(StreamingToolCallHandler):
    """GLM-specific streaming tool call handler"""
    
    def __init__(self):
        super().__init__(GLMToolCallConverter())