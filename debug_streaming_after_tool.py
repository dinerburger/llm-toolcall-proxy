#!/usr/bin/env python3
"""
Debug streaming response after tool calls
"""

import json
import requests
from openai import OpenAI

def test_streaming_after_tool_call():
    """Test the exact scenario from lmstudio-tooluse-test.py"""
    print("Testing Streaming After Tool Call")
    print("=" * 40)
    
    client = OpenAI(base_url="http://127.0.0.1:5000", api_key="lm-studio")
    MODEL = "glm-4.5-air-hi-mlx@4bit"
    
    # Simulate the exact message flow from lmstudio-tooluse-test.py
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that can retrieve Wikipedia articles. "
                "When asked about a topic, you can retrieve Wikipedia articles "
                "and cite information from them."
            ),
        },
        {"role": "user", "content": "tell me about lee jae myung"},
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "test_id_123",
                    "type": "function",
                    "function": {
                        "name": "fetch_wikipedia_content",
                        "arguments": '{"search_query": "Lee Jae-myung"}'
                    }
                }
            ],
        },
        {
            "role": "tool",
            "content": '{"status": "success", "content": "Lee Jae Myung is a South Korean politician...", "title": "Lee Jae Myung"}',
            "tool_call_id": "test_id_123",
        }
    ]
    
    print("Testing non-streaming first...")
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )
        print("✅ Non-streaming works")
        print(f"Response: {response.choices[0].message.content[:100]}...")
    except Exception as e:
        print(f"❌ Non-streaming failed: {e}")
        return False
    
    print("\nTesting streaming...")
    try:
        stream_response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            stream=True
        )
        
        print("✅ Streaming request successful")
        print("Collecting chunks...")
        
        collected_content = ""
        chunk_count = 0
        
        for chunk in stream_response:
            chunk_count += 1
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                collected_content += content
            
            if chunk_count > 50:  # Safety limit
                print("\n[Truncated - too many chunks]")
                break
        
        print(f"\n\nCollected {len(collected_content)} characters in {chunk_count} chunks")
        print("✅ Streaming after tool call works!")
        return True
        
    except Exception as e:
        print(f"❌ Streaming failed: {e}")
        print(f"Error type: {type(e)}")
        
        # Try to get more details
        if hasattr(e, 'response'):
            print(f"Response status: {e.response.status_code if e.response else 'None'}")
            print(f"Response text: {e.response.text if e.response else 'None'}")
        
        return False

def test_direct_backend_streaming():
    """Test streaming directly to backend"""
    print("\n" + "=" * 40)
    print("Testing Direct Backend Streaming")
    print("=" * 40)
    
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {"role": "user", "content": "tell me about lee jae myung"},
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "test_id_123",
                    "type": "function",
                    "function": {
                        "name": "fetch_wikipedia_content",
                        "arguments": '{"search_query": "Lee Jae-myung"}'
                    }
                }
            ],
        },
        {
            "role": "tool",
            "content": '{"status": "success", "content": "Lee Jae Myung is a South Korean politician...", "title": "Lee Jae Myung"}',
            "tool_call_id": "test_id_123",
        }
    ]
    
    try:
        print("Testing direct backend streaming...")
        response = requests.post(
            "http://localhost:8888/v1/chat/completions",
            json={
                "model": "glm-4.5-air-hi-mlx@4bit",
                "messages": messages,
                "stream": True
            },
            stream=True,
            timeout=30
        )
        
        print(f"Backend streaming status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Backend streaming works")
            chunk_count = 0
            for line in response.iter_lines(decode_unicode=True):
                chunk_count += 1
                if line.startswith('data: '):
                    data = line[6:]
                    if data.strip() == '[DONE]':
                        break
                    try:
                        chunk_data = json.loads(data)
                        if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                            delta = chunk_data['choices'][0].get('delta', {})
                            if 'content' in delta and delta['content']:
                                print(delta['content'], end="", flush=True)
                    except json.JSONDecodeError:
                        pass
                
                if chunk_count > 100:  # Safety limit
                    break
            
            print(f"\n✅ Backend streaming successful ({chunk_count} chunks)")
            return True
        else:
            print(f"❌ Backend streaming failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Backend streaming error: {e}")
        return False

def main():
    print("Debugging Streaming After Tool Calls")
    print("=" * 50)
    
    # Test 1: Streaming through proxy after tool call
    proxy_success = test_streaming_after_tool_call()
    
    # Test 2: Direct backend streaming
    backend_success = test_direct_backend_streaming()
    
    print("\n" + "=" * 50)
    print("Debug Results:")
    print(f"Proxy Streaming: {'✅ WORKS' if proxy_success else '❌ FAILED'}")
    print(f"Backend Streaming: {'✅ WORKS' if backend_success else '❌ FAILED'}")
    
    if not proxy_success and backend_success:
        print("\n🔍 Issue is in the proxy streaming implementation")
        print("Check _handle_streaming_response method")
    elif not backend_success:
        print("\n🔍 Issue is in the backend server")
        print("Check LM Studio server configuration")
    elif proxy_success and backend_success:
        print("\n🎉 Both proxy and backend streaming work!")

if __name__ == '__main__':
    main()