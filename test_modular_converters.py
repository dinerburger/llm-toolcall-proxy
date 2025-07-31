#!/usr/bin/env python3
"""
Test the modular converter system
"""

import json
import sys
import time
from typing import Dict, Any

# Add current directory to Python path
sys.path.insert(0, '.')

from converters.factory import converter_factory
from converters.glm import GLMToolCallConverter
from converters.openai import OpenAIToolCallConverter
from converters.claude import ClaudeToolCallConverter
from converters.base import PassThroughConverter

def test_model_detection():
    """Test model detection and converter selection"""
    print("=== Testing Model Detection and Converter Selection ===")
    
    test_cases = [
        ("glm-4.5-air-hi-mlx@4bit", GLMToolCallConverter),
        ("chatglm-6b", GLMToolCallConverter),
        ("custom-glm-model", GLMToolCallConverter),
        ("gpt-4", OpenAIToolCallConverter),
        ("gpt-3.5-turbo", OpenAIToolCallConverter),
        ("claude-3-sonnet", ClaudeToolCallConverter),
        ("claude-2", ClaudeToolCallConverter),
        ("unknown-model", PassThroughConverter),
        ("", PassThroughConverter),
        (None, PassThroughConverter),
    ]
    
    success_count = 0
    for model_name, expected_type in test_cases:
        converter = converter_factory.get_converter(model_name)
        
        if isinstance(converter, expected_type):
            print(f"✅ {model_name or 'None'} -> {expected_type.__name__}")
            success_count += 1
        else:
            print(f"❌ {model_name or 'None'} -> Expected {expected_type.__name__}, got {type(converter).__name__}")
    
    print(f"\nModel Detection: {success_count}/{len(test_cases)} passed")
    return success_count == len(test_cases)

def test_glm_converter():
    """Test GLM converter functionality"""
    print("\n=== Testing GLM Converter ===")
    
    converter = GLMToolCallConverter()
    
    # Test content with GLM tool call
    glm_content = """I'll search for information about that.
<tool_call>fetch_wikipedia_content
<arg_key>search_query</arg_key>
<arg_value>Python programming language</arg_value>
</tool_call>"""
    
    # Test detection methods
    partial_detected = converter.has_partial_tool_call(glm_content)
    complete_detected = converter.is_complete_tool_call(glm_content)
    
    print(f"Partial tool call detected: {partial_detected}")
    print(f"Complete tool call detected: {complete_detected}")
    
    if not (partial_detected and complete_detected):
        print("❌ GLM tool call detection failed")
        return False
    
    # Test parsing
    tool_calls = converter.parse_tool_calls(glm_content)
    print(f"Parsed tool calls: {len(tool_calls)}")
    
    if len(tool_calls) != 1:
        print("❌ GLM tool call parsing failed")
        return False
    
    tool_call = tool_calls[0]
    if (tool_call['function']['name'] != 'fetch_wikipedia_content' or
        '"search_query": "Python programming language"' not in tool_call['function']['arguments']):
        print("❌ GLM tool call parsing incorrect")
        print(f"Got: {tool_call}")
        return False
    
    # Test content cleaning
    clean_content = converter._clean_content(glm_content)
    if '<tool_call>' in clean_content:
        print("❌ GLM content cleaning failed")
        return False
    
    print(f"Cleaned content: '{clean_content}'")
    print("✅ GLM converter tests passed")
    return True

def test_response_conversion():
    """Test response conversion with different models"""
    print("\n=== Testing Response Conversion ===")
    
    # Test GLM response conversion
    glm_response = {
        "id": "test-123",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "glm-4.5-air-hi-mlx@4bit",
        "choices": [
            {
                "index": 0,
                "logprobs": None,
                "finish_reason": "stop",
                "message": {
                    "role": "assistant",
                    "content": "I'll help with that.\n<tool_call>search_function\n<arg_key>query</arg_key>\n<arg_value>test query</arg_value>\n</tool_call>"
                }
            }
        ]
    }
    
    # Get GLM converter and test conversion
    glm_converter = converter_factory.get_converter("glm-4.5-air-hi-mlx@4bit")
    converted_glm = glm_converter.convert_response(glm_response)
    
    # Check if conversion worked
    message = converted_glm['choices'][0]['message']
    if 'tool_calls' not in message or len(message['tool_calls']) == 0:
        print("❌ GLM response conversion failed")
        return False
    
    if converted_glm['choices'][0]['finish_reason'] != 'tool_calls':
        print("❌ GLM finish_reason not updated")
        return False
    
    print("✅ GLM response conversion successful")
    
    # Test OpenAI response (should pass through)
    openai_response = {
        "id": "test-456",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Hello! How can I help?"
                },
                "finish_reason": "stop"
            }
        ]
    }
    
    openai_converter = converter_factory.get_converter("gpt-4")
    converted_openai = openai_converter.convert_response(openai_response)
    
    # Should be unchanged
    if converted_openai != openai_response:
        print("❌ OpenAI response should pass through unchanged")
        return False
    
    print("✅ OpenAI response pass-through successful")
    return True

def test_streaming_handlers():
    """Test streaming handler selection"""
    print("\n=== Testing Streaming Handler Selection ===")
    
    # Test GLM streaming handler
    glm_handler = converter_factory.get_streaming_handler("glm-4.5-air-hi-mlx")
    if not hasattr(glm_handler, 'process_chunk'):
        print("❌ GLM streaming handler missing process_chunk method")
        return False
    
    # Test generic streaming handler for other models
    openai_handler = converter_factory.get_streaming_handler("gpt-4")
    if not hasattr(openai_handler, 'process_chunk'):
        print("❌ OpenAI streaming handler missing process_chunk method")
        return False
    
    print("✅ Streaming handler selection working")
    return True

def test_factory_methods():
    """Test factory utility methods"""
    print("\n=== Testing Factory Utility Methods ===")
    
    # Test model detection from response
    response_with_model = {"model": "glm-4.5-air-hi-mlx@4bit"}
    detected = converter_factory.detect_model_from_response(response_with_model)
    if detected != "glm-4.5-air-hi-mlx@4bit":
        print(f"❌ Model detection from response failed: {detected}")
        return False
    
    # Test model detection from request
    request_with_model = {"model": "gpt-4"}
    detected = converter_factory.detect_model_from_request(request_with_model)
    if detected != "gpt-4":
        print(f"❌ Model detection from request failed: {detected}")
        return False
    
    # Test supported models listing
    supported = converter_factory.list_supported_models()
    if not any('glm' in pattern.lower() for pattern in supported):
        print("❌ Supported models list missing GLM patterns")
        return False
    
    print("✅ Factory utility methods working")
    return True

def test_converter_registration():
    """Test dynamic converter registration"""
    print("\n=== Testing Dynamic Converter Registration ===")
    
    class TestConverter(PassThroughConverter):
        def can_handle_model(self, model_name: str) -> bool:
            return model_name == "test-model"
    
    # Register new converter
    test_converter = TestConverter()
    converter_factory.register_converter(test_converter)
    
    # Test if it's used
    selected = converter_factory.get_converter("test-model")
    if not isinstance(selected, TestConverter):
        print("❌ Dynamic converter registration failed")
        return False
    
    print("✅ Dynamic converter registration working")
    return True

def main():
    print("Testing Modular Tool Call Converter System")
    print("=" * 50)
    
    tests = [
        ("Model Detection", test_model_detection),
        ("GLM Converter", test_glm_converter),
        ("Response Conversion", test_response_conversion),
        ("Streaming Handlers", test_streaming_handlers),
        ("Factory Methods", test_factory_methods),
        ("Converter Registration", test_converter_registration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Modular converter system is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Check the implementation.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)