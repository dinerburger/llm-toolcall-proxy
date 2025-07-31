#!/usr/bin/env python3
"""
Test the integration between the proxy server and lmstudio-tooluse-test.py
"""

import json
import requests
import time
import subprocess
import sys
import signal
import os

def test_proxy_server():
    """Test if proxy server is running and responding"""
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Proxy server is running")
            return True
        else:
            print(f"❌ Proxy server health check failed: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Proxy server not reachable: {e}")
        return False

def test_chat_completions_endpoint():
    """Test the /v1/chat/completions endpoint"""
    test_request = {
        "model": "glm-4.5-air-hi-mlx",
        "messages": [
            {"role": "user", "content": "Hello, can you help me?"}
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "test_function",
                    "description": "A test function",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "param": {"type": "string"}
                        }
                    }
                }
            }
        ]
    }
    
    try:
        print("Testing /v1/chat/completions endpoint...")
        response = requests.post(
            "http://localhost:5000/v1/chat/completions",
            json=test_request,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ Endpoint responded with JSON")
                
                # Check if response has expected structure
                if 'choices' in result and len(result['choices']) > 0:
                    message = result['choices'][0].get('message', {})
                    if 'tool_calls' in message:
                        print("✅ Tool calls detected in response")
                        print(f"Tool calls: {json.dumps(message['tool_calls'], indent=2)}")
                    else:
                        print("ℹ️  No tool calls in response (normal for non-tool responses)")
                        print(f"Content: {message.get('content', 'No content')}")
                    return True
                else:
                    print("❌ Unexpected response structure")
                    print(f"Response: {json.dumps(result, indent=2)}")
                    return False
                    
            except json.JSONDecodeError:
                print("❌ Response is not valid JSON")
                print(f"Response text: {response.text}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_openai_client_connection():
    """Test OpenAI client connection through proxy"""
    try:
        print("Testing OpenAI client connection...")
        
        # This mimics what lmstudio-tooluse-test.py does
        from openai import OpenAI
        
        client = OpenAI(base_url="http://127.0.0.1:5000", api_key="lm-studio")
        
        response = client.chat.completions.create(
            model="glm-4.5-air-hi-mlx",
            messages=[
                {"role": "user", "content": "Say hello"}
            ],
            timeout=30
        )
        
        print("✅ OpenAI client connected successfully")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI client connection failed: {e}")
        return False

def main():
    print("Testing LM Studio Integration with Proxy Server")
    print("=" * 50)
    
    # Test 1: Proxy server health
    proxy_running = test_proxy_server()
    
    if not proxy_running:
        print("\n❌ Proxy server is not running. Please start it first:")
        print("python app.py")
        return
    
    # Test 2: Chat completions endpoint
    endpoint_working = test_chat_completions_endpoint()
    
    # Test 3: OpenAI client connection
    client_working = test_openai_client_connection()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Proxy Server Running: {'✅ PASS' if proxy_running else '❌ FAIL'}")
    print(f"Chat Completions Endpoint: {'✅ PASS' if endpoint_working else '❌ FAIL'}")
    print(f"OpenAI Client Connection: {'✅ PASS' if client_working else '❌ FAIL'}")
    
    if proxy_running and endpoint_working and client_working:
        print("\n🎉 All tests passed! lmstudio-tooluse-test.py should work now.")
        print("\nTo run the Wikipedia chatbot:")
        print("python lmstudio-tooluse-test.py")
        print("\nMake sure your LM Studio server is running on port 8888 with GLM model loaded.")
    else:
        print("\n❌ Some tests failed. Check the proxy server and backend connection.")
        
        if not proxy_running:
            print("- Start proxy server: python app.py")
        if not endpoint_working:
            print("- Check backend LM Studio server on port 8888")
        if not client_working:
            print("- Check OpenAI client compatibility")

if __name__ == '__main__':
    main()