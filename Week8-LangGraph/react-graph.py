from typing import TypedDict
from tools import calculator, web_search, get_time

from langgraph.graph import StateGraph, END
import requests

class AgentState(TypedDict):
    messages: list
    next_step: str  # "continue" or "end"
def think_node(state: AgentState):
    """Node 1: LLM thinks and decides next action"""
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "llama3.2",
            "messages": state["messages"],
            "stream": False
        }
    )
    reply = response.json()["message"]["content"]
    state["messages"].append({"role": "assistant", "content": reply})
    
    # Decide what happens next based on the reply
    if "ACTION: TOOL:" in reply:
        state["next_step"] = "tool"
    else:
        state["next_step"] = "end"
    
    return state

def tool_node(state: AgentState):
    """Node 2: Runs whichever tool the model requested"""
    last_message = state["messages"][-1]["content"]
    tool_line = last_message.split("ACTION: TOOL:")[1].strip()
    tool_line = tool_line.split("\n")[0].strip()
    
    if tool_line.startswith("calculator"):
        expression = tool_line[len("calculator("):-1]
        result = calculator(expression)
    elif tool_line.startswith("web_search"):
        query = tool_line[len("web_search("):-1].strip('"\'')
        result = web_search(query)
    elif tool_line.startswith("get_time"):
        result = get_time()
    else:
        result = "Tool not found"
    
    state["messages"].append({
        "role": "user",
        "content": f"OBSERVATION: {result}"
    })
    
    return state
def route_next_step(state: AgentState):
    """Decides which node to go to next"""
    return state["next_step"]


graph = StateGraph(AgentState)

# Add both nodes
graph.add_node("think", think_node)
graph.add_node("tool", tool_node)

# Set starting point
graph.set_entry_point("think")

# Conditional branching after "think"
graph.add_conditional_edges(
    "think",
    route_next_step,
    {
        "tool": "tool",   # if next_step == "tool" → go to tool node
        "end": END        # if next_step == "end" → finish
    }
)

# After tool runs, loop BACK to think
graph.add_edge("tool", "think")

app = graph.compile()


if __name__ == "__main__":
    system_prompt = """You are a helpful agent with access to tools:
1. calculator(expression)
2. web_search(query)
3. get_time()

If you need a tool, respond EXACTLY in this format, 
with no deviation:
ACTION: TOOL: web_search("your search query here")

Example:
ACTION: TOOL: calculator(15 * 20)

Do NOT write just "web_search:" - you MUST include 
the full "ACTION: TOOL:" prefix exactly as shown.

If you have enough info, just answer normally.
"""


    initial_state = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "What is the current gold price in India now"}
        ],
        "next_step": ""
    }

    result = app.invoke(initial_state)

    print("\n=== Final Conversation ===")
    for msg in result["messages"]:
        print(f"{msg['role']}: {msg['content']}\n")