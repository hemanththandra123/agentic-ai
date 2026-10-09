import re
import subprocess
import requests

BLOCKED = ["&", "|", ";", "run_shell(", '")']
DESTRUCTIVE = ("del ", "erase ", "rmdir ", "rd ", "format ")
FILE_PATTERN = re.compile(
    r"[\w\-]+\.(?:py|txt|md|json|csv|js|html|css|log|yml|yaml|bat)\b", re.I)

current_request = ""
messages = []


def check_command(command):
    """Rules enforced by CODE, before the user is even asked."""
    lowered = command.lower()
    for token in BLOCKED:
        if token in lowered:
            return f"'{token}' is not allowed. Use ONE simple command."
    names = FILE_PATTERN.findall(current_request)
    for name in names:
        if name.lower() not in lowered:
            return (f"the user named '{name}' but the command does not "
                    f"contain it. Use exactly '{name}'.")
    if names and lowered.startswith(("mkdir", "md ")):
        return (f"the user named a file ('{names[0]}'), but mkdir makes a "
                f"FOLDER. Use: type NUL > {names[0]}")
    return None

def list_folder():
    result = subprocess.run(
        "dir /b", shell=True, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
        stdin=subprocess.DEVNULL, timeout=15)
    return result.stdout.strip() or "(empty)"


def run_shell_command(command):
    problem = check_command(command)
    if problem:
        print(f"\n[Blocked before running] {command}")
        return "BLOCKED: " + problem

    print(f"\nAgent wants to run: {command}")
    if input("Allow this command? (y/n): ").lower() != "y":
        return "DENIED"

    if command.lower().startswith(DESTRUCTIVE):
        print("DESTRUCTIVE command.")
        if input("Type DELETE to confirm: ") != "DELETE":
            return "DENIED"

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            stdin=subprocess.DEVNULL, timeout=15)
        output = (result.stdout + result.stderr).strip()
        failure_markers = ["could not find", "cannot find", "not recognized",
                           "does not exist", "access is denied"]

        if (result.returncode != 0
                or result.stderr.strip()
                or any(m in output.lower() for m in failure_markers)):
            return (f"FAILED (exit code {result.returncode}): "
                    f"the command did not do what was intended.\n{output}")

        text = f"SUCCEEDED:\n{output or '(no output)'}"
        if not command.lower().startswith("dir"):
            text += "\n\nFOLDER NOW CONTAINS:\n" + list_folder()
        return text
    except Exception as e:
        return f"FAILED: {e}"


CLI_PROMPT = """You are a CLI agent that runs ONE Windows cmd.exe command at a time.

FORMAT (always):
THOUGHT: (what needs to be done)
ACTION: TOOL: run_shell("command")

When the result answers the request:
ACTION: ANSWER: short summary

COMMANDS TO USE:
- list files:      run_shell("dir")
- create a file:   run_shell("type NUL > NAME")
- create a folder: run_shell("mkdir NAME")
- delete a file:   run_shell("del NAME")
- delete a folder: run_shell("rmdir /s /q NAME")
- show a file:     run_shell("type NAME")
- git:             run_shell("git status")

RULES:
- Use the EXACT name the user typed. Never fix or change it.
- Never chain commands with &, | or ;.
- The folder listing is added to results automatically. Do not run dir to verify.
- If a result says BLOCKED, try again with one simple command.
- Report only what the result shows. Never guess.
"""


def run_tool(tool_call):
    tool_call = tool_call.strip()
    if tool_call.startswith("run_shell"):
        command = tool_call[len("run_shell("):-1].strip('"\'')
        return run_shell_command(command)
    return "FAILED: unknown tool"


def cli_agent(user_input):
    global current_request
    current_request = user_input
    messages.clear()  # fresh context: old results can't be reused as new facts
    messages.append({"role": "user", "content": user_input})
    ran_any = False

    for step in range(5):
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2",
                "messages": [{"role": "system", "content": CLI_PROMPT},
                             *messages],
                "stream": False
            }
        )
        reply = response.json()["message"]["content"]

        if "ACTION: TOOL:" in reply:
            tool_line = reply.split("ACTION: TOOL:")[1].strip()
            tool_line = tool_line.split("\n")[0].strip()
            tool_result = run_tool(tool_line)

            if tool_result == "DENIED":
                return "Cancelled. The command was not run."

            if tool_result.startswith("FAILED"):
                note = ("An earlier command in this request already ran. "
                        "Check the folder with dir.\n") if ran_any else ""
                return f"The command failed.\n{note}{tool_result}"

            messages.append({"role": "assistant", "content": reply})

            if tool_result.startswith("BLOCKED"):
                messages.append({"role": "user", "content":
                    f"OBSERVATION: {tool_result}\nThat command was NOT run. "
                    "Try again with ONE simple command."})
                continue

            ran_any = True
            messages.append({"role": "user", "content":
                f"OBSERVATION: {tool_result}\n"
                "If this answers the request, reply with ACTION: ANSWER now."})

        elif "ACTION: ANSWER:" in reply:
            return reply.split("ACTION: ANSWER:")[1].strip()

        else:
            return reply

    return "Stopped after 5 steps without a final answer."


# ---- Main loop (keep at the very bottom) ----
print("=" * 50)
print("   Week 9 - CLI Automation Agent")
print("=" * 50)
print("Try: show me all files | create a new file scratch.py")
print("     delete scratch.py | check git status")
print("Type 'quit' to exit\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        print("Bye!")
        break
    print("\nAgent working...\n")
    print(f"\nAgent: {cli_agent(user_input)}\n")