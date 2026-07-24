# Week 7 — OpenHands (Autonomous Coding Agent)

## What is OpenHands
OpenHands is an open-source, fully autonomous AI coding agent 
that can write code, run commands, browse the web, and edit 
files — all within a Docker sandbox for safety.

GitHub: OpenHands/OpenHands

## What I Learned

### Infrastructure Setup (Successfully Completed)
- Enabled Virtualization Technology in BIOS
- Installed WSL 2 (Windows Subsystem for Linux)
- Installed Ubuntu (Linux distribution inside Windows)
- Installed Docker Desktop
- Configured WSL Integration in Docker settings
- Successfully ran test containers (hello-world)
- Successfully launched OpenHands via Docker
- Accessed OpenHands web UI at localhost:3000

### LLM Configuration
- Initially attempted Ollama (local, free)
  - Blocked by: OpenHands requires minimum 16,384 token 
    context window; Ollama's default llama3.1 only provides 
    8,192 tokens
- Switched to Groq API (free tier, cloud-based)
  - Hit rate limit: free tier allows 12,000 tokens/minute,
    OpenHands requests often exceed 50,000+ tokens per call

### Hardware Constraint Discovered
- OpenHands + Docker + WSL2 requires 16GB+ RAM for stable operation
- My laptop has 8GB RAM total, ~1.3GB available under load
- Sandbox containers repeatedly crashed with 
  "Sandbox entered error state" due to insufficient memory

## Architecture Understanding

OpenHands' components map directly to what I built in Weeks 1-6:

| OpenHands Feature | My Equivalent Build |
|---|---|
| ReAct reasoning loop | react_agent.py (Week 3) |
| Tool calling | tools.py (Week 2) |
| File reading/editing | file_agent.py (Week 5) |
| Multi-file understanding | multi_file_agent.py (Week 6) |
| Docker sandboxing | New concept — safety isolation |
| Two-tier container architecture | App server + Agent server |

## Key Takeaway

Understanding an agent's internals (built from scratch in 
Weeks 1-6) makes production tools like OpenHands completely 
transparent — even when the tool itself doesn't run perfectly 
due to hardware constraints, I understand exactly WHY it's 
failing and WHAT each component is trying to do.

## Real World Lesson

Production-grade autonomous agents like OpenHands are 
resource-intensive by design (multiple containers, large 
context models, sandboxed execution). This is a genuine 
infrastructure consideration for real deployments — not 
just a "nice to have."

## Next Steps
- Revisit OpenHands with access to 16GB+ RAM hardware
- Continue with Week 8 (lightweight, cloud-based, 
  no local resource constraints)