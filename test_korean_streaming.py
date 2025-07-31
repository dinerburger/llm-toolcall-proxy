#!/usr/bin/env python3
"""
Test Korean text streaming to identify encoding issues
"""

import json
import requests
from openai import OpenAI

# Test both direct backend and proxy
BACKEND_URL = "http://localhost:8888"
PROXY_URL = "http://127.0.0.1:5000"

def test_direct_backend_korean():
    """Test direct backend Korean streaming"""
    print("Testing Direct Backend Korean Streaming")
    print("=" * 50)
    
    payload = {
        "model": "glm-4.5-air-hi-mlx@4bit",
        "messages": [
            {"role": "user", "content": "안녕하세요. 한국어로 간단한 시를 써주세요."}
        ],
        "stream": True,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            stream=True
        )
        
        print(f"Backend status: {response.status_code}")
        print(f"Backend headers: {dict(response.headers)}")
        print("Backend response:")
        
        chunk_count = 0
        for line in response.iter_lines(decode_unicode=True):
            chunk_count += 1
            if line and chunk_count <= 10:  # Show first 10 chunks
                print(f"Chunk {chunk_count}: {repr(line)}")
                if line.startswith('data: ') and line[6:].strip() != '[DONE]':
                    try:
                        data = json.loads(line[6:])
                        content = data.get('choices', [{}])[0].get('delta', {}).get('content', '')
                        if content:
                            print(f"  Content: {repr(content)} -> {content}")
                    except:
                        pass
            elif chunk_count > 20:
                print("... (truncated)")
                break
                
        print(f"Total chunks: {chunk_count}")
        
    except Exception as e:
        print(f"❌ Backend test failed: {e}")

def test_proxy_korean():
    """Test proxy Korean streaming"""
    print("\nTesting Proxy Korean Streaming")
    print("=" * 50)
    
    try:
        client = OpenAI(base_url=PROXY_URL, api_key="test")
        
        # Test with OpenAI client
        print("Using OpenAI client...")
        stream_response = client.chat.completions.create(
            model="glm-4.5-air-hi-mlx@4bit",
            messages=[
                {"role": "user", "content": "안녕하세요. 한국어로 간단한 시를 써주세요."}
            ],
            stream=True,
            temperature=0.7
        )
        
        print("Proxy streaming chunks:")
        chunk_count = 0
        collected_content = ""
        
        for chunk in stream_response:
            chunk_count += 1
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                collected_content += content
                if chunk_count <= 10:  # Show first 10 chunks with content
                    print(f"Chunk {chunk_count}: {repr(content)} -> {content}")
                    
            if chunk_count > 50:  # Safety limit
                print("... (truncated)")
                break
        
        print(f"\nTotal chunks: {chunk_count}")
        print(f"Final collected content: {collected_content}")
        
    except Exception as e:
        print(f"❌ Proxy test failed: {e}")

def test_raw_proxy_korean():
    """Test raw HTTP proxy Korean streaming"""
    print("\nTesting Raw Proxy Korean Streaming")
    print("=" * 50)
    
    payload = {
        "model": "glm-4.5-air-hi-mlx@4bit", 
        "messages": [
            {"role": "user", "content": "안녕하세요. 한국어로 간단한 시를 써주세요."}
        ],
        "stream": True,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            f"{PROXY_URL}/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            stream=True
        )
        
        print(f"Proxy status: {response.status_code}")
        print(f"Proxy headers: {dict(response.headers)}")
        print("Raw proxy response:")
        
        chunk_count = 0
        for line in response.iter_lines(decode_unicode=True):
            chunk_count += 1
            if line and chunk_count <= 10:  # Show first 10 chunks
                print(f"Raw chunk {chunk_count}: {repr(line)}")
                if line.startswith('data: ') and line[6:].strip() != '[DONE]':
                    try:
                        data = json.loads(line[6:])
                        content = data.get('choices', [{}])[0].get('delta', {}).get('content', '')
                        if content:
                            print(f"  Content: {repr(content)} -> {content}")
                    except:
                        pass
            elif chunk_count > 20:
                print("... (truncated)")
                break
                
        print(f"Total chunks: {chunk_count}")
        
    except Exception as e:
        print(f"❌ Raw proxy test failed: {e}")

if __name__ == "__main__":
    test_direct_backend_korean()
    test_proxy_korean()
    test_raw_proxy_korean()
    
    print("\n" + "=" * 50)
    print("Encoding Analysis Complete")
    print("Check the repr() output to see if Korean characters are properly encoded")