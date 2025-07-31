#!/usr/bin/env python3
"""
Test <think> tag cleaning with environment variable control
"""

import os
from converters.glm import GLMToolCallConverter

def test_with_remove_enabled():
    """Test with REMOVE_THINK_TAGS=true (default)"""
    print("Testing with REMOVE_THINK_TAGS=true (default)")
    print("=" * 50)
    
    # Ensure environment variable is set to true
    os.environ['REMOVE_THINK_TAGS'] = 'true'
    
    converter = GLMToolCallConverter()
    
    content = """
    Here is my response.
    <think>
    I need to think about this carefully.
    This should be removed when enabled.
    </think>
    And here is the final answer.
    Some content </think> here.
    """
    
    cleaned = converter._clean_content(content)
    print(f"Original: {repr(content)}")
    print(f"Cleaned: {repr(cleaned)}")
    print(f"Contains complete think tags: {'<think>' in cleaned and '</think>' in cleaned}")
    print(f"Contains orphaned closing tags: {'</think>' in cleaned}")
    print()

def test_with_remove_disabled():
    """Test with REMOVE_THINK_TAGS=false"""
    print("Testing with REMOVE_THINK_TAGS=false")
    print("=" * 50)
    
    # Set environment variable to false
    os.environ['REMOVE_THINK_TAGS'] = 'false'
    
    # Create new converter instance to pick up new config
    converter = GLMToolCallConverter()
    
    content = """
    Here is my response.
    <think>
    I need to think about this carefully.
    This should be kept when disabled.
    </think>
    And here is the final answer.
    Some content </think> here.
    """
    
    cleaned = converter._clean_content(content)
    print(f"Original: {repr(content)}")
    print(f"Cleaned: {repr(cleaned)}")
    print(f"Contains complete think content: {'I need to think about this carefully.' in cleaned}")
    print(f"Contains orphaned closing tags: {'</think>' in cleaned}")
    print()

def test_mixed_scenario():
    """Test mixed scenario with tool calls and think tags"""
    print("Testing mixed scenario (REMOVE_THINK_TAGS=false)")
    print("=" * 50)
    
    os.environ['REMOVE_THINK_TAGS'] = 'false'
    converter = GLMToolCallConverter()
    
    content = """
    I need to search for information.
    <think>
    This is my internal reasoning.
    I should search for Lee Jae-myung.
    </think>
    
    [TOOL_REQUEST]
    {"name": "search", "arguments": {"query": "Lee Jae-myung"}}
    [END_TOOL_REQUEST]
    
    Some orphaned tag </think> here.
    """
    
    cleaned = converter._clean_content(content)
    print(f"Original: {repr(content)}")
    print(f"Cleaned: {repr(cleaned)}")
    print(f"Contains tool request: {'TOOL_REQUEST' in cleaned}")
    print(f"Contains complete think content: {'internal reasoning' in cleaned}")
    print(f"Contains orphaned closing tags: {'</think>' in cleaned}")
    print()

def test_env_var_variations():
    """Test different environment variable values"""
    print("Testing Environment Variable Variations")
    print("=" * 50)
    
    test_values = ['true', 'True', 'TRUE', 'false', 'False', 'FALSE', '1', '0', 'yes', 'no']
    
    content = """
    Response with <think>internal thinking</think> here.
    """
    
    for value in test_values:
        os.environ['REMOVE_THINK_TAGS'] = value
        converter = GLMToolCallConverter()
        cleaned = converter._clean_content(content)
        
        think_removed = 'internal thinking' not in cleaned
        print(f"REMOVE_THINK_TAGS='{value}' -> Think tags removed: {think_removed}")
    
    print()

if __name__ == "__main__":
    test_with_remove_enabled()
    test_with_remove_disabled()
    test_mixed_scenario()
    test_env_var_variations()
    
    print("=" * 50)
    print("Environment Variable Configuration Test Complete")
    print("Set REMOVE_THINK_TAGS=false to preserve complete <think> tags")
    print("Set REMOVE_THINK_TAGS=true to remove complete <think> tags (default)")