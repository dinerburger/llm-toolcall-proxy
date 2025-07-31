#!/usr/bin/env python3
"""
Simple test runner that starts the proxy server and runs tests
"""

import subprocess
import time
import requests
import json
import sys
import signal
import os

def test_tool_call_conversion():
    """Test the tool call conversion logic directly"""
    print("=== Testing Tool Call Conversion ===")
    
    # Import our converter
    from app import ToolCallConverter
    
    converter = ToolCallConverter()
    
    # Test GLM format response
    glm_response = {
        "id": "chatcmpl-test",
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
                    "content": "I'll search for information about Kyungju.\n<tool_call>fetch_wikipedia_content\n<arg_key>search_query</arg_key>\n<arg_value>Kyungju Korea</arg_value>\n</tool_call>"
                }
            }
        ],
        "usage": {
            "prompt_tokens": 632,
            "completion_tokens": 41,
            "total_tokens": 673
        }
    }
    
    print("Original GLM response:")
    print(json.dumps(glm_response, indent=2))
    
    converted = converter.convert_response(glm_response)
    
    print("\nConverted response:")
    print(json.dumps(converted, indent=2))
    
    # Verify conversion worked
    message = converted['choices'][0]['message']
    if 'tool_calls' in message and len(message['tool_calls']) > 0:
        print("✅ Tool call conversion successful!")
        tool_call = message['tool_calls'][0]
        print(f"   Function: {tool_call['function']['name']}")
        print(f"   Arguments: {tool_call['function']['arguments']}")
        print(f"   Finish reason: {converted['choices'][0]['finish_reason']}")
        return True
    else:
        print("❌ Tool call conversion failed!")
        return False

def test_proxy_with_mock_backend():
    """Test proxy with a mock backend server"""
    print("\n=== Testing Proxy with Mock Backend ===")
    
    # Create a simple mock backend response
    mock_glm_response = {
        "id": "chatcmpl-mock",
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
                    "content": "I'll help you with that.\n<tool_call>fetch_wikipedia_content\n<arg_key>search_query</arg_key>\n<arg_value>Kyungju historical city Korea</arg_value>\n</tool_call>"
                }
            }
        ],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 30,
            "total_tokens": 80
        }
    }
    
    print("Mock GLM backend response:")
    print(json.dumps(mock_glm_response, indent=2))
    
    # Start a simple mock server
    mock_server_code = f'''
import http.server
import socketserver
import json

class MockHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/chat/completions':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {json.dumps(mock_glm_response)}
            self.wfile.write(response.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress logs

PORT = 8888
with socketserver.TCPServer(("", PORT), MockHandler) as httpd:
    print(f"Mock server running on port {{PORT}}")
    httpd.serve_forever()
'''
    
    # Write mock server to file
    with open('/tmp/mock_server.py', 'w') as f:
        f.write(mock_server_code)
    
    # Start mock server
    print("Starting mock backend server on port 8888...")
    mock_process = subprocess.Popen([sys.executable, '/tmp/mock_server.py'])
    time.sleep(2)
    
    try:
        # Test if we can reach the proxy
        print("Testing proxy server...")
        
        test_request = {
            "model": "glm-4.5-air-hi-mlx@4bit",
            "messages": [
                {"role": "user", "content": "Tell me about Kyungju"}
            ]
        }
        
        try:
            response = requests.post(
                "http://localhost:5000/chat/completions",
                json=test_request,
                timeout=10
            )
            
            print(f"Proxy response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("Proxy response:")
                print(json.dumps(result, indent=2))
                
                # Check if tool calls were converted
                message = result['choices'][0]['message']
                if 'tool_calls' in message:
                    print("✅ End-to-end test successful! Tool calls were converted.")
                    return True
                else:
                    print("❌ Tool calls were not converted properly.")
                    return False
            else:
                print(f"❌ Proxy returned error: {response.text}")
                return False
                
        except requests.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False
            
    finally:
        # Clean up mock server
        mock_process.terminate()
        mock_process.wait()
        if os.path.exists('/tmp/mock_server.py'):
            os.remove('/tmp/mock_server.py')

def main():
    print("Flask Proxy Server Test Suite")
    print("=" * 40)
    
    # Test 1: Tool call conversion logic
    conversion_success = test_tool_call_conversion()
    
    # Test 2: Check if proxy server is running
    try:
        health_response = requests.get("http://localhost:5000/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Proxy server is running")
            proxy_running = True
        else:
            print("❌ Proxy server health check failed")
            proxy_running = False
    except requests.RequestException:
        print("❌ Proxy server is not running")
        proxy_running = False
    
    # Test 3: End-to-end test with mock backend
    if proxy_running:
        e2e_success = test_proxy_with_mock_backend()
    else:
        print("Skipping end-to-end test (proxy server not running)")
        e2e_success = False
    
    print("\n" + "=" * 40)
    print("Test Results:")
    print(f"Tool Call Conversion: {'✅ PASS' if conversion_success else '❌ FAIL'}")
    print(f"Proxy Server Running: {'✅ PASS' if proxy_running else '❌ FAIL'}")
    print(f"End-to-End Test: {'✅ PASS' if e2e_success else '❌ FAIL'}")
    
    if not proxy_running:
        print("\nTo run the proxy server:")
        print("python app.py")

if __name__ == '__main__':
    main()