#!/usr/bin/env python3
"""
Test actual tool call functionality with GLM model
This creates a mock backend that returns GLM-style tool call responses
to verify our proxy conversion works end-to-end
"""

import json
import requests
import subprocess
import time
import sys
import signal
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver
import threading

class MockGLMHandler(BaseHTTPRequestHandler):
    """Mock GLM backend that returns GLM-style tool call responses"""
    
    def do_POST(self):
        if self.path == '/v1/chat/completions':
            # Read the request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Check if tools are requested
            has_tools = 'tools' in request_data and len(request_data['tools']) > 0
            
            if has_tools:
                # Return GLM-style tool call response
                glm_response = {
                    "id": "chatcmpl-mock-glm",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": "glm-4.5-air-hi-mlx@4bit",
                    "choices": [
                        {
                            "index": 0,
                            "logprobs": None,
                            "finish_reason": "stop",
                            "message": {
                                "role": "assistant",
                                "content": "I'll search for information about that topic.\n<tool_call>fetch_wikipedia_content\n<arg_key>search_query</arg_key>\n<arg_value>Python programming language</arg_value>\n</tool_call>"
                            }
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 50,
                        "completion_tokens": 30,
                        "total_tokens": 80
                    }
                }
            else:
                # Return normal response
                glm_response = {
                    "id": "chatcmpl-mock-normal",
                    "object": "chat.completion", 
                    "created": int(time.time()),
                    "model": "glm-4.5-air-hi-mlx@4bit",
                    "choices": [
                        {
                            "index": 0,
                            "logprobs": None,
                            "finish_reason": "stop",
                            "message": {
                                "role": "assistant",
                                "content": "Hello! I'm a mock GLM response. How can I help you?"
                            }
                        }
                    ],
                    "usage": {
                        "prompt_tokens": 20,
                        "completion_tokens": 15,
                        "total_tokens": 35
                    }
                }
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response_str = json.dumps(glm_response)
            self.wfile.write(response_str.encode())
            
            print(f"Mock GLM returned: {response_str}")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress HTTP logs
        pass

def start_mock_glm_server():
    """Start mock GLM server on port 8888"""
    server = HTTPServer(('localhost', 8888), MockGLMHandler)
    print("Mock GLM server started on port 8888")
    server.serve_forever()

def test_tool_call_conversion():
    """Test tool call conversion through proxy"""
    print("=== Testing Tool Call Conversion ===")
    
    # Start mock GLM server in background
    server_thread = threading.Thread(target=start_mock_glm_server, daemon=True)
    server_thread.start()
    time.sleep(2)  # Wait for server to start
    
    # Test request with tools (should trigger GLM tool call response)
    test_request = {
        "model": "glm-4.5-air-hi-mlx",
        "messages": [
            {"role": "user", "content": "Tell me about Python programming"}
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "fetch_wikipedia_content",
                    "description": "Fetch Wikipedia content",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search_query": {"type": "string"}
                        },
                        "required": ["search_query"]
                    }
                }
            }
        ]
    }
    
    try:
        print("Sending request with tools to proxy...")
        response = requests.post(
            "http://localhost:5000/v1/chat/completions",
            json=test_request,
            timeout=10
        )
        
        print(f"Proxy response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Proxy response:")
            print(json.dumps(result, indent=2))
            
            # Check if conversion worked
            message = result['choices'][0]['message']
            
            if 'tool_calls' in message and len(message['tool_calls']) > 0:
                print("\n✅ SUCCESS: GLM tool call converted to standard format!")
                tool_call = message['tool_calls'][0]
                print(f"   Function: {tool_call['function']['name']}")
                print(f"   Arguments: {tool_call['function']['arguments']}")
                print(f"   Finish reason: {result['choices'][0]['finish_reason']}")
                
                # Verify content was cleaned
                if '<tool_call>' not in message.get('content', ''):
                    print("   ✅ Content cleaned of tool call markup")
                else:
                    print("   ❌ Content still contains tool call markup")
                    
                return True
            else:
                print("\n❌ FAILED: Tool call was not converted")
                print(f"Message content: {message.get('content', 'No content')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_openai_client_with_tools():
    """Test OpenAI client with tool calls"""
    print("\n=== Testing OpenAI Client with Tools ===")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(base_url="http://127.0.0.1:5000", api_key="lm-studio")
        
        # Test with tools (should get GLM tool call response)
        response = client.chat.completions.create(
            model="glm-4.5-air-hi-mlx",
            messages=[
                {"role": "user", "content": "Search for information about artificial intelligence"}
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "fetch_wikipedia_content",
                        "description": "Fetch Wikipedia content",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "search_query": {"type": "string"}
                            },
                            "required": ["search_query"]
                        }
                    }
                }
            ]
        )
        
        print("OpenAI client response:")
        print(f"  Content: {response.choices[0].message.content}")
        
        if response.choices[0].message.tool_calls:
            print("  ✅ Tool calls detected!")
            for tool_call in response.choices[0].message.tool_calls:
                print(f"    Function: {tool_call.function.name}")
                print(f"    Arguments: {tool_call.function.arguments}")
            return True
        else:
            print("  ❌ No tool calls found")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI client test failed: {e}")
        return False

def main():
    print("Testing Tool Call Conversion End-to-End")
    print("=" * 50)
    
    # Test 1: Direct HTTP request
    conversion_test = test_tool_call_conversion()
    
    # Test 2: OpenAI client
    client_test = test_openai_client_with_tools()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Tool Call Conversion: {'✅ PASS' if conversion_test else '❌ FAIL'}")
    print(f"OpenAI Client Tools: {'✅ PASS' if client_test else '❌ FAIL'}")
    
    if conversion_test and client_test:
        print("\n🎉 Tool call conversion is working correctly!")
        print("lmstudio-tooluse-test.py should work properly with tool calls.")
    else:
        print("\n❌ Tool call conversion has issues.")
        print("Check the proxy server implementation.")

if __name__ == '__main__':
    main()