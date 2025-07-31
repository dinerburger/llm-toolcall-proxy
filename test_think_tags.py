#!/usr/bin/env python3
"""
Test <think> tag cleaning functionality
"""

from converters.glm import GLMToolCallConverter

def test_think_tag_cleaning():
    """Test various think tag scenarios"""
    print("Testing <think> Tag Cleaning")
    print("=" * 50)
    
    converter = GLMToolCallConverter()
    
    # Test case 1: Complete think pairs (should be removed)
    content1 = """
    Here is my response.
    <think>
    I need to think about this carefully.
    This is internal thinking.
    </think>
    And here is the final answer.
    """
    
    print("Test 1: Complete <think>...</think> pairs")
    cleaned1 = converter._clean_content(content1)
    print(f"Original: {repr(content1)}")
    print(f"Cleaned: {repr(cleaned1)}")
    print(f"Contains <think>: {'<think>' in cleaned1}")
    print(f"Contains </think>: {'</think>' in cleaned1}")
    print()
    
    # Test case 2: Orphaned closing tag (should be removed)
    content2 = """
    Here is my response.
    Some content here.
    </think>
    And here is more content.
    """
    
    print("Test 2: Orphaned </think> tag")
    cleaned2 = converter._clean_content(content2)
    print(f"Original: {repr(content2)}")
    print(f"Cleaned: {repr(cleaned2)}")
    print(f"Contains </think>: {'</think>' in cleaned2}")
    print()
    
    # Test case 3: Orphaned opening tag (should be removed)
    content3 = """
    Here is my response.
    <think>
    This thinking never ends...
    And here is more content.
    """
    
    print("Test 3: Orphaned <think> tag")
    cleaned3 = converter._clean_content(content3)
    print(f"Original: {repr(content3)}")
    print(f"Cleaned: {repr(cleaned3)}")
    print(f"Contains <think>: {'<think>' in cleaned3}")
    print()
    
    # Test case 4: Multiple orphaned closing tags
    content4 = """
    Here is content.
    </think>
    More content.
    </think>
    Final content.
    """
    
    print("Test 4: Multiple orphaned </think> tags")
    cleaned4 = converter._clean_content(content4)
    print(f"Original: {repr(content4)}")
    print(f"Cleaned: {repr(cleaned4)}")
    print(f"Contains </think>: {'</think>' in cleaned4}")
    print()
    
    # Test case 5: Mixed with tool calls
    content5 = """
    I need to search for information.
    </think>
    
    [TOOL_REQUEST]
    {"name": "search", "arguments": {"query": "test"}}
    [END_TOOL_REQUEST]
    
    <think>
    Now I'll process the results.
    """
    
    print("Test 5: Think tags mixed with tool calls")
    cleaned5 = converter._clean_content(content5)
    print(f"Original: {repr(content5)}")
    print(f"Cleaned: {repr(cleaned5)}")
    print(f"Contains <think>: {'<think>' in cleaned5}")
    print(f"Contains </think>: {'</think>' in cleaned5}")
    print(f"Contains TOOL_REQUEST: {'TOOL_REQUEST' in cleaned5}")
    print()
    
    # Test case 6: Normal content (should remain unchanged)
    content6 = """
    This is normal content without any think tags.
    Just regular text that should remain unchanged.
    """
    
    print("Test 6: Normal content (no think tags)")
    cleaned6 = converter._clean_content(content6)
    print(f"Original: {repr(content6)}")
    print(f"Cleaned: {repr(cleaned6)}")
    print(f"Content preserved: {content6.strip() == cleaned6}")
    print()

if __name__ == "__main__":
    test_think_tag_cleaning()
    
    print("=" * 50)
    print("Think Tag Cleaning Test Complete")
    print("Check debug output above for orphaned tag removal")