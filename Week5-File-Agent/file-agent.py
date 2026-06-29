import requests
import subprocess
import os

# ── System prompt ───────────────────────────────────
FILE_AGENT_PROMPT = """You are an expert Python developer agent.

You can use these tools:
1. read_file(filepath) - Read any file
2. write_file(filepath, content) - Write/update a file
3. run_tests(filepath) - Run pytest on a test file
4. run_code(code) - Execute Python code

You MUST always follow this exact format:

THOUGHT: (analyze what needs to be done)
ACTION: TOOL: tool_name("input")

After seeing result:
THOUGHT: (what did you find? what needs fixing?)
ACTION: TOOL: next_tool("input")

When all tests pass:
ACTION: ANSWER: summary of what you fixed

RULES:
- ALWAYS read the file first before editing
- ALWAYS run tests after making changes
- NEVER guess what the code looks like — read it first
- Fix ALL failing tests before answering
- Keep the original function names unchanged
"""

messages = []

# ── Tools ───────────────────────────────────────────
def read_file(filepath):
    try:
        filepath = filepath.strip().strip('"\'')
        with open(filepath, 'r') as f:
            content = f.read()
        return f"File content:\n{content}"
    except Exception as e:
        return f"❌ Error reading file: {e}"

def write_file(filepath, content):
    try:
        filepath = filepath.strip().strip('"\'')
        content = content.strip().strip('"\'')
        with open(filepath, 'w') as f:
            f.write(content)
        return f"✅ File saved: {filepath}"
    except Exception as e:
        return f"❌ Error writing file: {e}"

def run_tests(filepath):
    try:
        filepath = filepath.strip().strip('"\'')
        result = subprocess.run(
            ['python', '-m', 'pytest', filepath, '-v'],
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout + result.stderr
        if result.returncode == 0:
            return f"✅ All tests passed!\n{output}"
        else:
            return f"❌ Tests failed:\n{output}"
    except Exception as e:
        return f"❌ Error running tests: {e}"

def run_code(code):
    try:
        code = code.strip().strip('"\'')
        import tempfile
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py',
            delete=False, encoding='utf-8'
        ) as f:
            f.write(code)
            temp_file = f.name
        result = subprocess.run(
            ['python', temp_file],
            capture_output=True, text=True, timeout=10
        )
        os.unlink(temp_file)
        if result.returncode == 0:
            return f"✅ Output:\n{result.stdout}"
        else:
            return f"❌ Error:\n{result.stderr}"
    except Exception as e:
        return f"❌ Error: {e}"

def run_tool(tool_call):
    
    tool_call = tool_call.strip().lower()  # ← add .lower()

    if tool_call.startswith("read_file"):
        arg = tool_call[len("read_file("):-1]
        return read_file(arg)

    elif tool_call.startswith("write_file"):
        inner = tool_call[len("write_file("):-1]
        if inner.startswith('"'):
            end_quote = inner.find('"', 1)
            filepath = inner[1:end_quote]
            content = inner[end_quote+2:].strip().strip('"\'')
        elif inner.startswith("'"):
            end_quote = inner.find("'", 1)
            filepath = inner[1:end_quote]
            content = inner[end_quote+2:].strip().strip('"\'')
        else:
            comma = inner.find(",")
            filepath = inner[:comma].strip().strip('"\'')
            content = inner[comma+1:].strip().strip('"\'')
        return write_file(filepath, content)

    elif tool_call.startswith("run_tests"):
        arg = tool_call[len("run_tests("):-1]
        return run_tests(arg)

    elif tool_call.startswith("run_code"):
        arg = tool_call[len("run_code("):-1]
        return run_code(arg)

    return "Tool not found"

def file_agent(user_input):
    messages.append({"role": "user", "content": user_input})

    step = 0
    max_steps = 10

    while step < max_steps:
        step += 1
        print(f"\n--- Step {step} ---")

        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2",
                "messages": [
                    {"role": "system", "content": FILE_AGENT_PROMPT},
                    *messages
                ],
                "stream": False
            }
        )

        reply = response.json()["message"]["content"]

        if "ACTION: TOOL:" in reply:
            # Extract tool call — handle multiline
            tool_section = reply.split("ACTION: TOOL:")[1].strip()

            # Find complete tool call
            start = tool_section.find("(")
            depth = 0
            end = -1
            for i, ch in enumerate(tool_section[start:]):
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        end = start + i
                        break

            if end != -1:
                tool_line = tool_section[:end+1]
            else:
                tool_line = tool_section.split("\n")[0]

            print(f"🔧 Tool: {tool_line[:80]}...")
            tool_result = run_tool(tool_line)
            print(f"📊 Result: {tool_result[:300]}")

            messages.append({"role": "assistant", "content": reply})
            messages.append({
                "role": "user",
                "content": f"OBSERVATION: {tool_result}\nContinue."
            })

        elif "ACTION: ANSWER:" in reply:
            final = reply.split("ACTION: ANSWER:")[1].strip()
            messages.append({"role": "assistant", "content": reply})
            return final

        else:
            messages.append({"role": "assistant", "content": reply})
            return reply

    return "Max steps reached"

# ── Main ────────────────────────────────────────────
print("=" * 50)
print("   Week 5 - File Agent")
print("=" * 50)

# Get paths
base = os.path.dirname(os.path.abspath(__file__))
utils_path = os.path.join(base, "test-project", "utils.py")
test_path = os.path.join(base, "test-project", "test-utils.py")

print(f"Target file: {utils_path}")
print(f"Test file:   {test_path}\n")

task = f"""
Read the file at {utils_path}
Then run the tests at {test_path}
Find all failing tests and fix the functions in utils.py
Make sure ALL tests pass before finishing
"""

print("🤖 Agent starting...\n")
result = file_agent(task)
print(f"\n✅ Done:\n{result}")