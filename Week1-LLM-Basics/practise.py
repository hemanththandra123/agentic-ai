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
answer1 = chat("Tell me what else you can do")
print(answer1)


