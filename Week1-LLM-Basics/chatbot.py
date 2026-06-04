import requests

messages = []

def chat(user_input):
    # Add user message to memory
    messages.append({"role": "user", "content": user_input})
    
    # Send full conversation history to Ollama
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2",
            "messages": messages,
            "stream": False
        }
    )
    
    # Get the reply
    reply = response.json()["message"]["content"]
    
    # Add reply to memory
    messages.append({"role": "assistant", "content": reply})
    
    return reply

# ── Main loop ──────────────────────────────────────
print("=" * 50)
print("  Hemanth's Local Chatbot - powered by Llama3.2")
print("=" * 50)
print("Type 'quit' to exit\n")

while True:
    user_input = input("You: ")
    
    if user_input.lower() == "quit":
        print("Bye!")
        break
    
    print("\nBot: thinking...")
    response = chat(user_input)
    print(f"\nBot: {response}\n")

    
