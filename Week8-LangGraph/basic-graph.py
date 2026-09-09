from typing import TypedDict
from langgraph.graph import StateGraph, END
import requests

#define what our state looks like 

class AgentState(TypedDict):
    messages : list



def call_llm(state: AgentState):
    """This node calls the LLM with current messages"""
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2",
            "messages": state["messages"],
            "stream": False
        }
    )
    reply = response.json()["message"]["content"]
    
    # Add the reply to messages
    state["messages"].append({"role": "assistant", "content": reply})
    return state

# Build the graph
graph = StateGraph(AgentState)

# Add our node
graph.add_node("call_llm", call_llm)

# Set which node runs first
graph.set_entry_point("call_llm")

# Set which node runs after call_llm (in this case, we END)
graph.add_edge("call_llm", END)

# Compile the graph into a runnable app
app = graph.compile()
# Print visual graph (Mermaid format)
print(app.get_graph().draw_mermaid())

# Run the graph
if __name__ == "__main__":
    initial_state = {
        "messages": [
            {"role": "user", "content": "What is 2*9?"}
        ]
    }
    
    result = app.invoke(initial_state)
    
    print("Final messages:")
    for msg in result["messages"]:
        print(f"{msg['role']}: {msg['content']}")