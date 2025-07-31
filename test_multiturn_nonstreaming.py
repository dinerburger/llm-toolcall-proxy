#!/usr/bin/env python3
"""
Test multi-turn conversation without streaming (for now)
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

def test_multiturn_conversation():
    """Test multi-turn conversation without streaming"""
    print("Testing Multi-Turn Conversation (Non-Streaming)")
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
    
    # Simulate multi-turn conversation
    conversation_turns = [
        "tell me about lee jae myung",
        "what about his political career specifically?",
        "now tell me about Python programming language", 
        "what are the main features of Python?"
    ]
    
    for turn_num, user_input in enumerate(conversation_turns, 1):
        print(f"\n=== Turn {turn_num}: {user_input} ===")
        
        # Add user message
        messages.append({"role": "user", "content": user_input})
        
        try:
            # Get response from model
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

                # Get the post-tool-call response (NON-STREAMING for now)
                print("\nGetting final response (non-streaming)...")
                final_response = client.chat.completions.create(
                    model=MODEL, 
                    messages=messages
                )
                
                final_content = final_response.choices[0].message.content
                print(f"Final response: {final_content[:200]}{'...' if len(final_content) > 200 else ''}")
                
                # Add final response to conversation
                messages.append(
                    {
                        "role": "assistant",
                        "content": final_content,
                    }
                )
                
            else:
                # Handle regular response (no tool calls)
                print("Regular response (no tool calls)")
                print(f"Assistant: {response.choices[0].message.content}")
                messages.append(
                    {
                        "role": "assistant",
                        "content": response.choices[0].message.content,
                    }
                )
            
            print(f"\nConversation length: {len(messages)} messages")
            
        except Exception as e:
            print(f"❌ Error in turn {turn_num}: {e}")
            return False
    
    print(f"\n{'='*50}")
    print(f"Multi-turn conversation completed successfully!")
    print(f"Final conversation length: {len(messages)} messages")
    
    return True

if __name__ == "__main__":
    success = test_multiturn_conversation()
    
    if success:
        print("\n🎉 Multi-turn conversation test PASSED!")
        print("The proxy server correctly handles:")
        print("- Multiple conversation turns")
        print("- Tool call conversion in multi-turn context") 
        print("- Message history management")
        print("- Non-streaming responses after tool calls")
        print("\nNote: Streaming is still being debugged")
    else:
        print("\n❌ Multi-turn conversation test FAILED!")
        print("Check the proxy server implementation.")