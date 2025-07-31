#!/usr/bin/env python3
"""
Debug tool call conversion with actual GLM model
"""

import json
import requests

def test_direct_backend():
    """Test direct backend call to see GLM response format"""
    print("=== Testing Direct Backend Call ===")
    
    test_request = {
        "model": "glm-4.5-air-hi-mlx@4bit",
        "messages": [
            {"role": "user", "content": "tell me about lee jae myung"}
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "fetch_wikipedia_content",
                    "description": "Search Wikipedia and fetch the introduction of the most relevant article",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search_query": {
                                "type": "string",
                                "description": "Search query for finding the Wikipedia article"
                            }
                        },
                        "required": ["search_query"]
                    }
                }
            }
        ]
    }
    
    try:
        print("Sending request to backend (port 8888)...")
        response = requests.post(
            "http://localhost:8888/v1/chat/completions",
            json=test_request,
            timeout=30
        )
        
        print(f"Backend response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Backend response:")
            print(json.dumps(result, indent=2))
            
            # Check message content for GLM format
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0].get('message', {})
                content = message.get('content', '')
                if '<tool_call>' in content:
                    print("\n✅ GLM tool call format detected in backend response!")
                    print(f"Content: {content}")
                else:
                    print("\n❌ No GLM tool call format found in backend response")
            
            return result
        else:
            print(f"Backend error: {response.text}")
            return None
            
    except Exception as e:
        print(f"Backend request failed: {e}")
        return None

def test_proxy_conversion():
    """Test proxy server conversion"""
    print("\n=== Testing Proxy Server Conversion ===")
    
    test_request = {
        "model": "glm-4.5-air-hi-mlx@4bit",
        "messages": [
            {"role": "user", "content": "tell me about lee jae myung"}
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "fetch_wikipedia_content",
                    "description": "Search Wikipedia and fetch the introduction of the most relevant article",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "search_query": {
                                "type": "string",
                                "description": "Search query for finding the Wikipedia article"
                            }
                        },
                        "required": ["search_query"]
                    }
                }
            }
        ]
    }
    
    try:
        print("Sending request to proxy (port 5000)...")
        response = requests.post(
            "http://localhost:5000/v1/chat/completions",
            json=test_request,
            timeout=30
        )
        
        print(f"Proxy response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Proxy response:")
            print(json.dumps(result, indent=2))
            
            # Check if conversion worked
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0].get('message', {})
                
                if 'tool_calls' in message and len(message['tool_calls']) > 0:
                    print("\n✅ Tool call conversion successful!")
                    for tool_call in message['tool_calls']:
                        print(f"   Function: {tool_call['function']['name']}")
                        print(f"   Arguments: {tool_call['function']['arguments']}")
                    print(f"   Finish reason: {result['choices'][0]['finish_reason']}")
                    return True
                else:
                    print("\n❌ No tool calls found in proxy response")
                    content = message.get('content', '')
                    if '<tool_call>' in content:
                        print(f"❌ GLM format still present: {content}")
                    return False
        else:
            print(f"Proxy error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Proxy request failed: {e}")
        return False

def test_openai_client():
    """Test with OpenAI client like lmstudio-tooluse-test.py does"""
    print("\n=== Testing OpenAI Client ===")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(base_url="http://127.0.0.1:5000", api_key="lm-studio")
        
        response = client.chat.completions.create(
            model="glm-4.5-air-hi-mlx@4bit",
            messages=[
                {"role": "user", "content": "tell me about lee jae myung"}
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "fetch_wikipedia_content",
                        "description": "Search Wikipedia and fetch the introduction of the most relevant article",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "search_query": {
                                    "type": "string",
                                    "description": "Search query for finding the Wikipedia article"
                                }
                            },
                            "required": ["search_query"]
                        }
                    }
                }
            ]
        )
        
        print("OpenAI client response:")
        print(f"Content: {response.choices[0].message.content}")
        
        if response.choices[0].message.tool_calls:
            print("✅ Tool calls detected by OpenAI client!")
            for tool_call in response.choices[0].message.tool_calls:
                print(f"   Function: {tool_call.function.name}")
                print(f"   Arguments: {tool_call.function.arguments}")
            return True
        else:
            print("❌ No tool calls detected by OpenAI client")
            return False
            
    except Exception as e:
        print(f"OpenAI client test failed: {e}")
        return False

def main():
    print("Debugging Tool Call Conversion")
    print("=" * 50)
    
    # Test 1: Direct backend call
    backend_response = test_direct_backend()
    
    # Test 2: Proxy conversion
    proxy_success = test_proxy_conversion()
    
    # Test 3: OpenAI client (like lmstudio-tooluse-test.py)
    client_success = test_openai_client()
    
    print("\n" + "=" * 50)
    print("Debug Results:")
    print(f"Backend Response: {'✅ RECEIVED' if backend_response else '❌ FAILED'}")
    print(f"Proxy Conversion: {'✅ SUCCESS' if proxy_success else '❌ FAILED'}")
    print(f"OpenAI Client: {'✅ SUCCESS' if client_success else '❌ FAILED'}")
    
    if not proxy_success:
        print("\n🔍 Debugging suggestions:")
        print("1. Check if GLM model returns <tool_call> format")
        print("2. Verify converter factory model detection")
        print("3. Check if ENABLE_TOOL_CALL_CONVERSION is true")
        print("4. Review proxy server logs")

if __name__ == '__main__':
    main()