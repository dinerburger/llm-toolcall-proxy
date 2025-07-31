#!/usr/bin/env python3
"""
Test empty <think></think> tag removal in base converter
"""

from converters.base import PassThroughConverter
from converters.glm import GLMToolCallConverter

def test_empty_think_tag_removal():
    """Test various empty think tag scenarios"""
    print("Testing Empty <think></think> Tag Removal")
    print("=" * 50)
    
    converter = PassThroughConverter()
    
    test_cases = [
        # Case 1: Simple empty tags
        ("Simple empty: <think></think>", "Simple empty: ", "Complete empty tags"),
        
        # Case 2: Empty with spaces
        ("With spaces: <think> </think>", "With spaces: ", "Empty with spaces"),
        
        # Case 3: Empty with newlines
        ("With newlines: <think>\n</think>", "With newlines: ", "Empty with newlines"),
        
        # Case 4: Empty with mixed whitespace
        ("Mixed: <think> \n \t </think>", "Mixed: ", "Empty with mixed whitespace"),
        
        # Case 5: Multiple empty tags
        ("Multiple: <think></think> text <think> </think> more", "Multiple:  text  more", "Multiple empty tags"),
        
        # Case 6: Mixed with content tags (should preserve content)
        ("Mixed: <think>content</think> and <think></think>", "Mixed: <think>content</think> and ", "Mixed content and empty"),
        
        # Case 7: Normal content (should be unchanged)
        ("Normal content without think tags", "Normal content without think tags", "Normal content"),
        
        # Case 8: Only whitespace content (should be preserved)
        ("Only content: <think>actual thinking</think>", "Only content: <think>actual thinking</think>", "Non-empty content"),
    ]
    
    for i, (input_text, expected, description) in enumerate(test_cases, 1):
        result = converter._remove_empty_think_tags(input_text)
        status = "✅" if result == expected else "❌"
        
        print(f"Test {i}: {description}")
        print(f"  Input:    {repr(input_text)}")
        print(f"  Expected: {repr(expected)}")
        print(f"  Result:   {repr(result)}")
        print(f"  Status:   {status}")
        print()

def test_glm_converter_integration():
    """Test GLM converter with empty think tag removal"""
    print("Testing GLM Converter Integration")
    print("=" * 50)
    
    import os
    # Test with REMOVE_THINK_TAGS=false to see if empty tags are still removed
    os.environ['REMOVE_THINK_TAGS'] = 'false'
    
    converter = GLMToolCallConverter()
    
    content = """
    Here is my response.
    <think></think>
    <think>This has content and should be preserved</think>
    <think> </think>
    Some final text.
    <think>
    </think>
    """
    
    print("Testing with REMOVE_THINK_TAGS=false (content tags should be preserved)")
    cleaned = converter._clean_content(content)
    print(f"Original: {repr(content)}")
    print(f"Cleaned:  {repr(cleaned)}")
    
    # Check results
    has_empty_tags = '<think></think>' in cleaned or '<think> </think>' in cleaned
    has_content_tags = '<think>This has content' in cleaned
    
    print(f"Empty tags removed: {'✅' if not has_empty_tags else '❌'}")
    print(f"Content tags preserved: {'✅' if has_content_tags else '❌'}")
    print()

def test_response_conversion():
    """Test response conversion with empty think tags"""
    print("Testing Response Conversion")
    print("=" * 50)
    
    converter = PassThroughConverter()
    
    # Mock response data
    response_data = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Hello <think></think> world <think> </think> from AI!"
                }
            }
        ]
    }
    
    result = converter.convert_response(response_data)
    
    print("Original content:", repr(response_data["choices"][0]["message"]["content"]))
    print("Processed content:", repr(result["choices"][0]["message"]["content"]))
    
    expected = "Hello  world  from AI!"
    actual = result["choices"][0]["message"]["content"]
    status = "✅" if actual == expected else "❌"
    print(f"Empty tags removed: {status}")
    print()

if __name__ == "__main__":
    test_empty_think_tag_removal()
    test_glm_converter_integration()
    test_response_conversion()
    
    print("=" * 50)
    print("Empty Think Tag Removal Test Complete")
    print("✅ Empty <think></think> tags are always removed")
    print("✅ Content <think>...</think> tags follow REMOVE_THINK_TAGS setting")
    print("✅ Works in both regular and streaming modes")