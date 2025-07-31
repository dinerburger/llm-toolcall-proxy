#!/usr/bin/env python3
"""
Test simple streaming without tool calls
"""

import requests
from openai import OpenAI

def test_simple_streaming():
    """Test basic streaming without any tool calls"""
    print("Testing Simple Streaming (No Tool Calls)")
    print("=" * 40)
    
    client = OpenAI(base_url="http://127.0.0.1:5000", api_key="lm-studio")
    
    try:
        print("Testing simple streaming request...")
        stream_response = client.chat.completions.create(
            model="glm-4.5-air-hi-mlx@4bit",
            messages=[
                {"role": "user", "content": "Write a short poem about coding"}
            ],
            stream=True
        )
        
        print("✅ Streaming request successful")
        print("Response chunks:")
        
        collected_content = ""
        chunk_count = 0
        
        for chunk in stream_response:
            chunk_count += 1
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                collected_content += content
            
            if chunk_count > 100:  # Safety limit
                print("\n[Truncated - too many chunks]")
                break
        
        print(f"\n\nSimple streaming works! ({chunk_count} chunks, {len(collected_content)} chars)")
        return True
        
    except Exception as e:
        print(f"❌ Simple streaming failed: {e}")
        return False

def test_raw_streaming():
    """Test raw HTTP streaming request"""
    print("\n" + "=" * 40)
    print("Testing Raw HTTP Streaming")
    print("=" * 40)
    
    try:
        response = requests.post(
            "http://localhost:5000/v1/chat/completions",
            json={
                "model": "glm-4.5-air-hi-mlx@4bit",
                "messages": [
                    {"role": "user", "content": "Say hello"}
                ],
                "stream": True
            },
            stream=True,
            timeout=30
        )
        
        print(f"Raw streaming status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Raw streaming works")
            chunk_count = 0
            for line in response.iter_lines(decode_unicode=True):
                chunk_count += 1
                print(f"Line {chunk_count}: {line}")
                
                if chunk_count > 10:  # Just show first few lines
                    print("...[truncated]")
                    break
            
            return True
        else:
            print(f"❌ Raw streaming failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Raw streaming error: {e}")
        return False

def main():
    simple_works = test_simple_streaming()
    raw_works = test_raw_streaming()
    
    print("\n" + "=" * 40)
    print("Results:")
    print(f"Simple Streaming: {'✅ WORKS' if simple_works else '❌ FAILED'}")
    print(f"Raw HTTP Streaming: {'✅ WORKS' if raw_works else '❌ FAILED'}")

if __name__ == '__main__':
    main()