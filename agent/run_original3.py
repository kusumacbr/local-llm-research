import os, sys
os.environ.setdefault("PROVIDER", "ollama")
os.environ.setdefault("OLLAMA_MODEL", "llama3.2:3b")
import agent

QUESTIONS = [
    "What is the leave policy for new employees?",
    "Who approves expense claims above ₹5,000, and within how many days must claims be submitted?",
    "What is the CEO's home address?",
]
prov = os.environ.get("PROVIDER", "ollama").lower()
model_tag = "gemini-flash-lite-latest" if prov == "gemini" else os.environ.get("OLLAMA_MODEL", "llama3.2:3b")
output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, f"results_original3_{model_tag.replace(':', '_').replace('/', '_')}.md")

with open(output_path, "w", encoding="utf-8") as f:
    for i, q in enumerate(QUESTIONS, 1):
        print(f"\n===== TASK {i}: {q} =====")
        ans = agent.run_agent(q)
        clean_ans = ans.replace("**", "").replace("* ", "- ")
        title = f"Task {i}: {q}"
        f.write(f"{title}\n{'-' * len(title)}\n\n{clean_ans}\n\n")