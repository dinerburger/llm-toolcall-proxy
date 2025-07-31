#!/usr/bin/env python3
"""
Test script for the proxy server
Tests tool call conversion and API forwarding
"""

import json
import requests
import unittest
from unittest.mock import patch, Mock
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import ToolCallConverter, ProxyHandler

class TestToolCallConverter(unittest.TestCase):
    """Test the ToolCallConverter class"""
    
    def setUp(self):
        self.converter = ToolCallConverter()
    
    def test_parse_glm_tool_calls_single(self):
        """Test parsing single GLM tool call"""
        content = """
I'll fetch information about Kyungju city.
<tool_call>fetch_wikipedia_content
<arg_key>search_query</arg_key>
<arg_value>Kyungju Korea</arg_value>
</tool_call>
"""
        
        tool_calls = self.converter.parse_glm_tool_calls(content)
        
        self.assertEqual(len(tool_calls), 1)
        self.assertEqual(tool_calls[0]['type'], 'function')
        self.assertEqual(tool_calls[0]['function']['name'], 'fetch_wikipedia_content')
        
        args = json.loads(tool_calls[0]['function']['arguments'])
        self.assertEqual(args['search_query'], 'Kyungju Korea')
    
    def test_parse_glm_tool_calls_multiple(self):
        """Test parsing multiple GLM tool calls"""
        content = """
<tool_call>function1
<arg_key>param1</arg_key>
<arg_value>value1</arg_value>
</tool_call>

<tool_call>function2
<arg_key>param2</arg_key>
<arg_value>value2</arg_value>
</tool_call>
"""
        
        tool_calls = self.converter.parse_glm_tool_calls(content)
        
        self.assertEqual(len(tool_calls), 2)
        self.assertEqual(tool_calls[0]['function']['name'], 'function1')
        self.assertEqual(tool_calls[1]['function']['name'], 'function2')
    
    def test_convert_response_glm_format(self):
        """Test converting GLM format response to standard format"""
        glm_response = {
            "id": "chatcmpl-2a4n39i2z3o7o3bg70iev4",
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
                        "content": "I'll fetch information about Kyungju city.\n<tool_call>fetch_wikipedia_content\n<arg_key>search_query</arg_key>\n<arg_value>Kyungju Korea</arg_value>\n</tool_call>"
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 632,
                "completion_tokens": 41,
                "total_tokens": 673
            }
        }
        
        converted = self.converter.convert_response(glm_response)
        
        # Check that tool_calls were added
        message = converted['choices'][0]['message']
        self.assertIn('tool_calls', message)
        self.assertEqual(len(message['tool_calls']), 1)
        self.assertEqual(message['tool_calls'][0]['function']['name'], 'fetch_wikipedia_content')
        
        # Check that finish_reason was updated
        self.assertEqual(converted['choices'][0]['finish_reason'], 'tool_calls')
        
        # Check that content was cleaned
        self.assertEqual(message['content'], "I'll fetch information about Kyungju city.")
    
    def test_convert_response_standard_format(self):
        """Test that standard format responses are not modified"""
        standard_response = {
            "id": "chatcmpl-shlg1zo2jmivd2x6lo5ggr",
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
        
        converted = self.converter.convert_response(standard_response)
        
        # Should be unchanged
        self.assertEqual(converted, standard_response)

def test_proxy_server():
    """Test proxy server functionality"""
    print("\n=== Testing Proxy Server ===")
    
    base_url = "http://localhost:5000"
    
    # Test health endpoint
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Health check: {response.status_code} - {response.json()}")
    except requests.RequestException as e:
        print(f"Health check failed: {e}")
        return False
    
    # Test chat completions with mock GLM response
    print("\nTesting chat completions...")
    test_request = {
        "model": "glm-4.5-air-hi-mlx@4bit",
        "messages": [
            {"role": "user", "content": "Tell me about Kyungju city"}
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "fetch_wikipedia_content",
                    "description": "Fetch content from Wikipedia",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search_query": {"type": "string"}
                        }
                    }
                }
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            json=test_request,
            timeout=30
        )
        print(f"Chat completions: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error response: {response.text}")
    except requests.RequestException as e:
        print(f"Chat completions test failed: {e}")
        return False
    
    return True

if __name__ == '__main__':
    print("Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "="*50)
    print("Running integration tests...")
    print("Make sure the proxy server is running on port 5000")
    print("and the backend API is running on port 8888")
    
    input("Press Enter to continue with integration tests...")
    test_proxy_server()