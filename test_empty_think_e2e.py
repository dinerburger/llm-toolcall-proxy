#!/usr/bin/env python3
"""
End-to-end test for empty think tag removal
"""

import json
import requests

PROXY_URL = "http://127.0.0.1:5000"

def test_empty_think_tags_e2e():
    """Test empty think tag removal through proxy"""
    print("End-to-End Empty Think Tag Test")
    print("=" * 50)
    
    # Simulate a response that might come from GLM with empty think tags
    test_cases = [
        {
            "name": "Empty think tags only",
            "messages": [{"role": "user", "content": "Say hello with empty think tags: <think></think> Hello <think> </think> world!"}],
            "expected_pattern": "Hello  world!"
        },
        {
            "name": "Mixed empty and content think tags", 
            "messages": [{"role": "user", "content": "Response: <think>I should think</think> Answer <think></think> here."}],
            "expected_pattern": "Answer  here."  # Content tags behavior depends on REMOVE_THINK_TAGS
        },
        {
            "name": "Multiple empty variations",
            "messages": [{"role": "user", "content": "Test: <think></think><think> </think><think>\n</think> Done."}],
            "expected_pattern": " Done."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        
        payload = {
            "model": "glm-4.5-air-hi-mlx@4bit",
            "messages": test_case["messages"],
            "stream": False,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(
                f"{PROXY_URL}/v1/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                print(f"  Input:  {repr(test_case['messages'][0]['content'])}")
                print(f"  Output: {repr(content)}")
                
                # Check if empty think tags were removed
                has_empty_tags = '<think></think>' in content or '<think> </think>' in content
                print(f"  Empty tags removed: {'✅' if not has_empty_tags else '❌'}")
                
            else:
                print(f"  ❌ Request failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()

def test_streaming_empty_think_tags():
    """Test empty think tag removal in streaming mode"""
    print("Streaming Empty Think Tag Test")
    print("=" * 50)
    
    payload = {
        "model": "glm-4.5-air-hi-mlx@4bit",
        "messages": [
            {"role": "user", "content": "Please respond with: Hello <think></think> world <think> </think> from streaming!"}
        ],
        "stream": True,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(
            f"{PROXY_URL}/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=30
        )
        
        if response.status_code == 200:
            print("Streaming response:")
            
            collected_content = ""
            for line in response.iter_lines(decode_unicode=True):
                if line and line.startswith('data: ') and line[6:].strip() != '[DONE]':
                    try:
                        chunk_data = json.loads(line[6:])
                        delta_content = chunk_data.get('choices', [{}])[0].get('delta', {}).get('content', '')
                        if delta_content:
                            collected_content += delta_content
                            print(delta_content, end='', flush=True)
                    except json.JSONDecodeError:
                        pass
            
            print(f"\n\nFinal content: {repr(collected_content)}")
            
            # Check if empty think tags were removed from streaming
            has_empty_tags = '<think></think>' in collected_content or '<think> </think>' in collected_content
            print(f"Empty tags removed from streaming: {'✅' if not has_empty_tags else '❌'}")
            
        else:
            print(f"❌ Streaming request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Streaming error: {e}")

if __name__ == "__main__":
    print("Make sure the proxy server is running on port 5000...")
    print()
    
    test_empty_think_tags_e2e()
    test_streaming_empty_think_tags()
    
    print("=" * 50)
    print("End-to-End Test Complete")
    print("Empty <think></think> tags should be removed in all modes")