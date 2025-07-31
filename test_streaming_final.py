#!/usr/bin/env python3
"""
Final streaming test - exact scenario from lmstudio-tooluse-test.py
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
            "content": content[:500] + "..." if len(content) > 500 else content,  # Truncate for readability
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

def test_full_streaming_scenario():
    """Test the exact streaming scenario from lmstudio-tooluse-test.py"""
    print("Testing Full Streaming Scenario")
    print("=" * 50)
    
    # Initialize conversation like lmstudio-tooluse-test.py
    messages = [
        {
            "role": "system",
            "content": (
                "You are an assistant that can retrieve Wikipedia articles. "
                "When asked about a topic, you can retrieve Wikipedia articles "
                "and cite information from them."
            ),
        }
    ]
    
    # Test the exact query that was failing
    user_input = "tell me about lee jae myung"
    print(f"User: {user_input}")
    
    # Add user message
    messages.append({"role": "user", "content": user_input})
    
    try:
        # Get initial response (should include tool calls)
        print("\n1. Getting initial response with tool calls...")
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=[WIKI_TOOL],
        )
        
        print(f"Response content: {response.choices[0].message.content}")
        print(f"Has tool calls: {bool(response.choices[0].message.tool_calls)}")

        if response.choices[0].message.tool_calls:
            print("✅ Tool calls detected!")
            
            # Handle tool calls exactly like lmstudio-tooluse-test.py
            tool_calls = response.choices[0].message.tool_calls

            # Add assistant message with tool calls
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

                # Print the Wikipedia content
                terminal_width = min(shutil.get_terminal_size().columns, 80)
                print("\n" + "=" * terminal_width)
                if result["status"] == "success":
                    print(f"Wikipedia article: {result['title']}")
                    print("-" * terminal_width)
                    print(result["content"])
                else:
                    print(f"Error: {result['message']}")
                print("=" * terminal_width)

                # Add tool result to conversation
                messages.append(
                    {
                        "role": "tool",
                        "content": json.dumps(result),
                        "tool_call_id": tool_call.id,
                    }
                )

            # Get the post-tool-call response with STREAMING
            print("\n2. Getting final response with STREAMING...")
            stream_response = client.chat.completions.create(
                model=MODEL, 
                messages=messages,
                stream=True  # This is the critical test!
            )
            
            print("✅ Streaming request created successfully")
            print("Assistant (streaming): ", end="", flush=True)
            
            collected_content = ""
            chunk_count = 0
            
            for chunk in stream_response:
                chunk_count += 1
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    collected_content += content
                    
                if chunk_count > 200:  # Safety limit
                    print("\n[Truncated - too many chunks]")
                    break
            
            print(f"\n\n✅ Streaming completed successfully!")
            print(f"Total content: {len(collected_content)} characters in {chunk_count} chunks")
            
            # Add final response to conversation
            messages.append(
                {
                    "role": "assistant",
                    "content": collected_content,
                }
            )
            
            return True
            
        else:
            print("❌ No tool calls detected - this is unexpected")
            return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"Error type: {type(e)}")
        return False

if __name__ == "__main__":
    success = test_full_streaming_scenario()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 FULL STREAMING TEST PASSED!")
        print("The proxy server now correctly handles:")
        print("- Tool call conversion (GLM → OpenAI format)")
        print("- Multi-turn conversations")
        print("- Streaming responses after tool calls")
        print("- OpenAI SDK compatibility")
        print("\n✅ lmstudio-tooluse-test.py should now work perfectly!")
    else:
        print("❌ FULL STREAMING TEST FAILED!")
        print("Check the implementation for remaining issues.")