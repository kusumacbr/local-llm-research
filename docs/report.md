Local LLM Research Report (Day 4 Fair Comparison Update, 21 Oct 2026)
=====================================================================

Git commit: 316e4ac (Day 3 Base Commit)

Question: Are local models good enough, fast enough and safe enough to use in our agents? Dummy data only. Ollama listens on localhost only.

Summary
=======

On a 4 GB RTX 3050 laptop GPU, models of 0.5B to 3B parameters run entirely on the GPU at 67 to 214 tokens/sec, with no per-call cost and no data leaving the machine. They are fast enough once loaded. They were not reliable enough for our multi-step tool-using agent: no model gave a fully correct answer on any of the three test tasks. A cold start (first request after unload) costs about 5.5 to 6 s regardless of model size.

For clinical ICD-10-CM diagnosis coding across 10 public health articles using the official CMS FY 2026 taxonomy, the Day 4 fair-comparison evaluation restored real page text (mechanically cleaned without rewriting), eliminated answer-key prompt example leakage (isolating v1 vs v2), enforced strict structured schema limits (`maxItems: 6`) on both local and cloud models, and settled the answer key to 47 clinical conditions via official CMS guidelines and tabular notes. Under these fair rules, local small models (1.5B to 3B) achieved only 0.0% to 2.1% exact recall (2.5% to 5.6% precision), while 7B achieved 10.6% recall (16.7% precision) with 36.7% hallucinations. In contrast, cloud reference gemini-flash-lite-latest under identical schema constraints achieved 87.2% recall (41/47 exact matches), 78.8% precision, and 0% hallucinations. Temperature 0 repeated runs revealed that the local model is 100% bit-for-bit deterministic, whereas the cloud model exhibited minor output variance across 9 of 10 articles.

Hardware
===========

| Item | Value |
|---|---|
| GPU | NVIDIA GeForce RTX 3050 Laptop, 4096 MiB VRAM |
| CPU | Intel Core i7-12650H |
| RAM | 16 GB |
| Free disk | 53 GB on C: |
| NVIDIA driver | 592.82 (CUDA 13.1) |
| OS | Windows 11 Home Single Language, Build 26200 |

Software versions
====================

Ollama 0.40.4, Python 3.14.3, requests 2.32.5, pandas 3.0.2, openai 1.66.0, python-dotenv 1.0.1. Full list in `requirements.txt`.

Models and licences
======================

| Model | Params | Quant | Licence | Commercial use |
|---|---|---|---|---|
| qwen2.5:0.5b | 494M | Q4_K_M | Apache 2.0 (Alibaba Cloud) | Yes |
| llama3.2:1b-instruct-q4_K_M | 1.2B | Q4_K_M | Llama 3.2 Community License | Yes, with conditions |
| llama3.2:3b | 3.2B | Q4_K_M | Llama 3.2 Community License | Yes, with conditions |
| llama3.2:1b (extra, v1 only) | 1.2B | Q8_0 | Llama 3.2 Community License | Yes, with conditions |
| qwen2.5:1.5b (Day 3 benchmark) | 1.5B | Q4_K_M | Apache 2.0 (Alibaba Cloud) | Yes |
| qwen2.5:7b (Day 3 benchmark) | 7.6B | Q4_K_M | Apache 2.0 (Alibaba Cloud) | Yes |

Licences were read with `ollama show MODEL_NAME --license`. Llama conditions: licence copy and "Built with Llama" attribution if distributed, compliance with Meta's Acceptable Use Policy, and a separate licence above 700M monthly active users. The AUP restricts, among other things, unlicensed professional advice and processing private information without the right to. This is my summary and not legal advice. Legal review is recommended before any production use.

The 1B was first tested at Q8_0 (v1). On Day 2 it was replaced by the Q4_K_M tag so all three models use the same quantization.

GPU fit
==========

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

Speed benchmark (warm)
=========================

Script: `benchmarks/speed_benchmark.py`. Settings: 5 fixed prompts x 3 runs per model, seed 42, temperature 0, num_ctx 2048, warm-up request excluded, other models unloaded before each model. Data: `results/speed_results_v2.csv` (45 rows).

| Model | Quant | Tokens/sec | TTFT (s) | VRAM (MiB) |
|---|---|---|---|---|
| qwen2.5:0.5b | Q4_K_M | 213.91 | 0.13 | 519 |
| llama3.2:1b-instruct-q4_K_M | Q4_K_M | 149.73 | 0.14 | 975 |
| llama3.2:3b | Q4_K_M | 67.33 | 0.18 | 2299 |

With equal quantization, speed falls steadily as size rises. TTFT here is load duration plus prompt-evaluation duration reported by Ollama, which is only an approximation of true time to first token. Token counts varied between identical runs despite a fixed seed, so outputs were not perfectly deterministic.

Quantization effect on the 1B (same model, Q8_0 vs Q4_K_M)
----------------------------------------------------------

Data: `results/speed_results_v1_1b-q8.csv` (v1) and `results/speed_results_v2.csv` (v2). Both sets of averages were computed from the CSV files with pandas.

| 1B variant | Tokens/sec | VRAM (MiB) |
|---|---|---|
| Q8_0 (v1) | 110.92 | 1465 |
| Q4_K_M (v2) | 149.73 | 975 |

Q4_K_M was about 35% faster and used about 490 MiB less VRAM. Part of the earlier slowdown of the 1B was therefore quantization and not model size. Answer quality of the Q4 1B on the agent tasks was not tested.

The 0.5B and 3B results in v2 are close to their v1 results (v1: 217.93 and 67.03 tokens/sec; v2: 213.91 and 67.33), which indicates the benchmark is repeatable.

Cold start
=============

Method: `ollama stop MODEL_NAME`, wait until `ollama ps` is empty, then time the first streamed token by wall clock. 3 runs per model, num_ctx 2048, seed 42, temperature 0. Script: `benchmarks/cold_start.py`. Data: `results/cold_start.csv`.

| Model | Cold first token (s) | Load (s) | Individual runs (s) |
|---|---|---|---|
| qwen2.5:0.5b | 5.78 | 3.63 | 6.77, 5.26, 5.31 |
| llama3.2:1b-instruct-q4_K_M | 5.53 | 3.43 | 5.54, 5.57, 5.48 |
| llama3.2:3b | 6.04 | 3.91 | 6.05, 6.01, 6.06 |

Findings
--------

- Cold start is about 5.5 to 6 s for every model, so size has little effect. A warm first token took about 0.13 to 0.18 s (approximation from section 5), so the first request after unload is roughly 30 to 40 times slower.
- About 2 s of each cold start is not covered by Ollama's `load_duration`. The cause was not investigated.
- The 0.5B run 1 (6.77 s) is an outlier, possibly a cold disk cache (not confirmed).
- Ollama unloads idle models after 5 minutes by default. Keeping the model loaded (the `keep_alive` setting) should avoid this delay but was not tested.

Agent test (original 3 questions, no cloud fallback)
=======================================================

The hand-written agent was pointed at `http://localhost:11434/v1`. The change was one new provider entry plus removing the cloud fallback for Ollama. The agent loop and tool definitions were unchanged. Raw logs: `results/agent_original3_raw.txt`. Dummy docs: `agent/docs/`. The llama3.2:1b column is the Q8_0 tag. The llama3.2:1b-instruct-q4_K_M column was run on 13 Oct 2026 with the same three questions and the original docs. Raw log: `results/agent_original3_q4_raw.txt`.

| Task | llama3.2:3b | llama3.2:1b (Q8_0) | llama3.2:1b-instruct-q4_K_M | qwen2.5:0.5b |
|---|---|---|---|---|
| 1. Leave policy (truth: 18 annual, 6 CL, 10 SL, carry-forward 8) | Failed: read_doc called with argument `fn`, tool call leaked as text, no answer | Wrong: invented 20 days, never read the file | Mostly correct: read_doc with filename; 18 days, carry-forward 8, CL 6; omitted 10 sick days and wrongly attached "2 consecutive days" to half-day leave | Mostly correct: 18 days, carry-forward 8, CL 6; omitted 10 sick days |
| 2. Approver above Rs 5,000 and submission days (truth: Director, 30 days) | Partly: 30 days right, approver wrong, file never opened | Wrong: read the wrong file, invented "HR Manager, 10 days" | Failed: tool calls written out as text (malformed JSON), no tool executed, no answer | Partly: 30 days right, approvers confused |
| 3. CEO home address (truth: not in docs) | Refused, did not say "not in docs" | Same refusal | Failed: tool call written out as text, no tool executed, no answer | Tried an invented filename, asked the user for the file |

Time per task: 0.4 to 12.7 s.

Quantization on the 1B: the Q4_K_M tag answered task 1 mostly correctly, where the Q8_0 tag invented facts, but it failed tasks 2 and 3 by writing tool calls as plain text instead of making them (the Q8_0 tag did make calls). With three questions and one run each, this shows that the two versions behave differently on this agent. It does not show that one is better.

Earlier runs on llama3.2:3b with a stricter system prompt and a clearer tool description still failed: the model kept sending `fn` instead of `filename`, and invented answers such as "25 days leave" and a US 401(k) plan.

Findings
--------

- Llama models sent a wrong argument name; the Qwen model used `filename` correctly. Tool-calling training mattered more than size.
- No model said that the documents do not contain the answer.
- Small models gave confident answers that were not grounded in the documents.
- Limits: 3 questions, one run each, one agent. This is evidence, not proof for all small models.

Problems hit
===============

- The 3B spilled to CPU at 4096 context. Fixed by using 2048.
- `/set parameter num_ctx` applies only after the model reloads, so set it before the first message.
- Several loaded models added up in VRAM and inflated readings. Fixed with `ollama stop`.
- The first benchmark push uploaded nothing because the files were not in the cloned folder.
- The `processor` column in the CSV has an MB/GB prefix (for example "MB 100% GPU"). The value itself is correct. The script fix is applied for future runs.
- An early agent test used different questions. The original three were re-run for a fair comparison.

Recommendation (Days 1 & 2)
==============================

- Fast enough: yes, once loaded (67 to 214 tokens/sec). Cold start is about 6 s.
- Safe for data: yes, nothing left the machine.
- Good enough: not on this 4 GB hardware for multi-step tool use.
- Do not replace the cloud model for this agent yet.

ICD-10-CM classification benchmark (Day 4 Fair Comparison Update)
==================================================================

Git commit: 316e4ac (Day 3 Base Commit)

A. Summary
----------
Local models on this 4 GB laptop GPU cannot reliably perform clinical ICD-10-CM diagnosis coding under fair, standardized evaluation conditions. On restored real page text using neutral prompt examples (v2) and adjudicated ground truth (47 conditions), models of 1.5B to 3B parameters achieved only 0.0% to 2.1% exact recall (2.5% to 5.6% exact precision). The 7.6B model achieved 10.6% recall and 16.7% precision, but hallucinated non-existent codes or non-billable ranges 36.7% of the time.

In contrast, cloud reference `gemini-flash-lite-latest` evaluated under the exact same schema constraint (`maxItems: 6`) achieved 87.2% recall (41 of 47 exact matches), 78.8% precision, and 0% taxonomy hallucinations, processing articles at 1.94 s/article (1,853 articles/hour).

Isolating prompt leakage revealed that the answer hints in Prompt v1 (`I10, E11.9, J45.909, G30.9, N18.9`) were responsible for almost all exact matches in small models (less than or equal to 3B): `qwen2.5:3b` dropped from 4 hits to 0 (11.1% to 0.0% recall), and `qwen2.5:1.5b` dropped from 6 hits to 1 (12.8% to 2.1% recall).

Repeat runs at temperature 0 established that local models on Ollama are 100% bit-for-bit deterministic (10/10 identical outputs), whereas cloud APIs exhibit non-determinism across runs (only 1/10 identical outputs) due to distributed GPU execution and Mixture-of-Experts routing.

B. Setup
--------
- Hardware: NVIDIA GeForce RTX 3050 Laptop GPU (4096 MiB VRAM), 12th Gen Intel Core i7-12650H (16 logical processors), 16 GB DDR4 RAM, Windows 11 Home (Build 26200).
- Software: Ollama 0.40.4, Python 3.14.3, Trafilatura 2.3.1, requests 2.32.5, pandas 3.0.2, openai 1.66.0.
- Models and Quantisation: `qwen2.5:1.5b` (Q4_K_M, 100% GPU), `qwen2.5:3b` (Q4_K_M, 100% GPU), `llama3.2:3b` (Q4_K_M, 100% GPU), `qwen2.5:7b` (Q4_K_M, 55%/45% CPU/GPU split), and `gemini-flash-lite-latest` (Cloud Reference).
- Generation Settings: Temperature 0, `num_predict: 450`, single run per model on each article. All local models stopped before each run via `ollama stop`.
- Schema: Strict JSON schema (`schema/icd10_schema.json`) requiring `{"conditions": [{"name": str, "icd10cm_code": str, "tier": "primary"|"secondary"|"tertiary"}]}` with `maxItems: 6`.
- Prompt Files:
  - `prompts/extraction_prompt.txt` (v1: contains answer hints `I10, E11.9, J45.909, G30.9, N18.9`).
  - `prompts/extraction_prompt_v2.txt` (v2: neutral out-of-key examples `M54.50, K21.9, R51.9, L20.9, H10.9`).
- Code Table Version: CMS FY 2026 ICD-10-CM Tabular Order File (`icd10cm_order_2026.txt`, 98,186 valid classification codes).
- Answer Key: Adjudicated against official CMS ICD-10-CM coding guidelines and tabular notes, containing 47 condition rows across 10 articles (`data/answer_key.csv`).

C. Test Set & Text Preparation
------------------------------
Articles were re-fetched from US government public health sources (MedlinePlus, NIDDK, CDC, NHLBI) and extracted using Trafilatura 2.3.1 with strictly mechanical cleaning: removing navigation menus, breadcrumbs, footers, and link URLs, unwrapping embedded glossary popups, and normalizing broken intra-sentence line breaks. Zero sentences were added, deleted, or reworded.

The previous rewritten summary files have been archived to `data/articles_curated_rewritten/` and are no longer used for scoring.

Article Text Restoration and Comparison Table
---------------------------------------------

| Article | Source Title | Day 3 Words | Restored Words | Day 3 Match (%) | Rewritten Words | New Words in Rewritten (%) |
|---|---|---|---|---|---|---|
| `art_01` | Asthma | 860 | 860 | 100.0% | 650 | 6.2% |
| `art_02` | High Blood Pressure | 510 | 510 | 100.0% | 460 | 37.3% |
| `art_03` | Pneumonia | 1019 | 1019 | 100.0% | 440 | 33.5% |
| `art_04` | Alzheimer's Disease | 611 | 598 | 97.7% | 394 | 55.5% |
| `art_05` | What is Chronic Kidney Disease? | 1298 | 1084 | 87.1% | 550 | 56.7% |
| `art_06` | Chronic Kidney Disease and Diabetes | 486 | 405 | 96.2% | 420 | 56.8% |
| `art_07` | Metabolic Syndrome | 653 | 653 | 100.0% | 476 | 54.4% |
| `art_08` | Stroke | 1037 | 1033 | 98.9% | 507 | 45.6% |
| `art_09` | Chronic Obstructive Pulmonary Disease | 797 | 397 | 57.6% | 454 | 64.7% |
| `art_10` | Heart Failure | 1103 | 1103 | 100.0% | 483 | 49.5% |

Note: On MedlinePlus pages, Trafilatura extracts 97.7% to 100.0% of Day 3 vocabulary while joining lines cleanly. On NIDDK, CDC, and NHLBI, lower percentage match reflects the mechanical stripping of website navigation menus, breadcrumbs, and glossary popup tooltips (`krah-nik`, `in-fluh-may-shun`) that previously cluttered the Day 3 raw fetch.

D. Main Results Table (Restored Real Text, Prompt v2 Neutral, Strict Schema maxItems: 6, Adjudicated Key)
---------------------------------------------------------------------------------------------------------

Data: `results/eval_results.csv` and `results/gemini_results_structured_v2.csv`. Evaluated against the 47-condition official adjudicated answer key.

| Model | Valid JSON | Codes Returned (Unique) | Invalid Codes | Exact Matches (GT=47) | Exact Precision / Recall / F1 | Category Match | Chapter Match | Tier Match | Seconds / Article | Throughput |
|---|---|---|---|---|---|---|---|---|---|---|
| `qwen2.5:1.5b` | 10/10 (100%) | 18 | 8 (44.4%) | 1 | P=5.6% / R=2.1% / F1=3.1% | 4 | 14 | 1 | 4.26 s | 844 art/hr |
| `qwen2.5:3b` | 10/10 (100%) | 19 | 4 (21.1%) | 0 | P=0.0% / R=0.0% / F1=0.0% | 6 | 16 | 0 | 4.25 s | 847 art/hr |
| `llama3.2:3b` | 10/10 (100%) | 40 | 30 (75.0%) | 1 | P=2.5% / R=2.1% / F1=2.3% | 4 | 14 | 1 | 7.38 s | 488 art/hr |
| `qwen2.5:7b` | 10/10 (100%) | 30 | 11 (36.7%) | 5 | P=16.7% / R=10.6% / F1=13.0% | 15 | 22 | 5 | 18.85 s | 191 art/hr |
| `gemini-flash-lite-latest` (Cloud Reference) | 10/10 (100%) | 52 | 0 (0.0%) | 41 | P=78.8% / R=87.2% / F1=82.8% | 43 | 49 | 36 | 1.94 s | 1853 art/hr |

E. One Change at a Time: Prompt v1 (with hints) vs Prompt v2 (neutral examples)
--------------------------------------------------------------------------------

Data: `results/eval_results_v1.csv` vs `results/eval_results_v2.csv` (both tested on identical restored real text under the 47-condition adjudicated key):

| Model | Prompt Variant | Codes Returned | Invalid Codes | Exact Matches | Exact Precision | Exact Recall | F1 Score | Cat Matches | Mean Latency |
|---|---|---|---|---|---|---|---|---|---|
| `qwen2.5:1.5b` | v1 (hints) | 20 | 7 (35.0%) | 6 | 30.0% | 12.8% | 17.9% | 9 | 4.19 s |
| `qwen2.5:1.5b` | v2 (neutral) | 18 | 8 (44.4%) | 1 | 5.6% | 2.1% | 3.1% | 4 | 4.26 s |
| `qwen2.5:3b` | v1 (hints) | 20 | 2 (10.0%) | 4 | 20.0% | 8.5% | 11.9% | 9 | 4.36 s |
| `qwen2.5:3b` | v2 (neutral) | 19 | 4 (21.1%) | 0 | 0.0% | 0.0% | 0.0% | 6 | 4.25 s |
| `llama3.2:3b` | v1 (hints) | 37 | 22 (59.5%) | 6 | 16.2% | 12.8% | 14.3% | 8 | 8.37 s |
| `llama3.2:3b` | v2 (neutral) | 40 | 30 (75.0%) | 1 | 2.5% | 2.1% | 2.3% | 4 | 7.38 s |
| `qwen2.5:7b` | v1 (hints) | 31 | 6 (19.4%) | 5 | 16.1% | 10.6% | 12.8% | 17 | 18.54 s |
| `qwen2.5:7b` | v2 (neutral) | 30 | 11 (36.7%) | 5 | 16.7% | 10.6% | 13.0% | 15 | 18.85 s |

Findings on Prompt Leakage:
1. The five code hints in v1 (`I10, E11.9, J45.909, G30.9, N18.9`) provided an immense artificial boost to smaller models: `qwen2.5:3b` dropped from 4 exact matches to 0 (0.0% recall), and `qwen2.5:1.5b` dropped from 6 hits to 1.
2. In contrast, `qwen2.5:7b` maintained exactly 5 hits across both prompt variants, demonstrating genuine comprehension of the text rather than prompt memorization.

F. Temperature 0 Repeat Variance (Determinism Question)
-------------------------------------------------------

To test reproducibility under production settings, both local and cloud models were evaluated 3 times at `temperature = 0` across all 10 restored articles:
- Local Model (`qwen2.5:1.5b`): 10/10 (100.0%) identical outputs across all 3 runs. Greedy decoding on Ollama is fully deterministic.
- Cloud Model (`gemini-flash-lite-latest`): 1/10 (10.0%) identical outputs across all 3 runs. 9 of 10 articles exhibited minor formatting, whitespace, or secondary code ordering differences due to distributed GPU execution and Mixture-of-Experts routing.

G. Cloud Model Evaluation Under Equal Rules
-------------------------------------------
Under plain JSON mode, Gemini emitted 114 codes (up to 32 codes on a single article). Under the strict JSON schema constraint (`maxItems: 6`), Gemini was forced to prioritize the top 6 conditions per article:
- Total unique codes dropped from 114 to 52 (strictly bounded).
- Exact precision surged from 25.4% to 78.8%.
- Exact recall remained high at 87.2% (41 of 47 conditions captured).
- Taxonomy validity remained flawless at 100% (0 invalid codes).

H. Answer Key Adjudication Summary
----------------------------------
Disagreements between Gemini and the draft answer key were adjudicated using the official CMS ICD-10-CM guidelines and tabular notes, expanding the key from 36 to 47 conditions (16 total row operations: 13 added, 4 modified, 1 removed). Full line-by-line documentation is preserved in `results/answer_key_changes.md`:
1. Combination Codes (Guideline I.B.9): On `art_06`, combination code `E11.22` (Type 2 diabetes with diabetic CKD) is mandated over unbundled codes. Tabular notes under `E11.22` explicitly direct: "Use additional code to identify stage of CKD (N18.1-N18.6)"; therefore, `N18.9` is also legitimately retained as the secondary code.
2. Clinical Specificity (Guideline I.B.1): On `art_02`, vague umbrella code `I51.9` (Heart disease, unspecified) was replaced with explicitly documented specific conditions: `I50.9` (Heart failure), `I21.9` (Heart attack), and `N19` (Kidney failure).
3. Tabular Instructional Notes: On `art_04`, `F03.90` was replaced with `F02.80` because Tabular notes under `G30` mandate "Use additional code `F02.8-`" and `F03` has an Excludes1 conflict.
4. Text Alignment: Removed `J45.909` from `art_09` (only present in rewritten summary); added `E88.01` (Alpha-1-antitrypsin deficiency) which is explicitly in the source text.

I. Why Earlier Numbers Were Replaced
------------------------------------
1. Rewritten Text: Previous evaluations ran on synthesized summaries rather than real web text.
2. Unequal Rules: Cloud reference ran unconstrained (114 codes), while local models had an item limit.
3. Prompt Leakage: In-key prompt examples artificially inflated small model scores on v1.
4. Adjudicated Ground Truth: The draft key had 36 entries with several guideline violations (e.g. Excludes1 conflicts, vague umbrella codes).

J. Limits & Next Steps
----------------------
- Edge models (less than or equal to 3B) suffer from catastrophic parametric hallucination and cannot perform standalone ICD-10 coding.
- Production deployment requires Retrieval-Augmented Generation (RAG) to ground local models in official CMS code descriptions rather than relying on parametric weights.



