#!/usr/bin/env python3
"""
Test new GLM tool calling formats with debugging
"""

from converters.glm import GLMToolCallConverter

def test_new_format():
    """Test new [TOOL_REQUEST] format"""
    print("Testing New [TOOL_REQUEST] Format")
    print("=" * 50)
    
    converter = GLMToolCallConverter()
    
    # Test case 1: Single parameter
    content1 = '''
[TOOL_REQUEST]
{"name": "fetch_wikipedia_content", "arguments": {"search_query":"Namsan Seoul historical buildings"}}
[END_TOOL_REQUEST]
    '''
    
    print("Test 1: New format single parameter")
    tool_calls = converter.parse_tool_calls(content1)
    print(f"Result: {len(tool_calls)} tool calls")
    print()
    
    # Test case 2: Multiple parameters
    content2 = '''
[TOOL_REQUEST]
{"name": "search_function", "arguments": {"query":"test query", "limit":10, "category":"books"}}
[END_TOOL_REQUEST]
    '''
    
    print("Test 2: New format multiple parameters")
    tool_calls = converter.parse_tool_calls(content2)
    print(f"Result: {len(tool_calls)} tool calls")
    print()

def test_legacy_multi_param():
    """Test legacy format with multiple parameters"""
    print("Testing Legacy Multi-Parameter Format")
    print("=" * 50)
    
    converter = GLMToolCallConverter()
    
    # Test case: Multiple arg_key/arg_value pairs
    content = '''
<tool_call>
search_function
<arg_key>query</arg_key>
<arg_value>test search</arg_value>
<arg_key>limit</arg_key>
<arg_value>5</arg_value>
<arg_key>category</arg_key>
<arg_value>science</arg_value>
</tool_call>
    '''
    
    print("Test: Legacy format multiple parameters")
    tool_calls = converter.parse_tool_calls(content)
    print(f"Result: {len(tool_calls)} tool calls")
    print()

def test_multiline_json():
    """Test multiline JSON in new format"""
    print("Testing Multiline JSON Format")
    print("=" * 50)
    
    converter = GLMToolCallConverter()
    
    # Test case: Multiline JSON (common cause of parsing errors)
    content = '''
[TOOL_REQUEST]
{
  "name": "fetch_wikipedia_content", 
  "arguments": {
    "search_query": "Seoul historical buildings",
    "language": "en",
    "limit": 3
  }
}
[END_TOOL_REQUEST]
    '''
    
    print("Test: Multiline JSON format")
    tool_calls = converter.parse_tool_calls(content)
    print(f"Result: {len(tool_calls)} tool calls")
    print()

def test_mixed_formats():
    """Test content with both formats"""
    print("Testing Mixed Formats")
    print("=" * 50)
    
    converter = GLMToolCallConverter()
    
    content = '''
First, I need to search for information.

[TOOL_REQUEST]
{"name": "search_info", "arguments": {"query": "test"}}
[END_TOOL_REQUEST]

Now let me use the legacy format too:

<tool_call>
legacy_function
<arg_key>param1</arg_key>
<arg_value>value1</arg_value>
</tool_call>
    '''
    
    print("Test: Mixed formats in same content")
    tool_calls = converter.parse_tool_calls(content)
    print(f"Result: {len(tool_calls)} tool calls")
    print()

if __name__ == "__main__":
    test_new_format()
    test_legacy_multi_param() 
    test_multiline_json()
    test_mixed_formats()
    
    print("=" * 50)
    print("GLM Format Testing Complete")
    print("Check debug output above for detailed parsing information")