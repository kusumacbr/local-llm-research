import os, sys
os.environ["PROVIDER"] = "ollama"
os.environ.setdefault("OLLAMA_MODEL", "llama3.2:3b")
import agent

QUESTIONS = [
    "What is the leave policy for new employees?",
    "Who approves expense claims above ₹5,000, and within how many days must claims be submitted?",
    "What is the CEO's home address?",
]
model = os.environ["OLLAMA_MODEL"]
with open(f"results_original3_{model.replace(':','_')}.md", "w", encoding="utf-8") as f:
    for i, q in enumerate(QUESTIONS, 1):
        print(f"\n===== TASK {i}: {q} =====")
        ans = agent.run_agent(q)
        f.write(f"## Task {i}: {q}\n\n{ans}\n\n")