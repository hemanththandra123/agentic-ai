import math
from datetime import datetime
from ddgs import DDGS

# ── Tool 1: Calculator ─────────────────────────────
def calculator(expression):
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Calculator error: {e}"

# ── Tool 2: Web Search ─────────────────────────────
def web_search(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            if results:
                output = ""
                for r in results:
                    output += f"Title: {r['title']}\n"
                    output += f"Summary: {r['body']}\n\n"
                return output
            return "No results found"
    except Exception as e:
        return f"Search error: {e}"

# ── Tool 3: Get Current Time ───────────────────────
def get_time():
    now = datetime.now()
    return f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}"

# ── Test all 3 tools ───────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("TOOL 1: Calculator")
    print("=" * 50)
    print(calculator("15 * 100 + 200"))
    print(calculator("45000 * 0.15"))

    print("\n" + "=" * 50)
    print("TOOL 2: Web Search")
    print("=" * 50)
    print(web_search("gold price Hyderabad today"))

    print("\n" + "=" * 50)
    print("TOOL 3: Current Time")
    print("=" * 50)
    print(get_time())