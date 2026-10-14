Benchmark Results Summary: Local LLM ICD-10-CM Extraction
==========================================================

Date: 2026-10-14
Hardware: NVIDIA GeForce RTX 3050 Laptop GPU (4096 MiB VRAM), 12th Gen Intel Core i7-12650H, 16 GB RAM
Software: Windows 11, Ollama 0.40.4, Python 3.14.3
Prompt File: prompts/extraction_prompt_v2.txt (out-of-key examples)
Schema: schema/icd10_schema.json (JSON format constraint, temperature: 0)
Test Set: 10 full-text public health articles fetched via script and cleaned for clear readability and understanding (36 ground-truth clinical conditions in data/answer_key.csv)
Scoring Rule: Unique normalized codes per article; range strings never count; category match = first 3 characters.

Final Performance and Accuracy Table
------------------------------------

| Model | Size | Processor | Valid JSON | Unique Codes Returned | Invalid Codes (Hallucinations) | Exact Matches (GT) | Exact Precision | Exact Recall | Exact F1 | Category Match (3-char) | Chapter Match | Tier Match | Latency / Art | Throughput | Mean Tokens (in / out) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen2.5:1.5b | 1.5B (Q4_K_M) | 100% GPU | 10/10 (100%) | 18 | 4 (22.2%) | 3 | 16.7% | 8.3% | 11.1% | 6 | 13 | 1 | 4.38 s | 822 art/hr | 1363.9 / 156.4 |
| qwen2.5:3b | 3.2B (Q4_K_M) | 100% GPU | 10/10 (100%) | 22 | 3 (13.6%) | 1 | 4.5% | 2.8% | 3.4% | 6 | 19 | 1 | 4.58 s | 787 art/hr | 1363.9 / 91.9 |
| llama3.2:3b | 3.2B (Q4_K_M) | 100% GPU | 10/10 (100%) | 44 | 33 (75.0%) | 2 | 4.5% | 5.6% | 5.0% | 4 | 11 | 2 | 9.35 s | 385 art/hr | 1341.6 / 193.4 |
| qwen2.5:7b | 7.6B (Q4_K_M) | 55%/45% CPU/GPU | 10/10 (100%) | 41 | 10 (24.4%) | 5 | 12.2% | 13.9% | 13.0% | 11 | 33 | 4 | 25.37 s | 142 art/hr | 1363.9 / 185.9 |
| gemini-flash-lite-latest (Cloud Reference) | Cloud Frontier | Cloud API | 10/10 (100%) | 114 | 0 (0.0%) | 29 | 25.4% | 80.6% | 38.7% | 32 | 73 | 24 | 5.71 s | 630 art/hr | 1368.9 / 524.2 |

Note: Detailed article-by-article results are recorded in results/eval_results.csv, and full generation traces are preserved in results/eval_raw_responses.json.
