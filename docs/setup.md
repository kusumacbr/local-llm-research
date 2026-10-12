\# Setup Guide



Tested on: Windows 11 Home Single Language (Build 26200), i7-12650H, 16 GB RAM, RTX 3050 Laptop GPU (4 GB), NVIDIA driver 592.82.



\## 1. Install

1\. Install Ollama for Windows from ollama.com/download/windows.

2\. Check the version: `ollama --version` (tested: 0.40.3).

3\. Keep Ollama on localhost (default). Do not set OLLAMA\_HOST.

4\. Install Python (tested: 3.14.3), then `pip install requests pandas openai python-dotenv`.



\## 2. Pull models

```

ollama pull qwen2.5:0.5b

ollama pull llama3.2:1b

ollama pull llama3.2:3b

```

Check quantization and licence: `ollama show <model>` and `ollama show <model> --license`.



\## 3. Check GPU use

```

ollama run <model>

/set parameter num\_ctx 2048

hi

```

In a second terminal, `ollama ps` must show 100% GPU. Set num\_ctx BEFORE the first message, because it only applies when the model (re)loads.



\## 4. Run the speed benchmark

Before running: `ollama ps` is empty, `nvidia-smi` shows about 0 MiB, and other GPU apps are closed.

```

python benchmarks\\speed\_benchmark.py

```

Output: `results/speed\_results.csv` (3 models x 5 prompts x 3 runs = 45 rows). Settings: seed 42, temperature 0, num\_ctx 2048.



\## 5. Run the agent test

```

$env:PROVIDER="ollama"

$env:OLLAMA\_MODEL="llama3.2:3b"

python agent\\run\_original3.py

```

Needs a `docs` folder with dummy Acme Robotics .md files next to agent.py. Uses http://localhost:11434/v1. There is no cloud fallback for the ollama provider. Repeat with llama3.2:1b and qwen2.5:0.5b.



\## 6. Versions

Ollama 0.40.3, Python 3.14.3, requests 2.32.5, pandas 3.0.2. Full list: `requirements.txt`.



\## Known issues

\- num\_ctx set in the terminal applies only after the model reloads.

\- Several loaded models add up in VRAM. Run `ollama stop <model>` between tests.

\- The `processor` column in the CSV has an MB/GB prefix (e.g. "GB 100% GPU"). The value is correct.

