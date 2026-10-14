Setup and Reproduction Guide
=============================

Tested on 14 Oct 2026: Windows 11 Home Single Language (Build 26200), Intel Core i7-12650H, 16 GB RAM, NVIDIA GeForce RTX 3050 Laptop GPU (4 GB VRAM), NVIDIA driver 592.82, Ollama 0.40.4.

Prerequisites and Installation
---------------------------------

A. Install Ollama:
1. Download and run the Windows installer from ollama.com/download/windows
2. Verify installation:
   ollama --version
   (Tested with Ollama version 0.40.4)
3. Keep Ollama bound to localhost (default). Do not expose OLLAMA_HOST externally.

B. Python Environment:
Install Python 3.10+ (tested on Python 3.14.3) and dependencies:
pip install requests pandas openai python-dotenv
(Or use pip install -r requirements.txt)

Pull Required Models
-----------------------

Pull the evaluated local models for the ICD-10-CM benchmark:
ollama pull qwen2.5:1.5b
ollama pull qwen2.5:3b
ollama pull llama3.2:3b
ollama pull qwen2.5:7b

For earlier speed and cold start benchmarks (Days 1 and 2), optionally pull:
ollama pull qwen2.5:0.5b
ollama pull llama3.2:1b-instruct-q4_K_M

Check model details, quantization (Q4_K_M), and licences:
ollama show qwen2.5:1.5b
ollama show qwen2.5:3b
ollama show llama3.2:3b
ollama show qwen2.5:7b

CMS ICD-10-CM Code Table and Public Health Articles
------------------------------------------------------

The clinical code validation table originates from the official Centers for Medicare and Medicaid Services (CMS):
- Source: CMS 2026 ICD-10-CM Code Descriptions in Tabular Order (FY 2026, effective Oct 1, 2025 to Sept 30, 2026)
- URL: https://www.cms.gov/files/zip/2026-code-descriptions-tabular-order.zip
- Output File: data/icd10cm/icd10cm_order_2026.txt (98,186 total valid diagnosis codes)

To automatically download, unpack, and verify the CMS table and fetch the 10 public health articles:
python scripts/fetch_articles.py

The script fetches the articles from official public-domain sources (MedlinePlus, CDC, NIH) and cleans them by removing web scraping noise, broken HTML anchor linebreaks, and navigation clutter to ensure clean, readable, and understandable text in data/articles/art_01.txt through art_10.txt.

How to Run the Benchmark and Scorer
--------------------------------------

The primary benchmark script is benchmarks/run_eval.py. It automatically executes built-in assertion checks for duplicate handling, range string exclusion, and category matching before running model evaluations.

A. Full Evaluation (All 4 Models on All 10 Articles):
To run the full evaluation across qwen2.5:1.5b, qwen2.5:3b, llama3.2:3b, and qwen2.5:7b:
python benchmarks/run_eval.py

Outputs generated:
- results/eval_results.csv: Per-article performance metrics (40 rows).
- results/eval_raw_responses.json: Full untruncated JSON responses and token statistics for all 40 calls.

B. Live Demonstration Mode (2 Articles):
For interactive demonstration or grading:
python benchmarks/run_eval.py --models qwen2.5:3b --articles art_01 art_02 --live

Prints:
- Raw JSON emitted by the model
- Expected gold-standard codes and tiers
- Unique codes parsed
- Exact matches (e.g. I10)
- Category matches (first 3 characters, e.g. E11 vs E11.9)
- Chapter matches
- Invalid / hallucinated codes (and hyphenated range strings)
- Wall-clock latency and token throughput

C. Run on a Specific Model or Article:
python benchmarks/run_eval.py --models qwen2.5:7b --article art_05 --live

Other Benchmarks (Speed and Agent Test)
------------------------------------------

Warm Inference Speed Benchmark:
python benchmarks/speed_benchmark.py
Settings: 5 prompts x 3 runs, seed 42, temperature 0, num_ctx 2048. Results in results/speed_results_v2.csv.

Cold Start Latency Benchmark:
python benchmarks/cold_start.py
Measures time-to-first-token on cold load after ollama stop. Results in results/cold_start.csv.

Multi-Step Agent Test:
$env:PROVIDER="ollama"
$env:OLLAMA_MODEL="llama3.2:3b"
python agent/run_original3.py

To run with the cloud reference provider (Gemini):
$env:PROVIDER="gemini"
python agent/run_original3.py

Outputs are saved directly to results/results_original3_MODEL_TAG.md.
