#!/usr/bin/env python3
"""
Non-interactive test version of lmstudio-tooluse-test.py
"""

import json
import shutil
from openai import OpenAI

# Initialize client (using proxy server)
client = OpenAI(base_url="http://127.0.0.1:5000", api_key="lm-studio")
MODEL = "glm-4.5-air-hi-mlx@4bit"

def fetch_wikipedia_content(search_query: str) -> dict:
    """Fetches wikipedia content for a given search_query"""
    try:
        import urllib.parse
        import urllib.request
        
        # Search for most relevant article
        search_url = "https://en.wikipedia.org/w/api.php"
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": search_query,
            "srlimit": 1,
        }

        url = f"{search_url}?{urllib.parse.urlencode(search_params)}"
        with urllib.request.urlopen(url) as response:
            search_data = json.loads(response.read().decode())

        if not search_data["query"]["search"]:
            return {
                "status": "error",
                "message": f"No Wikipedia article found for '{search_query}'",
            }

        # Get the normalized title from search results
        normalized_title = search_data["query"]["search"][0]["title"]

        # Now fetch the actual content with the normalized title
        content_params = {
            "action": "query",
            "format": "json",
            "titles": normalized_title,
            "prop": "extracts",
            "exintro": "true",
            "explaintext": "true",
            "redirects": 1,
        }

        url = f"{search_url}?{urllib.parse.urlencode(content_params)}"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())

        pages = data["query"]["pages"]
        page_id = list(pages.keys())[0]

        if page_id == "-1":
            return {
                "status": "error",
                "message": f"No Wikipedia article found for '{search_query}'",
            }

        content = pages[page_id]["extract"].strip()
        return {
            "status": "success",
            "content": content,
            "title": pages[page_id]["title"],
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

# Define tool for LM Studio
WIKI_TOOL = {
    "type": "function",
    "function": {
        "name": "fetch_wikipedia_content",
        "description": (
            "Search Wikipedia and fetch the introduction of the most relevant article. "
            "Always use this if the user is asking for something that is likely on wikipedia. "
            "If the user has a typo in their search query, correct it before searching."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "search_query": {
                    "type": "string",
                    "description": "Search query for finding the Wikipedia article",
                },
            },
            "required": ["search_query"],
        },
    },
}

def test_query(user_input: str):
    """Test a single query"""
    print(f"\n=== Testing Query: '{user_input}' ===")
    
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that can retrieve Wikipedia articles. "
                "When asked about a topic, you can retrieve Wikipedia articles "
                "and cite information from them."
            ),
        },
        {"role": "user", "content": user_input}
    ]

    try:
        print("Sending request to proxy server...")
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=[WIKI_TOOL],
        )

        print(f"Response received. Content: {response.choices[0].message.content}")
        print(f"Tool calls: {bool(response.choices[0].message.tool_calls)}")

        if response.choices[0].message.tool_calls:
            print("✅ Tool calls detected!")
            
            # Handle all tool calls
            tool_calls = response.choices[0].message.tool_calls

            # Add all tool calls to messages
            messages.append(
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": tool_call.type,
                            "function": tool_call.function,
                        }
                        for tool_call in tool_calls
                    ],
                }
            )

            # Process each tool call and add results
            for tool_call in tool_calls:
                args = json.loads(tool_call.function.arguments)
                result = fetch_wikipedia_content(args["search_query"])

                # Print the Wikipedia content in a formatted way
                terminal_width = min(shutil.get_terminal_size().columns, 80)
                print("\n" + "=" * terminal_width)
                if result["status"] == "success":
                    print(f"\nWikipedia article: {result['title']}")
                    print("-" * terminal_width)
                    # Truncate content for readability
                    content = result["content"]
                    if len(content) > 500:
                        content = content[:500] + "..."
                    print(content)
                else:
                    print(f"\nError fetching Wikipedia content: {result['message']}")
                print("=" * terminal_width)

                messages.append(
                    {
                        "role": "tool",
                        "content": json.dumps(result),
                        "tool_call_id": tool_call.id,
                    }
                )

            # Get the post-tool-call response
            print("\nGetting final response...")
            final_response = client.chat.completions.create(
                model=MODEL, 
                messages=messages
            )
            print(f"\nFinal Assistant Response:")
            print(final_response.choices[0].message.content)
            
            return True
        else:
            print("❌ No tool calls detected")
            print(f"Regular response: {response.choices[0].message.content}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("Testing LM Studio Tool Use with Proxy Server")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        "tell me about lee jae myung",
        "search for information about Python programming",
        "what is machine learning?",
    ]
    
    results = []
    for query in test_queries:
        success = test_query(query)
        results.append((query, success))
        print("\n" + "-" * 50)
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    for query, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{query}: {status}")
    
    successful = sum(1 for _, success in results if success)
    print(f"\nOverall: {successful}/{len(results)} tests passed")
    
    if successful == len(results):
        print("🎉 All tests passed! Tool call system is working correctly.")
    else:
        print("❌ Some tests failed. Check the implementation.")

if __name__ == "__main__":
    main()