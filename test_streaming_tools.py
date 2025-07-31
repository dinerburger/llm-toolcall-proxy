#!/usr/bin/env python3
"""
Test streaming tool call conversion functionality
"""

import json
import requests
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class MockStreamingGLMHandler(BaseHTTPRequestHandler):
    """Mock GLM backend that returns streaming responses with tool calls"""
    
    def do_POST(self):
        if self.path == '/v1/chat/completions':
            # Read the request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            # Check if streaming and tools are requested
            is_streaming = request_data.get('stream', False)
            has_tools = 'tools' in request_data and len(request_data['tools']) > 0
            
            if is_streaming and has_tools:
                self._send_streaming_tool_response()
            elif is_streaming:
                self._send_streaming_normal_response()
            else:
                self._send_normal_response(has_tools)
        else:
            self.send_response(404)
            self.end_headers()
    
    def _send_streaming_tool_response(self):
        """Send streaming response with GLM tool call format"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.end_headers()
        
        # Simulate streaming chunks that build up to a tool call
        chunks = [
            {
                "id": "chatcmpl-stream-test",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "glm-4.5-air-hi-mlx@4bit",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"role": "assistant", "content": "I'll search for that information."},
                        "finish_reason": None
                    }
                ]
            },
            {
                "id": "chatcmpl-stream-test",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "glm-4.5-air-hi-mlx@4bit",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": "\n<tool_call>fetch_wikipedia_content"},
                        "finish_reason": None
                    }
                ]
            },
            {
                "id": "chatcmpl-stream-test",
                "object": "chat.completion.chunk", 
                "created": int(time.time()),
                "model": "glm-4.5-air-hi-mlx@4bit",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": "\n<arg_key>search_query</arg_key>"},
                        "finish_reason": None
                    }
                ]
            },
            {
                "id": "chatcmpl-stream-test",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "glm-4.5-air-hi-mlx@4bit",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": "\n<arg_value>Python programming</arg_value>\n</tool_call>"},
                        "finish_reason": None
                    }
                ]
            },
            {
                "id": "chatcmpl-stream-test",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "glm-4.5-air-hi-mlx@4bit",
                "choices": [
                    {
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop"
                    }
                ]
            }
        ]
        
        for chunk in chunks:
            chunk_str = f"data: {json.dumps(chunk)}\n\n"
            self.wfile.write(chunk_str.encode())
            self.wfile.flush()
            time.sleep(0.1)  # Small delay to simulate streaming
        
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()
    
    def _send_streaming_normal_response(self):
        """Send streaming response without tool calls"""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.end_headers()
        
        chunks = [
            {
                "id": "chatcmpl-stream-normal",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "glm-4.5-air-hi-mlx@4bit",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"role": "assistant", "content": "Hello! "},
                        "finish_reason": None
                    }
                ]
            },
            {
                "id": "chatcmpl-stream-normal",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "glm-4.5-air-hi-mlx@4bit",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": "How can I help you today?"},
                        "finish_reason": None
                    }
                ]
            },
            {
                "id": "chatcmpl-stream-normal",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "glm-4.5-air-hi-mlx@4bit",
                "choices": [
                    {
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop"
                    }
                ]
            }
        ]
        
        for chunk in chunks:
            chunk_str = f"data: {json.dumps(chunk)}\n\n"
            self.wfile.write(chunk_str.encode())
            self.wfile.flush()
            time.sleep(0.1)
        
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()
    
    def _send_normal_response(self, has_tools):
        """Send normal non-streaming response"""
        if has_tools:
            response = {
                "id": "chatcmpl-normal-tools",
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
                            "content": "I'll search for that.\n<tool_call>fetch_wikipedia_content\n<arg_key>search_query</arg_key>\n<arg_value>Python programming</arg_value>\n</tool_call>"
                        }
                    }
                ]
            }
        else:
            response = {
                "id": "chatcmpl-normal",
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
                            "content": "Hello! How can I help you?"
                        }
                    }
                ]
            }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response_str = json.dumps(response)
        self.wfile.write(response_str.encode())
    
    def log_message(self, format, *args):
        # Suppress HTTP logs
        pass

def start_mock_server():
    """Start mock server on port 8888"""
    server = HTTPServer(('localhost', 8888), MockStreamingGLMHandler)
    print("Mock streaming GLM server started on port 8888")
    server.serve_forever()

def test_streaming_tool_calls():
    """Test streaming tool call conversion"""
    print("=== Testing Streaming Tool Call Conversion ===")
    
    # Start mock server
    server_thread = threading.Thread(target=start_mock_server, daemon=True)
    server_thread.start()
    time.sleep(2)
    
    # Test streaming request with tools
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
        ],
        "stream": True
    }
    
    try:
        print("Sending streaming request with tools...")
        response = requests.post(
            "http://localhost:5000/v1/chat/completions",
            json=test_request,
            stream=True,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("Streaming response chunks:")
            chunks_received = 0
            tool_calls_found = False
            
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    data = line[6:]
                    if data.strip() == '[DONE]':
                        print("Stream completed with [DONE]")
                        break
                    
                    try:
                        chunk = json.loads(data)
                        chunks_received += 1
                        
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            choice = chunk['choices'][0]
                            delta = choice.get('delta', {})
                            
                            print(f"Chunk {chunks_received}:")
                            if 'content' in delta and delta['content']:
                                print(f"  Content: {repr(delta['content'])}")
                            if 'tool_calls' in delta:
                                print(f"  Tool calls: {delta['tool_calls']}")
                                tool_calls_found = True
                            if 'finish_reason' in choice and choice['finish_reason']:
                                print(f"  Finish reason: {choice['finish_reason']}")
                    
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse chunk: {e}")
                        print(f"Raw data: {data}")
            
            print(f"\nTotal chunks received: {chunks_received}")
            if tool_calls_found:
                print("✅ SUCCESS: Tool calls detected in streaming response!")
                return True
            else:
                print("❌ FAILED: No tool calls found in streaming response")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_streaming_normal():
    """Test streaming without tool calls"""
    print("\n=== Testing Streaming Normal Response ===")
    
    test_request = {
        "model": "glm-4.5-air-hi-mlx", 
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "stream": True
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/v1/chat/completions",
            json=test_request,
            stream=True,
            timeout=10
        )
        
        if response.status_code == 200:
            chunks_received = 0
            content_received = ""
            
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    data = line[6:]
                    if data.strip() == '[DONE]':
                        break
                    
                    try:
                        chunk = json.loads(data)
                        chunks_received += 1
                        
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            if 'content' in delta and delta['content']:
                                content_received += delta['content']
                    
                    except json.JSONDecodeError:
                        pass
            
            print(f"Chunks received: {chunks_received}")
            print(f"Content: {repr(content_received)}")
            
            if chunks_received > 0 and content_received:
                print("✅ SUCCESS: Normal streaming works!")
                return True
            else:
                print("❌ FAILED: No content received")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("Testing Streaming Tool Call Conversion")
    print("=" * 50)
    
    # Test streaming tool calls
    streaming_tools_ok = test_streaming_tool_calls()
    
    # Test streaming normal
    streaming_normal_ok = test_streaming_normal()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Streaming Tool Calls: {'✅ PASS' if streaming_tools_ok else '❌ FAIL'}")
    print(f"Streaming Normal: {'✅ PASS' if streaming_normal_ok else '❌ FAIL'}")
    
    if streaming_tools_ok and streaming_normal_ok:
        print("\n🎉 Streaming tool call conversion is working!")
    else:
        print("\n❌ Some streaming tests failed.")

if __name__ == '__main__':
    main()