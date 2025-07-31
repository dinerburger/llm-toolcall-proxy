#!/usr/bin/env python3

import re

# Original GLM format from your example
content = """
I'll fetch information about Kyungju (경주) city and explain it in Korean as requested.
<tool_call>fetch_wikipedia_content
<arg_key>search_query</arg_key>
<arg_value>Kyungju Korea</arg_value>
</tool_call>"""

print("Content:")
print(repr(content))

# Test different regex patterns
patterns = [
    r'<tool_call>(.*?)<arg_key>(.*?)</arg_key><arg_value>(.*?)</arg_value></tool_call>',
    r'<tool_call>\s*(.*?)\s*<arg_key>\s*(.*?)\s*</arg_key>\s*<arg_value>\s*(.*?)\s*</arg_value>\s*</tool_call>',
    r'<tool_call>\s*([^\n<]+)\s*<arg_key>\s*([^\n<]+)\s*</arg_key>\s*<arg_value>\s*([^\n<]+)\s*</arg_value>\s*</tool_call>',
]

for i, pattern in enumerate(patterns):
    print(f"\nPattern {i+1}: {pattern}")
    matches = re.findall(pattern, content, re.DOTALL)
    print(f"Matches: {len(matches)}")
    for match in matches:
        print(f"  Function: '{match[0].strip()}'")
        print(f"  Key: '{match[1].strip()}'")
        print(f"  Value: '{match[2].strip()}'")

# Test with simpler content
simple_content = "<tool_call>fetch_wikipedia_content\n<arg_key>search_query</arg_key>\n<arg_value>Kyungju Korea</arg_value>\n</tool_call>"
print(f"\nSimple content: {repr(simple_content)}")

pattern = r'<tool_call>\s*(.*?)\s*<arg_key>\s*(.*?)\s*</arg_key>\s*<arg_value>\s*(.*?)\s*</arg_value>\s*</tool_call>'
matches = re.findall(pattern, simple_content, re.DOTALL)
print(f"Simple matches: {len(matches)}")
for match in matches:
    print(f"  Function: '{match[0].strip()}'")
    print(f"  Key: '{match[1].strip()}'")
    print(f"  Value: '{match[2].strip()}'")