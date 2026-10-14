Local LLM Research Report (Day 4 Final Results, 14 Oct 2026)
=============================================================

Question: Are local models good enough, fast enough and safe enough to use in our agents? Dummy data only. Ollama listens on localhost only.

Summary
-------

On a 4 GB RTX 3050 laptop GPU, models of 0.5B to 3B parameters run entirely on the GPU at 67 to 214 tokens/sec, with no per-call cost and no data leaving the machine. They are fast enough once loaded. They were not reliable enough for our multi-step tool-using agent: no model gave a fully correct answer on any of the three test tasks. A cold start (first request after unload) costs about 5.5 to 6 s regardless of model size.

1. Hardware
-----------

| Item | Value |
|---|---|
| GPU | NVIDIA GeForce RTX 3050 Laptop, 4096 MiB VRAM |
| CPU | Intel Core i7-12650H |
| RAM | 16 GB |
| Free disk | 53 GB on C: |
| NVIDIA driver | 592.82 (CUDA 13.1) |
| OS | Windows 11 Home Single Language, Build 26200 |

2. Software versions
--------------------

Ollama 0.40.3, Python 3.14.3, requests 2.32.5, pandas 3.0.2. Full list in `requirements.txt`.

3. Models and licences
----------------------

| Model | Params | Quant | Licence | Commercial use |
|---|---|---|---|---|
| qwen2.5:0.5b | 494M | Q4_K_M | Apache 2.0 (Alibaba Cloud) | Yes |
| llama3.2:1b-instruct-q4_K_M | 1.2B | Q4_K_M | Llama 3.2 Community License | Yes, with conditions |
| llama3.2:3b | 3.2B | Q4_K_M | Llama 3.2 Community License | Yes, with conditions |
| llama3.2:1b (extra, v1 only) | 1.2B | Q8_0 | Llama 3.2 Community License | Yes, with conditions |

Licences were read with `ollama show MODEL_NAME --license`. Llama conditions: licence copy and "Built with Llama" attribution if distributed, compliance with Meta's Acceptable Use Policy, and a separate licence above 700M monthly active users. The AUP restricts, among other things, unlicensed professional advice and processing private information without the right to. This is my summary and not legal advice. Legal review is recommended before any production use.

The 1B was first tested at Q8_0 (v1). On Day 2 it was replaced by the Q4_K_M tag so all three models use the same quantization.

4. GPU fit
----------

Method: `ollama run`, `/set parameter num_ctx` before the first message, then `ollama ps` and `nvidia-smi`. Idle baseline: 0 MiB used.

| Model | num_ctx | Size (ollama ps) | Processor | VRAM (MiB) |
|---|---|---|---|---|
| qwen2.5:0.5b | 2048 | 454 MB | 100% GPU | 519 |
| qwen2.5:0.5b | 4096 | 481 MB | 100% GPU | 545 |
| llama3.2:1b (Q8_0) | 2048 | 1.4 GB | 100% GPU | 1465 |
| llama3.2:1b-instruct-q4_K_M | 2048 | not recorded | 100% GPU | 975 (benchmark) |
| llama3.2:3b | 2048 | 2.3 GB | 100% GPU | 2299 (benchmark) |
| llama3.2:3b | 4096 | 2.9 GB | 20%/80% CPU/GPU | 2313 |

The 3B spilled onto the CPU at 4096 context although the card was empty, so the spill comes from the model's own memory need and not from other apps. The 1B Q8 and 0.5B also fit together at 100% GPU (1984 MiB total). Screenshots of `ollama ps` are still to be added.

5. Speed benchmark (warm)
-------------------------

Script: `benchmarks/speed_benchmark.py`. Settings: 5 fixed prompts x 3 runs per model, seed 42, temperature 0, num_ctx 2048, warm-up request excluded, other models unloaded before each model. Data: `results/speed_results_v2.csv` (45 rows).

| Model | Quant | Tokens/sec | TTFT (s) | VRAM (MiB) |
|---|---|---|---|---|
| qwen2.5:0.5b | Q4_K_M | 213.91 | 0.13 | 519 |
| llama3.2:1b-instruct-q4_K_M | Q4_K_M | 149.73 | 0.14 | 975 |
| llama3.2:3b | Q4_K_M | 67.33 | 0.18 | 2299 |

With equal quantization, speed falls steadily as size rises. TTFT here is load duration plus prompt-evaluation duration reported by Ollama, which is only an approximation of true time to first token. Token counts varied between identical runs despite a fixed seed, so outputs were not perfectly deterministic.

Quantization effect on the 1B (same model, Q8_0 vs Q4_K_M):

Data: `results/speed_results_v1_1b-q8.csv` (v1) and `results/speed_results_v2.csv` (v2). Both sets of averages were computed from the CSV files with pandas.

| 1B variant | Tokens/sec | VRAM (MiB) |
|---|---|---|
| Q8_0 (v1) | 110.92 | 1465 |
| Q4_K_M (v2) | 149.73 | 975 |

Q4_K_M was about 35% faster and used about 490 MiB less VRAM. Part of the earlier slowdown of the 1B was therefore quantization and not model size. Answer quality of the Q4 1B on the agent tasks was not tested.

The 0.5B and 3B results in v2 are close to their v1 results (v1: 217.93 and 67.03 tokens/sec; v2: 213.91 and 67.33), which indicates the benchmark is repeatable.

6. Cold start
-------------

Method: `ollama stop MODEL_NAME`, wait until `ollama ps` is empty, then time the first streamed token by wall clock. 3 runs per model, num_ctx 2048, seed 42, temperature 0. Script: `benchmarks/cold_start.py`. Data: `results/cold_start.csv`.

| Model | Cold first token (s) | Load (s) | Individual runs (s) |
|---|---|---|---|
| qwen2.5:0.5b | 5.78 | 3.63 | 6.77, 5.26, 5.31 |
| llama3.2:1b-instruct-q4_K_M | 5.53 | 3.43 | 5.54, 5.57, 5.48 |
| llama3.2:3b | 6.04 | 3.91 | 6.05, 6.01, 6.06 |

Findings:

1. Cold start is about 5.5 to 6 s for every model, so size has little effect. A warm first token took about 0.13 to 0.18 s (approximation from section 5), so the first request after unload is roughly 30 to 40 times slower.
2. About 2 s of each cold start is not covered by Ollama's `load_duration`. The cause was not investigated.
3. The 0.5B run 1 (6.77 s) is an outlier, possibly a cold disk cache (not confirmed).
4. Ollama unloads idle models after 5 minutes by default. Keeping the model loaded (the `keep_alive` setting) should avoid this delay but was not tested.

7. Agent test (original 3 questions, no cloud fallback)
-------------------------------------------------------

The hand-written agent was pointed at `http://localhost:11434/v1`. The change was one new provider entry plus removing the cloud fallback for Ollama. The agent loop and tool definitions were unchanged. Raw logs: `results/agent_original3_raw.txt`. Dummy docs: `agent/docs/`. The llama3.2:1b column is the Q8_0 tag. The llama3.2:1b-instruct-q4_K_M column was run on 13 Oct 2026 with the same three questions and the original docs. Raw log: `results/agent_original3_q4_raw.txt`.

| Task | llama3.2:3b | llama3.2:1b (Q8_0) | llama3.2:1b-instruct-q4_K_M | qwen2.5:0.5b |
|---|---|---|---|---|
| 1. Leave policy (truth: 18 annual, 6 CL, 10 SL, carry-forward 8) | Failed: read_doc called with argument `fn`, tool call leaked as text, no answer | Wrong: invented 20 days, never read the file | Mostly correct: read_doc with filename; 18 days, carry-forward 8, CL 6; omitted 10 sick days and wrongly attached "2 consecutive days" to half-day leave | Mostly correct: 18 days, carry-forward 8, CL 6; omitted 10 sick days |
| 2. Approver above Rs 5,000 and submission days (truth: Director, 30 days) | Partly: 30 days right, approver wrong, file never opened | Wrong: read the wrong file, invented "HR Manager, 10 days" | Failed: tool calls written out as text (malformed JSON), no tool executed, no answer | Partly: 30 days right, approvers confused |
| 3. CEO home address (truth: not in docs) | Refused, did not say "not in docs" | Same refusal | Failed: tool call written out as text, no tool executed, no answer | Tried an invented filename, asked the user for the file |

Time per task: 0.4 to 12.7 s.

Quantization on the 1B: the Q4_K_M tag answered task 1 mostly correctly, where the Q8_0 tag invented facts, but it failed tasks 2 and 3 by writing tool calls as plain text instead of making them (the Q8_0 tag did make calls). With three questions and one run each, this shows that the two versions behave differently on this agent. It does not show that one is better.

Earlier runs on llama3.2:3b with a stricter system prompt and a clearer tool description still failed: the model kept sending `fn` instead of `filename`, and invented answers such as "25 days leave" and a US 401(k) plan.

Findings:

1. Llama models sent a wrong argument name; the Qwen model used `filename` correctly. Tool-calling training mattered more than size.
2. No model said that the documents do not contain the answer.
3. Small models gave confident answers that were not grounded in the documents.
4. Limits: 3 questions, one run each, one agent. This is evidence, not proof for all small models.

8. Problems hit
---------------

- The 3B spilled to CPU at 4096 context. Fixed by using 2048.
- `/set parameter num_ctx` applies only after the model reloads, so set it before the first message.
- Several loaded models added up in VRAM and inflated readings. Fixed with `ollama stop`.
- The first benchmark push uploaded nothing because the files were not in the cloned folder.
- The `processor` column in the CSV has an MB/GB prefix (for example "MB 100% GPU"). The value itself is correct. The script fix is applied for future runs.
- An early agent test used different questions. The original three were re-run for a fair comparison.

9. Recommendation (Days 1 & 2)
------------------------------

- Fast enough: yes, once loaded (67 to 214 tokens/sec). Cold start is about 6 s.
- Safe for data: yes, nothing left the machine.
- Good enough: not on this 4 GB hardware for multi-step tool use.
- Do not replace the cloud model for this agent yet.

10. ICD-10-CM classification benchmark
--------------------------------------

Summary
-------
No: local models on this 4 GB laptop GPU cannot reliably perform clinical ICD-10-CM coding, yielding low exact precision (4.5% to 16.7%) and low recall (2.8% to 13.9%).
On speed, models fully resident on GPU (1.5B and 3B) process an article in 4.4 to 4.6 seconds (~780 to 820 articles/hour), while the 7B model with 55% CPU offload requires 25.4 seconds (~142 articles/hour).
Structured decoding enforces 100% valid JSON adherence across all models, but medical domain validity remains poor with 13.6% to 75.0% invalid or hallucinated codes.
Llama 3.2 3B failed decisively by outputting non-billable range blocks (75% invalid codes), whereas Qwen models predicted discrete encounter-level codes.
Recommendation: do not deploy local small models as autonomous medical coders on edge devices; they may serve only as coarse chapter triage filters or draft suggestion tools.

Setup
-----
- Hardware: NVIDIA GeForce RTX 3050 Laptop GPU (4096 MiB VRAM), 12th Gen Intel Core i7-12650H (16 logical processors), 16 GB DDR4 RAM, Windows 11 Home (Build 26200).
- Ollama version: 0.40.4.
- Models and quantisation: `qwen2.5:1.5b` (Q4_K_M, 100% GPU), `qwen2.5:3b` (Q4_K_M, 100% GPU), `llama3.2:3b` (Q4_K_M, 100% GPU), `qwen2.5:7b` (Q4_K_M, 55%/45% CPU/GPU split).
- Generation settings: Temperature 0, `num_predict: 450`, single run per model on each article. All models stopped before each model run via `ollama stop`.
- Schema: Strict JSON schema (`schema/icd10_schema.json`) requiring `{"conditions": [{"name": str, "icd10cm_code": str, "tier": "primary"|"secondary"|"tertiary"}]}` with `maxItems: 6`.
- Prompt file: `prompts/extraction_prompt_v2.txt` (clinical coding prompt with out-of-key example codes: M54.50, K21.9, R51.9, L20.9, H10.9).

Test set
--------
- 10 full-text health articles from public domain US government sources (NIH: NIDDK and NHLBI, MedlinePlus, CDC), catalogued with URLs and public-domain licences in data/sources.csv.
- Fetching and text curation: Articles were fetched via automated script (scripts/fetch_articles.py) and cleaned to remove web scraping noise (such as broken intra-sentence linebreaks from inline HTML anchor tags, website navigation menus, and dangling links), producing contiguous, readable, and clinically understandable text for model evaluation.
- Article composition: 5 single-condition articles (art_01 to art_05: Asthma, Hypertension, Pneumonia, Alzheimer's, Chronic Kidney Disease) and 5 multi-condition articles (art_06 to art_10: CKD + Diabetes, Metabolic Syndrome, Stroke, COPD, Heart Failure).
- Code table version: CMS FY 2026 ICD-10-CM Tabular Order File (icd10cm_order_2026.txt, effective Oct 1, 2025 to Sept 30, 2026; 98,186 valid classification codes).
- Answer key: Stored in data/answer_key.csv, containing 36 expected condition rows across the 10 articles, with clinical rationale and assigned importance tiers (primary, secondary, tertiary).
- Working draft disclaimer: The answer key was curated by review against the CMS 2026 tabular list and serves as an engineering benchmark draft, not a certified clinical ground truth.

Results table
-------------

| Model | Valid JSON | Codes Returned (Unique) | Invalid Codes | Exact Precision / Recall / F1 | Category Match | Chapter Match | Tier Match | Seconds / Article | Tokens / Article (in / out) |
|---|---|---|---|---|---|---|---|---|---|
| qwen2.5:1.5b | 10/10 (100%) | 18 | 4 (22.2%) | P=16.7% / R=8.3% / F1=11.1% | 6 | 13 | 1 | 4.38 s | 1363.9 / 156.4 |
| qwen2.5:3b | 10/10 (100%) | 22 | 3 (13.6%) | P=4.5% / R=2.8% / F1=3.4% | 6 | 19 | 1 | 4.58 s | 1363.9 / 91.9 |
| llama3.2:3b | 10/10 (100%) | 44 | 33 (75.0%) | P=4.5% / R=5.6% / F1=5.0% | 4 | 11 | 2 | 9.35 s | 1341.6 / 193.4 |
| qwen2.5:7b | 10/10 (100%) | 41 | 10 (24.4%) | P=12.2% / R=13.9% / F1=13.0% | 11 | 33 | 4 | 25.37 s | 1363.9 / 185.9 |
| gemini-flash-lite-latest (Cloud Reference) | 10/10 (100%) | 114 | 0 (0.0%) | P=25.4% / R=80.6% / F1=38.7% | 32 | 73 | 24 | 5.71 s | 1368.9 / 524.2 |

Cloud Reference Comparison and Answer Key Disagreements: gemini-flash-lite-latest had 0 invalid codes across 114 extracted conditions (100% taxonomy validity) and achieved 80.6% recall against the 36 gold-standard codes (29 exact matches). Disagreements with the draft answer key stemmed primarily from: (1) higher clinical specificity (e.g., coding Heart Failure I50.9 and Heart Attack I21.9 instead of unspecified heart disease I51.9 on article 2), (2) unbundled coding rather than combination codes (extracting E11.9 and N18.9 separately instead of combination code E11.22 on article 6), and (3) broader secondary extraction of underlying risk factors (e.g. COVID-19, sepsis, and sickle cell disease in pneumonia). Complete breakdown is preserved in results/gemini_disagreements.md.

Old vs new numbers
------------------
1. Duplicate codes fix: Duplicate code emissions (e.g. `I10;I10;I10`) now count as 1 code and 1 hit; on unique codes, Qwen 1.5B precision dropped from 23.1% to 16.7%, and 7B precision dropped from 26.1% to 12.2%.
2. Recall and F1 fix: Previously uncalculated, exact recall is now tracked against all 36 gold-standard codes, revealing that small models achieve only 2.8% to 13.9% recall (F1 of 3.4% to 13.0%).
3. 7B evaluation fix: `qwen2.5:7b` was previously tested on only 5 articles; it is now evaluated on all 10 articles under identical conditions, allowing a direct head-to-head comparison.
4. Prompt example contamination fix: Replaced the 5 answer-key prompt examples (`I10, E11.9, J45.909, G30.9, N18.9`, which covered 15 of 36 key rows) with out-of-key codes (`M54.50, K21.9, R51.9, L20.9, H10.9`), preventing artificial prompt memorization.
5. Range string and category match fix: Hyphenated ranges (`I10-I15`) are now strictly categorized as invalid with zero credit, and a 3-character category match column is added alongside exact match to measure partial taxonomic alignment.

Failure examples
----------------
1. Range string: `llama3.2:3b` on article 2 (High Blood Pressure) returned `"I10-I15"`, `"I21-I25"`, and `"I63-I66"` (expected discrete code `I10` for Essential hypertension). The model outputted block headings instead of encounter-level diagnosis codes.
2. Invented code: `qwen2.5:1.5b` on article 3 (Pneumonia) generated `"J50.0"` (expected `J18.9` for Pneumonia, unspecified organism). ICD-10-CM Chapter 10 skips from J47 to J60; code `J50.0` does not exist in the official CMS 2026 code table.
3. Wrong tier: `qwen2.5:1.5b` on article 8 (Stroke) generated `I10` (Hypertension) with `tier: "primary"` (expected `tier: "secondary"`, where `I63.9` Cerebral infarction is primary). The model captured the comorbidity but misjudged its clinical centrality in the article.

Throughput
----------
Throughput on this GPU (NVIDIA RTX 3050 Laptop, 4 GB VRAM) computed as `3600 / seconds_per_article`:
- `qwen2.5:1.5b`: 4.38 s/article -> 822 articles per hour (100% GPU)
- `qwen2.5:3b`: 4.58 s/article -> 787 articles per hour (100% GPU)
- `llama3.2:3b`: 9.35 s/article -> 385 articles per hour (100% GPU)
- `qwen2.5:7b`: 25.37 s/article -> 142 articles per hour (55%/45% CPU/GPU offload)

Limits
------
- 10 articles: A small evaluation set focusing on consumer health education articles rather than raw, noisy clinical electronic health records.
- One run each: Evaluations used greedy decoding (temperature 0); non-deterministic run-to-run variance was not measured.
- Draft answer key: Curation relied on single-reviewer clinical matching against the CMS tabular order file rather than dual certified professional medical coder adjudication.
- 4 GB GPU: Limited VRAM forced `qwen2.5:7b` to spill 55% of its weights to CPU and system RAM, causing a 5.8x throughput drop relative to `qwen2.5:1.5b`.

Next steps
----------
- Implement Retrieval-Augmented Generation (RAG) against the 98,186 CMS code descriptions so models retrieve top-k candidate codes instead of hallucinating from parametric memory.
- Add negative prompt constraints and few-shot formatting examples explicitly forbidding hyphenated code ranges.
- Evaluate domain-adapted medical language models (e.g. BioMistral or MedLlama) on larger GPU hardware (8 GB to 16 GB VRAM) to test whether clinical pre-training bridges the accuracy gap.


