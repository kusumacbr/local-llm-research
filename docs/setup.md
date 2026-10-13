Setup Guide
===========

Tested on 13 Oct 2026: Windows 11 Home Single Language (Build 26200), Intel i7-12650H, 16 GB RAM, NVIDIA RTX 3050 Laptop GPU (4 GB VRAM), NVIDIA driver 592.82. Dummy data only.

1. Install
----------

1. Install Ollama for Windows from ollama.com/download/windows.
2. Check the version with `ollama --version` (tested: 0.40.3).
3. Keep Ollama on localhost, which is the default. Do not set OLLAMA_HOST.
4. Install Python (tested: 3.14.3), then install the packages:

```
pip install requests pandas openai python-dotenv
```

2. Pull the models
------------------

```
ollama pull qwen2.5:0.5b
ollama pull llama3.2:1b-instruct-q4_K_M
ollama pull llama3.2:3b
```

Optional extra, used only in the v1 comparison: `ollama pull llama3.2:1b` (Q8_0).

Check the quantization and the licence of each model:

```
ollama show MODEL_NAME
ollama show MODEL_NAME --license
```

3. Check GPU use
----------------

```
ollama run MODEL_NAME
```

Inside the chat, set the context before the first message, because the setting only applies when the model loads:

```
/set parameter num_ctx 2048
hi
```

In a second terminal, run `ollama ps`. The PROCESSOR column must show 100% GPU and CONTEXT must show 2048. Then type `/bye` and run `ollama stop MODEL_NAME`.

Note: llama3.2:3b at a context of 4096 showed 20%/80% CPU/GPU on this 4 GB card.

4. Speed benchmark (warm)
-------------------------

Before running: `ollama ps` is empty, `nvidia-smi` shows about 0 MiB, and other GPU apps are closed.

```
python benchmarks\speed_benchmark.py
```

Settings: 5 fixed prompts x 3 runs per model, seed 42, temperature 0, num_ctx 2048, warm-up excluded. The script saves its results to the CSV file named in the script. The current results are in `results/speed_results_v2.csv` (3 models x 15 runs = 45 rows). The earlier run with the Q8_0 1B is in `results/speed_results_v1_1b-q8.csv`.

Print the averages:

```
python -c "import pandas as pd; df=pd.read_csv('results/speed_results_v2.csv'); print(df.groupby('model')[['tokens_per_sec','ttft_sec','vram_used_mb']].mean().round(2))"
```

Warning: running the script again overwrites the CSV file named in it. Copy the old results first.

5. Cold start benchmark
-----------------------

```
python benchmarks\cold_start.py
```

For each model the script runs `ollama stop`, waits until the model is unloaded, then times the first streamed token. 3 runs per model. Output: `results/cold_start.csv`. Do not use the PC for other work while it runs.

```
python -c "import pandas as pd; df=pd.read_csv('results/cold_start.csv'); print(df.groupby('model')[['cold_first_token_s','load_s']].mean().round(2))"
```

6. Agent test
-------------

The agent reads its documents from `agent/docs` (dummy Acme Robotics files only). It calls Ollama at http://localhost:11434/v1. When the provider is ollama there is no cloud fallback.

```
$env:PROVIDER="ollama"
$env:OLLAMA_MODEL="llama3.2:3b"
python agent\run_original3.py
```

Repeat with `llama3.2:1b` and `qwen2.5:0.5b` by changing OLLAMA_MODEL. The script prints each step and writes the answers to a results file in the current folder. A .env file is not needed for local runs. Never commit a .env file or API keys.

Note: the agent test runs used the Q8_0 tag `llama3.2:1b`, and the docs in `agent/docs` were reformatted to plain text afterwards (content unchanged).

7. Versions
-----------

| Item | Version |
|---|---|
| Ollama | 0.40.3 |
| Python | 3.14.3 |
| requests | 2.32.5 |
| pandas | 3.0.2 |
| NVIDIA driver | 592.82 |

Save the full package list with `pip freeze > requirements.txt`.

8. Known issues
---------------

- A context set with `/set parameter num_ctx` applies only after the model reloads.
- Models that stay loaded add up in VRAM. Run `ollama stop MODEL_NAME` between tests.
- The processor column in `speed_results_v2.csv` may show an MB or GB prefix, for example "MB 100% GPU". The value is correct. The script was fixed after that run.
- The first request after a model is unloaded takes about 5.5 to 6 s (see report section 6).
