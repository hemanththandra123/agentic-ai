import requests

def chat(prompt):
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
    )
    return response.json()["message"]["content"]

# ── Test 1: Without Chain of Thought ──────────────────
print("=" * 50)
print("TEST 1: Without CoT")
print("=" * 50)
answer1 = chat("What is 17 multiplied by 24 plus 56 divided by 8?")
print(answer1)

# ── Test 2: With Chain of Thought ─────────────────────
print("\n" + "=" * 50)
print("TEST 2: With Chain of Thought")
print("=" * 50)
answer2 = chat("What is 17 multiplied by 24 plus 56 divided by 8? Think step by step.")
print(answer2)
