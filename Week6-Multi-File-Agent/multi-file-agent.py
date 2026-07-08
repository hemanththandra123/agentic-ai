import requests
import os
import re

# ── Step 1: Build the Repo Map ─────────────────────
def build_repo_map(folder):
    repo_map = {}
    for filename in os.listdir(folder):
        if filename.endswith('.py'):
            filepath = os.path.join(folder, filename)
            with open(filepath, 'r') as f:
                content = f.read()
            functions = re.findall(r'def (\w+)\(', content)
            repo_map[filename] = functions
    return repo_map

def repo_map_to_text(repo_map):
    text = "PROJECT STRUCTURE:\n\n"
    for filename, functions in repo_map.items():
        text += f"{filename}:\n"
        for fn in functions:
            text += f"  - def {fn}(...)\n"
        text += "\n"
    return text

# ── Step 2: File tools ──────────────────────────────
def read_file(filepath):
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"

def write_file(filepath, content):
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        return f"File saved: {filepath}"
    except Exception as e:
        return f"Error: {e}"

# ── Step 3: Ask model which file is relevant ───────
def find_relevant_file(user_task, repo_map_text):
    prompt = repo_map_text
    prompt += "\nUser task: " + user_task
    prompt += "\n\nBased on the project structure above, which SINGLE file "
    prompt += "should be edited to complete this task?\n"
    prompt += "Respond with ONLY the filename, nothing else.\n"
    prompt += "Example: auth.py"

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
    )

    reply = response.json()["message"]["content"].strip()
    return reply

# ── Step 4: Edit the file ───────────────────────────
def edit_file(filepath, user_task, current_content):
    prompt = "You are an expert Python developer.\n\n"
    prompt += "Current content of " + filepath + ":\n"
    prompt += current_content
    prompt += "\n\nTask: " + user_task + "\n\n"
    prompt += "Return ONLY the complete updated file content.\n"
    prompt += "Do not add explanations, markdown, or code fences.\n"
    prompt += "Just the raw Python code."

    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
    )

    new_content = response.json()["message"]["content"].strip()
    new_content = new_content.replace("```python", "").replace("```", "").strip()
    return new_content

# ── Main flow ────────────────────────────────────────
def multi_file_agent(user_task, project_folder):
    print(f"Scanning project: {project_folder}\n")

    repo_map = build_repo_map(project_folder)
    repo_map_text = repo_map_to_text(repo_map)
    print(repo_map_text)

    print(f"Task: {user_task}\n")
    relevant_file = find_relevant_file(user_task, repo_map_text)
    print(f"Model chose: {relevant_file}\n")

    filepath = os.path.join(project_folder, relevant_file)

    if not os.path.exists(filepath):
        return f"Error: Model chose invalid file: {relevant_file}"

    current_content = read_file(filepath)
    print(f"Read {relevant_file} ({len(current_content)} chars)\n")

    new_content = edit_file(filepath, user_task, current_content)
    print("Generated new version\n")

    result = write_file(filepath, new_content)
    print(result)

    return f"Task complete. Updated: {relevant_file}"

# ── Run it ───────────────────────────────────────────
print("=" * 50)
print("   Week 6 - Multi-File Repo Agent")
print("=" * 50)

PROJECT_FOLDER = "sample-project"

task = input("What do you want to do? ")
result = multi_file_agent(task, PROJECT_FOLDER)
print(f"\n{result}")