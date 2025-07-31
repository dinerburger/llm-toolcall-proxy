#!/usr/bin/env python3
"""
Debug the tool call converter
"""

import json
import re
from app import ToolCallConverter

def debug_conversion():
    converter = ToolCallConverter()
    
    # Test content
    content = "I'll search for information about Kyungju.\n<tool_call>fetch_wikipedia_content\n<arg_key>search_query</arg_key>\n<arg_value>Kyungju Korea</arg_value>\n</tool_call>"
    
    print("Content to parse:")
    print(repr(content))
    print("\nContent:")
    print(content)
    
    # Test parsing
    print("\n=== Testing parse_glm_tool_calls ===")
    tool_calls = converter.parse_glm_tool_calls(content)
    print(f"Found {len(tool_calls)} tool calls:")
    for tc in tool_calls:
        print(json.dumps(tc, indent=2))
    
    # Test with the pattern directly
    print("\n=== Testing regex pattern directly ===")
    pattern = r'<tool_call>(.*?)<arg_key>(.*?)</arg_key><arg_value>(.*?)</arg_value></tool_call>'
    matches = re.findall(pattern, content, re.DOTALL)
    print(f"Regex found {len(matches)} matches:")
    for match in matches:
        print(f"Function: '{match[0].strip()}'")
        print(f"Key: '{match[1].strip()}'") 
        print(f"Value: '{match[2].strip()}'")
    
    # Test response conversion
    print("\n=== Testing convert_response ===")
    test_response = {
        "choices": [{
            "message": {
                "content": content
            },
            "finish_reason": "stop"
        }]
    }
    
    converted = converter.convert_response(test_response)
    print("Converted response:")
    print(json.dumps(converted, indent=2))

if __name__ == '__main__':
    debug_conversion()