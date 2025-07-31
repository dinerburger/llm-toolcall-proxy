#!/usr/bin/env python3
"""
Final test for Korean characters in streaming
"""

from openai import OpenAI

# Test Korean streaming with OpenAI client
client = OpenAI(base_url="http://127.0.0.1:5000", api_key="test")

def test_korean_streaming():
    """Test Korean text streaming"""
    print("한글 스트리밍 최종 테스트")
    print("=" * 50)
    
    try:
        stream_response = client.chat.completions.create(
            model="glm-4.5-air-hi-mlx@4bit",
            messages=[
                {"role": "user", "content": "현재 시간을 알려주세요. 한국어로 답변해주세요."}
            ],
            stream=True,
            temperature=0.7
        )
        
        print("스트리밍 응답:")
        print("-" * 30)
        
        collected_content = ""
        chunk_count = 0
        
        for chunk in stream_response:
            chunk_count += 1
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                collected_content += content
                
                # Check for broken Korean characters
                if '�' in content:
                    print(f"\n❌ 한글 깨짐 발견: {repr(content)}")
                    
            if chunk_count > 100:  # Safety limit
                print("\n[잘림 - 너무 많은 청크]")
                break
        
        print(f"\n\n총 {chunk_count}개 청크, {len(collected_content)}자")
        
        # Check final result
        if '�' in collected_content:
            print("❌ 최종 결과에 한글 깨짐이 있습니다")
            return False
        else:
            print("✅ 한글이 정상적으로 표시됩니다")
            return True
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

if __name__ == "__main__":
    success = test_korean_streaming()
    
    if success:
        print("\n🎉 한글 스트리밍이 완벽하게 작동합니다!")
    else:
        print("\n❌ 한글 스트리밍에 문제가 있습니다.")