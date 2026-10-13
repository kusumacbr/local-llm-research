import requests, csv, subprocess, time

MODELS = ["qwen2.5:0.5b", "llama3.2:1b-instruct-q4_K_M", "llama3.2:3b"]
PROMPTS = [
    "Explain what an API is in two sentences.",
    "Write a Python function that reverses a string.",
    "Summarize the benefits of unit testing in 3 bullet points.",
    "What is the difference between TCP and UDP?",
    "Write a short polite email asking for a meeting reschedule.",
]
RUNS = 3
URL = "http://localhost:11434/api/generate"
OPTIONS = {"seed": 42, "temperature": 0, "num_ctx": 2048}

def vram_used_mb():
    out = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.used",
         "--format=csv,noheader,nounits"], text=True)
    return int(out.strip().splitlines()[0])

def processor_split(model):
    out = subprocess.check_output(["ollama", "ps"], text=True)
    for line in out.splitlines():
        if line.startswith(model):
            return " ".join(line.split()[4:6])
    return " ".join(line.split()[4:6])

rows = []
for model in MODELS:
    subprocess.run(["ollama", "stop", model])
    time.sleep(3)
    # warm-up so load time isn't counted
    requests.post(URL, json={"model": model, "prompt": "hi",
                  "stream": False, "options": OPTIONS})
    split = processor_split(model)
    print(model, "->", split)
    for pi, prompt in enumerate(PROMPTS, 1):
        for run in range(1, RUNS + 1):
            r = requests.post(URL, json={
                "model": model, "prompt": prompt,
                "stream": False, "options": OPTIONS
            }).json()
            tps = r["eval_count"] / (r["eval_duration"] / 1e9)
            ttft = (r["load_duration"] + r["prompt_eval_duration"]) / 1e9
            rows.append([model, pi, run, round(tps, 2), round(ttft, 3),
                         r["eval_count"], vram_used_mb(), split])
            print(rows[-1])
    subprocess.run(["ollama", "stop", model])
    time.sleep(3)

with open("results/speed_results_v2.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["model", "prompt_id", "run", "tokens_per_sec", "ttft_sec",
                "tokens_generated", "vram_used_mb", "processor"])
    w.writerows(rows)
print("Saved results/speed_results_v2.csv")
