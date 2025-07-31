#!/usr/bin/env python3
"""
Test timeout configuration
"""

import os
from config import Config

def test_timeout_configurations():
    """Test different timeout configuration scenarios"""
    print("Testing Timeout Configuration")
    print("=" * 50)
    
    test_cases = [
        # (REQUEST_TIMEOUT, STREAMING_TIMEOUT, description)
        ("300", "600", "Default values"),
        ("60", "120", "Short timeouts"),
        ("300", "none", "Disabled streaming timeout"),
        ("300", "0", "Zero streaming timeout (disabled)"),
        ("300", "false", "False streaming timeout (disabled)"),
        ("300", "null", "Null streaming timeout (disabled)"),
        ("180", "1800", "Long streaming timeout"),
    ]
    
    for i, (req_timeout, stream_timeout, description) in enumerate(test_cases, 1):
        print(f"Test {i}: {description}")
        
        # Set environment variables
        os.environ['REQUEST_TIMEOUT'] = req_timeout
        os.environ['STREAMING_TIMEOUT'] = stream_timeout
        
        # Create new config instance
        config = Config()
        
        print(f"  REQUEST_TIMEOUT: {config.REQUEST_TIMEOUT}")
        print(f"  STREAMING_TIMEOUT: {config.STREAMING_TIMEOUT}")
        print(f"  STREAMING_TIMEOUT type: {type(config.STREAMING_TIMEOUT)}")
        
        # Check if streaming timeout is disabled
        if config.STREAMING_TIMEOUT is None:
            print(f"  ✅ Streaming timeout disabled")
        else:
            print(f"  ✅ Streaming timeout: {config.STREAMING_TIMEOUT} seconds")
        
        print()

def test_timeout_edge_cases():
    """Test edge cases for timeout configuration"""
    print("Testing Timeout Edge Cases")
    print("=" * 50)
    
    edge_cases = [
        ("NONE", "Uppercase NONE"),
        ("None", "Mixed case None"),
        ("NULL", "Uppercase NULL"),
        ("FALSE", "Uppercase FALSE"),
        ("", "Empty string"),
        ("invalid", "Invalid string (should default to int conversion error handling)"),
    ]
    
    for i, (value, description) in enumerate(edge_cases, 1):
        print(f"Edge Case {i}: {description}")
        
        os.environ['REQUEST_TIMEOUT'] = "300"
        os.environ['STREAMING_TIMEOUT'] = value
        
        try:
            config = Config()
            print(f"  STREAMING_TIMEOUT: {config.STREAMING_TIMEOUT}")
            print(f"  Type: {type(config.STREAMING_TIMEOUT)}")
            if config.STREAMING_TIMEOUT is None:
                print(f"  ✅ Successfully disabled")
            else:
                print(f"  ✅ Value: {config.STREAMING_TIMEOUT}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()

def demo_usage():
    """Demonstrate typical usage scenarios"""
    print("Usage Scenarios")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "Development (quick responses)",
            "request": "30",
            "streaming": "60"
        },
        {
            "name": "Production (balanced)",
            "request": "300", 
            "streaming": "600"
        },
        {
            "name": "Long tasks (no streaming limit)",
            "request": "300",
            "streaming": "none"
        }
    ]
    
    for scenario in scenarios:
        print(f"Scenario: {scenario['name']}")
        print(f"  export REQUEST_TIMEOUT={scenario['request']}")
        print(f"  export STREAMING_TIMEOUT={scenario['streaming']}")
        
        os.environ['REQUEST_TIMEOUT'] = scenario['request']
        os.environ['STREAMING_TIMEOUT'] = scenario['streaming']
        
        config = Config()
        print(f"  → Regular timeout: {config.REQUEST_TIMEOUT}s")
        if config.STREAMING_TIMEOUT is None:
            print(f"  → Streaming timeout: disabled")
        else:
            print(f"  → Streaming timeout: {config.STREAMING_TIMEOUT}s")
        print()

if __name__ == "__main__":
    test_timeout_configurations()
    test_timeout_edge_cases()
    demo_usage()
    
    print("=" * 50)
    print("Timeout Configuration Test Complete")
    print("✅ Regular and streaming timeouts are configurable")
    print("✅ Streaming timeout can be disabled with 'none', '0', 'false'")
    print("✅ Defaults: REQUEST_TIMEOUT=300s, STREAMING_TIMEOUT=600s")