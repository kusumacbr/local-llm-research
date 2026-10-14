Local LLM Research: ICD-10-CM Classification and Agent Benchmarking
===================================================================

This repository benchmarks the capabilities, clinical accuracy, and inference throughput of local small language models (0.5B to 7B parameters) running entirely on a consumer edge device (Windows 11, NVIDIA RTX 3050 Laptop GPU with 4 GB VRAM) using Ollama. It evaluates models on structured JSON medical condition extraction and official ICD-10-CM diagnosis coding across 10 public health articles using the official CMS FY 2026 tabular taxonomy, measuring exact code precision, recall, category matches, taxonomy hallucination rates, and hardware offload trade-offs under strict localhost privacy.

Reproducing the Benchmark from a Fresh Clone
--------------------------------------------

Step 1: Clone repository
git clone https://github.com/kusumacbr/local-llm-research.git

Step 2: Enter project directory
cd local-llm-research

Step 3: Install Python dependencies
pip install requests pandas openai python-dotenv

Step 4: Pull evaluated local models into Ollama
ollama pull qwen2.5:1.5b; ollama pull qwen2.5:3b; ollama pull llama3.2:3b; ollama pull qwen2.5:7b

Step 5: Fetch CMS ICD-10-CM code table and clean public health articles for evaluation
python scripts/fetch_articles.py

Step 6: Run the full 4-model evaluation benchmark across all 10 articles
python benchmarks/run_eval.py

Step 7: Run live demonstration on 2 articles
python benchmarks/run_eval.py --models qwen2.5:3b --articles art_01 art_02 --live

Detailed research findings, hardware metrics, and failure analyses are available in [docs/report.md](file:///c:/Users/Victus/Documents/local-llm-research-git/docs/report.md) and [results/summary.md](file:///c:/Users/Victus/Documents/local-llm-research-git/results/summary.md). Complete installation prerequisites are documented in [docs/setup.md](file:///c:/Users/Victus/Documents/local-llm-research-git/docs/setup.md).
