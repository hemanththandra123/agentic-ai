import requests
from tools import calculator, web_search, get_time

# ── Tool definitions we tell the model about ───────
TOOLS_DESCRIPTION = """
You have access to these tools:

1. calculator(expression) - For math calculations
   Example: calculator(45000 * 0.15)

2. web_search(query) - For real-time information
   Example: web_search("gold price Hyderabad today")

3. get_time() - For current date and time
   Example: get_time()

RULES:
- If you need to use a tool, respond EXACTLY like this:
  TOOL: tool_name(input)
- If you don't need a tool, just answer directly.
- Only use ONE tool per response.
"""

messages = []

def run_tool(tool_call):
    """Execute whichever tool the model chose"""
    if tool_call.startswith("calculator"):
        expression = tool_call[len("calculator("):-1]
        return calculator(expression)
    elif tool_call.startswith("web_search"):
        query = tool_call[len("web_search("):-1].strip('"\'')
        return web_search(query)
    elif tool_call.startswith("get_time"):
        return get_time()
    return "Tool not found"

def chat(user_input):
    messages.append({"role": "user", "content": user_input})

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2",
            "messages": [
                {"role": "system", "content": TOOLS_DESCRIPTION},
                *messages
            ],
            "stream": False
        }
    )

    reply = response.json()["message"]["content"]

    # ── Check if model wants to use a tool ─────────
    if "TOOL:" in reply:
        tool_line = reply.split("TOOL:")[1].strip()
        print(f"\n🔧 Using tool: {tool_line}")

        tool_result = run_tool(tool_line)
        print(f"📊 Tool result: {tool_result}")

        # Send tool result back to model
        messages.append({"role": "assistant", "content": reply})
        messages.append({"role": "user", "content": f"Tool result: {tool_result}"})

        # Get final answer from model
        final = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2",
                "messages": [
                    {"role": "system", "content": TOOLS_DESCRIPTION},
                    *messages
                ],
                "stream": False
            }
        )
        reply = final.json()["message"]["content"]

    messages.append({"role": "assistant", "content": reply})
    return reply

# ── Main loop ──────────────────────────────────────
print("=" * 50)
print("  Week 2 - AI Agent with Tools")
print("=" * 50)
print("Try asking:")
print("  - What is 15% of 45000?")
print("  - What are gold prices in Hyderabad?")
print("  - What time is it?")
print("Type 'quit' to exit\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        print("Bye!")
        break

    print("\nAgent: thinking...")
    response = chat(user_input)
    print(f"\nAgent: {response}\n")