import requests
import subprocess
import tempfile
import os
from tools import calculator, web_search, get_time

# ── System prompt for coding agent ─────────────────
CODING_PROMPT = """You are an expert Python coding agent.

You can use these tools:
1. run_code(code) - Write and execute Python code
2. web_search(query) - Search for documentation or solutions
3. calculator(expression) - For math calculations

You MUST always follow this exact format:

THOUGHT: (analyze what needs to be done)
ACTION: TOOL: tool_name("input")

If using run_code, write the COMPLETE Python code:
ACTION: TOOL: run_code("
def solution():
    # your code here
    pass

print(solution())
")

After seeing output:
THOUGHT: (did it work? any errors?)
ACTION: ANSWER: explanation + final code

RULES:
- ALWAYS run the code to verify it works
- If there is an error, fix and run again
- Maximum 3 fix attempts
- NEVER return unverified code
- Always print the output so you can see results
- Once code runs successfully, give ANSWER immediately
"""

messages = []

# ── Code execution tool ─────────────────────────────
def run_code(code):
    """Execute Python code and return output or error"""
    try:
        code = code.strip().strip('"\'')

        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(code)
            temp_file = f.name

        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=10
        )

        os.unlink(temp_file)

        if result.returncode == 0:
            return f"✅ Output:\n{result.stdout}"
        else:
            return f"❌ Error:\n{result.stderr}"

    except subprocess.TimeoutExpired:
        return "❌ Error: Code took too long to run (timeout)"
    except Exception as e:
        return f"❌ Error: {e}"

def run_tool(tool_call):
    """Execute whichever tool the model chose"""
    tool_call = tool_call.strip()

    if tool_call.startswith("run_code"):
        code = tool_call[len("run_code("):-1]
        return run_code(code)
    elif tool_call.lower().startswith("web_search"):
        query = tool_call[len("web_search("):-1]
        query = query.replace("query=", "").strip('"\'').strip()
        return web_search(query)
    elif tool_call.startswith("calculator"):
        expression = tool_call[len("calculator("):-1]
        return calculator(expression)
    elif tool_call.startswith("get_time"):
        return get_time()
    return "Tool not found"

def code_agent(user_input):
    """Coding agent with self debugging loop"""
    messages.append({"role": "user", "content": user_input})

    step = 0
    max_steps = 6

    while step < max_steps:
        step += 1

        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2",
                "messages": [
                    {"role": "system", "content": CODING_PROMPT},
                    *messages
                ],
                "stream": False
            }
        )

        reply = response.json()["message"]["content"]

        if "ACTION: TOOL:" in reply:
            tool_line = reply.split("ACTION: TOOL:")[1].strip()

            if tool_line.startswith("run_code"):
                start = tool_line.find("(")
                depth = 0
                end = -1
                for i, ch in enumerate(tool_line[start:]):
                    if ch == "(":
                        depth += 1
                    elif ch == ")":
                        depth -= 1
                        if depth == 0:
                            end = start + i
                            break
                if end != -1:
                    tool_line = tool_line[:end+1]
            else:
                tool_line = tool_line.split("\n")[0].strip()

            print(f"🔧 Running: {tool_line[:60]}...")
            tool_result = run_tool(tool_line)
            print(f"📊 {tool_result[:2000]}")

            # ── Key fix: stop looping if code works ──
            if "✅ Output:" in tool_result:
                messages.append({"role": "assistant", "content": reply})
                messages.append({
                    "role": "user",
                    "content": f"OBSERVATION: {tool_result}\nCode works perfectly! Give the ANSWER now."
                })
            else:
                messages.append({"role": "assistant", "content": reply})
                messages.append({
                    "role": "user",
                    "content": f"OBSERVATION: {tool_result}\nFix the error and try again."
                })

        elif "ACTION: ANSWER:" in reply:
            final_answer = reply.split("ACTION: ANSWER:")[1].strip()
            messages.append({"role": "assistant", "content": reply})
            return final_answer

        else:
            messages.append({"role": "assistant", "content": reply})
            return reply

    return "Max steps reached"

# ── Main loop ───────────────────────────────────────
print("=" * 50)
print("   Week 4 - Coding Agent")
print("=" * 50)
print("Try asking:")
print("  - Write a function to reverse a string")
print("  - Find all prime numbers up to 50")
print("  - Write a function to check if a number is palindrome")
print("  - Sort this list: [64, 34, 25, 12, 22, 11, 90]")
print("Type 'quit' to exit\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        print("Bye!")
        break

    print("\n🤖 Agent working...\n")
    answer = code_agent(user_input)
    print(f"\n✅ Agent: {answer}\n")
    print("=" * 50)