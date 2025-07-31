#!/usr/bin/env python3
"""
Simple test to verify the proxy server works
"""

import json
import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

from app import ToolCallConverter

def test_converter():
    """Test the converter directly"""
    print("=== Testing ToolCallConverter ===")
    
    converter = ToolCallConverter()
    
    # Test GLM response
    glm_response = {
        "id": "test-123",
        "object": "chat.completion",
        "created": 1753923395,
        "model": "glm-4.5-air-hi-mlx@4bit",
        "choices": [
            {
                "index": 0,
                "logprobs": None,
                "finish_reason": "stop",
                "message": {
                    "role": "assistant",
                    "content": "I'll help you with that.\n<tool_call>fetch_wikipedia_content\n<arg_key>search_query</arg_key>\n<arg_value>Kyungju Korea</arg_value>\n</tool_call>"
                }
            }
        ],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 30,
            "total_tokens": 80
        }
    }
    
    print("Original GLM response:")
    print(json.dumps(glm_response, indent=2))
    
    # Convert
    converted = converter.convert_response(glm_response)
    
    print("\nConverted response:")
    print(json.dumps(converted, indent=2))
    
    # Verify
    message = converted['choices'][0]['message']
    if 'tool_calls' in message and len(message['tool_calls']) > 0:
        print("\n✅ SUCCESS: Tool call conversion working!")
        tool_call = message['tool_calls'][0]
        print(f"   Function: {tool_call['function']['name']}")
        print(f"   Arguments: {tool_call['function']['arguments']}")
        print(f"   Finish reason: {converted['choices'][0]['finish_reason']}")
        print(f"   Clean content: '{message['content']}'")
        return True
    else:
        print("\n❌ FAILED: Tool call not converted")
        return False

def test_standard_response():
    """Test that standard responses are left unchanged"""
    print("\n=== Testing Standard Response (No Conversion) ===")
    
    converter = ToolCallConverter()
    
    standard_response = {
        "id": "test-456",
        "object": "chat.completion",
        "created": 1753923304,
        "model": "qwen3-235b-a22b-instruct-2507-dwq",
        "choices": [
            {
                "index": 0,
                "logprobs": None,
                "finish_reason": "tool_calls",
                "message": {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": "693664129",
                            "type": "function",
                            "function": {
                                "name": "fetch_wikipedia_content",
                                "arguments": "{\"search_query\": \"River Crossing Kyoungju\"}"
                            }
                        }
                    ]
                }
            }
        ]
    }
    
    print("Original standard response:")
    print(json.dumps(standard_response, indent=2))
    
    converted = converter.convert_response(standard_response)
    
    print("\nAfter 'conversion' (should be unchanged):")
    print(json.dumps(converted, indent=2))
    
    if converted == standard_response:
        print("\n✅ SUCCESS: Standard response left unchanged")
        return True
    else:
        print("\n❌ FAILED: Standard response was modified")
        return False

if __name__ == '__main__':
    print("Flask Proxy Server - Tool Call Converter Test")
    print("=" * 50)
    
    success1 = test_converter()
    success2 = test_standard_response()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"GLM Conversion Test: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"Standard Response Test: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! The converter is working correctly.")
        print("\nTo test the full proxy server:")
        print("1. Run: python app.py")
        print("2. Send requests to http://localhost:5000/chat/completions")
        print("3. Backend should be running on http://localhost:8888")
    else:
        print("\n❌ Some tests failed. Check the converter implementation.")