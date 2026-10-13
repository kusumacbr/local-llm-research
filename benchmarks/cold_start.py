import requests, json, subprocess, time, csv

MODELS = ["qwen2.5:0.5b", "llama3.2:1b-instruct-q4_K_M", "llama3.2:3b"]
RUNS = 3
URL = "http://localhost:11434/api/generate"
OPTIONS = {"seed": 42, "temperature": 0, "num_ctx": 2048}
PROMPT = "Explain what an API is in two sentences."

def unload(model):
    subprocess.run(["ollama", "stop", model], capture_output=True)
    for _ in range(20):  # wait until it is really gone
        out = subprocess.check_output(["ollama", "ps"], text=True)
        if model not in out:
            break
        time.sleep(1)
    time.sleep(2)

def vram_used_mb():
    out = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.used",
         "--format=csv,noheader,nounits"], text=True)
    return int(out.strip().splitlines()[0])

rows = []
for model in MODELS:
    for run in range(1, RUNS + 1):
        unload(model)
        t0 = time.perf_counter()
        first, final = None, None
        with requests.post(URL, json={"model": model, "prompt": PROMPT,
                           "stream": True, "options": OPTIONS}, stream=True) as r:
            for line in r.iter_lines():
                if not line:
                    continue
                d = json.loads(line)
                if first is None and d.get("response"):
                    first = time.perf_counter() - t0   # wall-clock to first token
                if d.get("done"):
                    final = d
        row = [model, run, round(first, 3),
               round(final["load_duration"] / 1e9, 3),
               round(final["prompt_eval_duration"] / 1e9, 3),
               vram_used_mb()]
        rows.append(row)
        print(row)
    unload(model)

with open("results/cold_start.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["model", "run", "cold_first_token_s", "load_s",
                "prompt_eval_s", "vram_used_mb"])
    w.writerows(rows)
print("Saved results/cold_start.csv")