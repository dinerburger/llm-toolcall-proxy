#!/usr/bin/env python3
"""
Test lmstudio-tooluse-test.py with streaming support
"""

import time
from openai import OpenAI

def test_streaming_with_tools():
    """Test streaming chat with tool calls through proxy"""
    print("Testing OpenAI Client Streaming with Tools")
    print("=" * 45)
    
    client = OpenAI(base_url="http://127.0.0.1:5000", api_key="lm-studio")
    
    # Test streaming with tools
    try:
        print("Making streaming request with tools...")
        
        response = client.chat.completions.create(
            model="glm-4.5-air-hi-mlx",
            messages=[
                {"role": "user", "content": "Tell me about artificial intelligence"}
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
            ],
            stream=True
        )
        
        print("Streaming response:")
        chunks_received = 0
        content_parts = []
        tool_calls_found = []
        
        for chunk in response:
            chunks_received += 1
            
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                content_parts.append(content)
                print(content, end="", flush=True)
            
            if hasattr(chunk.choices[0].delta, 'tool_calls') and chunk.choices[0].delta.tool_calls:
                tool_calls_found.extend(chunk.choices[0].delta.tool_calls)
                print(f"\n[Tool calls detected: {len(chunk.choices[0].delta.tool_calls)}]")
                for tool_call in chunk.choices[0].delta.tool_calls:
                    print(f"  Function: {tool_call.function.name}")
                    print(f"  Arguments: {tool_call.function.arguments}")
            
            if chunk.choices[0].finish_reason:
                print(f"\n[Finished: {chunk.choices[0].finish_reason}]")
        
        print(f"\n\nSummary:")
        print(f"Chunks received: {chunks_received}")
        print(f"Content length: {len(''.join(content_parts))}")
        print(f"Tool calls found: {len(tool_calls_found)}")
        
        if tool_calls_found:
            print("✅ SUCCESS: Streaming tool calls working with OpenAI client!")
            return True
        else:
            print("❌ FAILED: No tool calls detected")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_streaming_normal():
    """Test streaming without tools"""
    print("\n" + "=" * 45)
    print("Testing OpenAI Client Streaming (Normal)")
    print("=" * 45)
    
    client = OpenAI(base_url="http://127.0.0.1:5000", api_key="lm-studio")
    
    try:
        print("Making streaming request without tools...")
        
        response = client.chat.completions.create(
            model="glm-4.5-air-hi-mlx",
            messages=[
                {"role": "user", "content": "Write a short poem about coding"}
            ],
            stream=True
        )
        
        print("Streaming response:")
        chunks_received = 0
        content_parts = []
        
        for chunk in response:
            chunks_received += 1
            
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                content_parts.append(content)
                print(content, end="", flush=True)
            
            if chunk.choices[0].finish_reason:
                print(f"\n[Finished: {chunk.choices[0].finish_reason}]")
        
        full_content = ''.join(content_parts)
        
        print(f"\n\nSummary:")
        print(f"Chunks received: {chunks_received}")
        print(f"Content length: {len(full_content)}")
        
        if chunks_received > 0 and full_content:
            print("✅ SUCCESS: Normal streaming working!")
            return True
        else:
            print("❌ FAILED: No content received")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("OpenAI Client Streaming Test with Proxy")
    print("=" * 50)
    print("Make sure:")
    print("- Proxy server is running (python app.py)")
    print("- LM Studio is running on port 8888")
    print("- GLM model is loaded")
    print()
    
    # Test streaming with tools
    streaming_tools_ok = test_streaming_with_tools()
    
    # Test streaming without tools  
    streaming_normal_ok = test_streaming_normal()
    
    print("\n" + "=" * 50)
    print("Final Results:")
    print(f"Streaming with Tools: {'✅ PASS' if streaming_tools_ok else '❌ FAIL'}")
    print(f"Streaming Normal: {'✅ PASS' if streaming_normal_ok else '❌ FAIL'}")
    
    if streaming_tools_ok and streaming_normal_ok:
        print("\n🎉 All streaming tests passed!")
        print("lmstudio-tooluse-test.py should work perfectly with streaming!")
    else:
        print("\n❌ Some streaming tests failed.")

if __name__ == '__main__':
    main()