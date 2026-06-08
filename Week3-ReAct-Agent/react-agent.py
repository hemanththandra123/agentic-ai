import requests
from tools import calculator, web_search, get_time

# ── System prompt forces ReAct thinking ────────────
REACT_PROMPT = """You are an intelligent agent that ALWAYS reasons before acting.

You have access to these tools:
1. calculator(expression) - For any math
2. web_search(query) - For current/real-time info
3. get_time() - For current date and time

You MUST always follow this exact format:

THOUGHT: (think about what the user needs)
ACTION: (either use a tool OR answer directly)

If using a tool, write:
ACTION: TOOL: tool_name("input here")

If you have enough info to answer:
ACTION: ANSWER: your final answer here

RULES:
- NEVER skip the THOUGHT step
- NEVER guess on current facts → always web_search
- NEVER do math in your head → always use calculator
- After seeing a tool result, write another THOUGHT
- Only write ANSWER when you are confident
- Always use quotes around search queries
"""

messages = []

def run_tool(tool_call):
    """Execute the tool the model chose"""
    tool_call = tool_call.strip()
    if tool_call.startswith("calculator"):
        expression = tool_call[len("calculator("):-1]
        return calculator(expression)
    elif tool_call.startswith("web_search"):
        query = tool_call[len("web_search("):-1]
        query = query.replace("query=", "").strip('"\'').strip()
        return web_search(query)
    elif tool_call.startswith("get_time"):
        return get_time()
    return "Tool not found"

def react(user_input):
    """Full ReAct loop - Think, Act, Observe, repeat"""
    messages.append({"role": "user", "content": user_input})

    step = 0
    max_steps = 5

    while step < max_steps:
        step += 1

        # ── Get model's thought + action ───────────
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2",
                "messages": [
                    {"role": "system", "content": REACT_PROMPT},
                    *messages
                ],
                "stream": False
            }
        )

        reply = response.json()["message"]["content"]

        # ── Parse the response ─────────────────────
        if "ACTION: TOOL:" in reply:
            tool_line = reply.split("ACTION: TOOL:")[1].strip()
            tool_line = tool_line.split("\n")[0].strip()
            tool_result = run_tool(tool_line)

            # Add to conversation silently
            messages.append({"role": "assistant", "content": reply})
            messages.append({
                "role": "user",
                "content": f"OBSERVATION: {tool_result}\nContinue your reasoning."
            })

        elif "ACTION: ANSWER:" in reply:
            final_answer = reply.split("ACTION: ANSWER:")[1].strip()
            messages.append({"role": "assistant", "content": reply})
            return final_answer

        else:
            messages.append({"role": "assistant", "content": reply})
            return reply

    return "Could not complete the task"

# ── Main loop ──────────────────────────────────────
print("=" * 50)
print("     Hemanth's ReAct AI Agent")
print("=" * 50)
print("Try asking:")
print("  - Who is the President of USA?")
print("  - What is 15% of 85000?")
print("  - Latest news in Hyderabad?")
print("  - What time is it?")
print("Type 'quit' to exit\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        print("Bye!")
        break

    print("Agent: thinking...")
    answer = react(user_input)
    print(f"Agent: {answer}\n")
    print("-" * 50)