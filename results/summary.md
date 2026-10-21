BENCHMARK RESULTS SUMMARY: LOCAL LLM ICD-10-CM EXTRACTION (FAIR COMPARISON UPDATE)
==================================================================================

Metadata:
- Date: 2026-10-21
- Git Commit: 316e4ac (Day 3 Base Commit)
- Hardware: NVIDIA GeForce RTX 3050 Laptop GPU (4096 MiB VRAM), 12th Gen Intel Core i7-12650H, 16 GB RAM
- Software: Windows 11, Ollama 0.40.4, Python 3.14.3, Trafilatura 2.3.1
- Text Preparation: Articles were re-fetched from US government public health sources (MedlinePlus, NIDDK, CDC, NHLBI) and extracted using Trafilatura 2.3.1 with strictly mechanical cleaning: removing navigation menus, breadcrumbs, footers, and link URLs, unwrapping embedded glossary popups, and normalizing broken intra-sentence line breaks. Zero sentences were added, deleted, or reworded.
- Schema: schema/icd10_schema.json (Strict JSON schema requiring conditions list, maxItems: 6, temperature 0)
- Answer Key: 47 ground-truth clinical conditions in data/answer_key.csv, adjudicated under official CMS FY 2026/2027 ICD-10-CM guidelines and tabular notes.
- Scoring Rules: Unique normalized codes per article; range strings (I10-I15) never count; category match = first 3 characters.

----------------------------------------------------------------------------------

WHY EARLIER NUMBERS WERE REPLACED
============================================

Experimental Control Flaws
--------------------------
Three confounding variables previously prevented a fair comparison:

- Rewritten Versus Real Text:
  Articles in scripts/curate_clean_articles.py were rewritten summaries where 9 of 10 articles had 33.5% to 64.7% new words and were approximately 50% shorter than the source page. Real clinical deployment requires processing messy web pages, not synthetic summaries.

- Cloud Model Rule Disparity:
  The cloud reference previously ran in plain JSON mode without schema enforcement or code count limits, emitting up to 32 codes per article (114 total) to achieve 80.6% recall. It is now evaluated under the identical schema constraint (maxItems: 6).

- Prompt Leakage Confounding:
  Prompt v1 contained in-key code examples (I10, E11.9, J45.909, G30.9, N18.9) covering 15 of 36 key rows, artificially inflating small model exact matches. Testing v1 versus v2 on identical text isolates the exact value of the prompt hints.

----------------------------------------------------------------------------------

MAIN PERFORMANCE TABLE
=================================

Restored Text, Prompt v2 Neutral, Strict Schema maxItems 6
----------------------------------------------------------

| Model | Size | Processor | Valid JSON | Unique Codes | Invalid Codes (Hallucinations) | Exact Matches (GT=47) | Exact Precision | Exact Recall | Exact F1 | Category Match (3-char) | Chapter Match | Tier Match | Mean Latency / Art | Throughput |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen2.5:1.5b | 1.5B (Q4_K_M) | 100% GPU | 10/10 (100%) | 18 | 8 (44.4%) | 1 | 5.6% | 2.1% | 3.1% | 4 | 14 | 1 | 4.26 s | 844 art/hr |
| qwen2.5:3b | 3.2B (Q4_K_M) | 100% GPU | 10/10 (100%) | 19 | 4 (21.1%) | 0 | 0.0% | 0.0% | 0.0% | 6 | 16 | 0 | 4.25 s | 847 art/hr |
| llama3.2:3b | 3.2B (Q4_K_M) | 100% GPU | 10/10 (100%) | 40 | 30 (75.0%) | 1 | 2.5% | 2.1% | 2.3% | 4 | 14 | 1 | 7.38 s | 488 art/hr |
| qwen2.5:7b | 7.6B (Q4_K_M) | 55%/45% CPU/GPU | 10/10 (100%) | 30 | 11 (36.7%) | 5 | 16.7% | 10.6% | 13.0% | 15 | 22 | 5 | 18.85 s | 191 art/hr |
| gemini-flash-lite-latest | Cloud Frontier | Cloud API | 10/10 (100%) | 52 | 0 (0.0%) | 41 | 78.8% | 87.2% | 82.8% | 43 | 49 | 36 | 1.94 s | 1853 art/hr |

- Key Takeaway on Main Benchmark:
  Under identical rules, the cloud reference achieves 78.8% precision, 87.2% recall, and 0% taxonomy hallucinations. Local small models cannot reliably perform standalone clinical coding without external retrieval.

----------------------------------------------------------------------------------

ONE CHANGE AT A TIME (PROMPT ISOLATION)
==================================================

Prompt v1 (With Hints) Versus Prompt v2 (Neutral Examples)
----------------------------------------------------------
Both runs evaluated on identical restored real text under the 47-condition adjudicated answer key:

| Model | Prompt Variant | Codes Returned | Invalid Codes | Exact Matches | Exact Precision | Exact Recall | F1 Score | Cat Matches | Mean Latency |
|---|---|---|---|---|---|---|---|---|---|
| qwen2.5:1.5b | v1 (with hints) | 20 | 7 (35.0%) | 6 | 30.0% | 12.8% | 17.9% | 9 | 4.19 s |
| qwen2.5:1.5b | v2 (neutral) | 18 | 8 (44.4%) | 1 | 5.6% | 2.1% | 3.1% | 4 | 4.26 s |
| qwen2.5:3b | v1 (with hints) | 20 | 2 (10.0%) | 4 | 20.0% | 8.5% | 11.9% | 9 | 4.36 s |
| qwen2.5:3b | v2 (neutral) | 19 | 4 (21.1%) | 0 | 0.0% | 0.0% | 0.0% | 6 | 4.25 s |
| llama3.2:3b | v1 (with hints) | 37 | 22 (59.5%) | 6 | 16.2% | 12.8% | 14.3% | 8 | 8.37 s |
| llama3.2:3b | v2 (neutral) | 40 | 30 (75.0%) | 1 | 2.5% | 2.1% | 2.3% | 4 | 7.38 s |
| qwen2.5:7b | v1 (with hints) | 31 | 6 (19.4%) | 5 | 16.1% | 10.6% | 12.8% | 17 | 18.54 s |
| qwen2.5:7b | v2 (neutral) | 30 | 11 (36.7%) | 5 | 16.7% | 10.6% | 13.0% | 15 | 18.85 s |

- Analysis of Prompt Leakage:
  Prompt hints in v1 artificially created almost all exact matches for models less than or equal to 3B (qwen2.5:3b dropped from 4 hits to 0; qwen2.5:1.5b dropped from 6 to 1; llama3.2:3b dropped from 6 to 1). Only qwen2.5:7b maintained its 5 exact matches across both prompts, showing genuine article comprehension.

----------------------------------------------------------------------------------

TEMPERATURE 0 REPEAT VARIANCE
========================================

Determinism Across 3 Repeated Runs
----------------------------------

- Local Model Determinism:
  Local Model (qwen2.5:1.5b): 10/10 (100.0%) identical across all 3 runs. Zero variance; outputs are 100% bit-for-bit deterministic.

- Cloud Model Determinism:
  Cloud Model (gemini-flash-lite-latest): 1/10 (10.0%) identical across all 3 runs. 9 of 10 articles showed slight output variations (token ordering, formatting spaces) due to cloud-side MoE batch routing and distributed GPU floating-point non-determinism.

----------------------------------------------------------------------------------

ANSWER KEY ADJUDICATION SUMMARY
==========================================

Official ICD-10-CM Standards Alignment
--------------------------------------
The answer key was updated from 36 to 47 conditions in data/answer_key.csv (16 total row operations: 13 added, 4 replaced, 1 removed). Full line-by-line clinical rationales are preserved in results/answer_key_changes.md:

- Combination Codes (Guideline I.B.9):
  Kept E11.22 (Type 2 diabetes with diabetic CKD) on art_06. Tabular notes under E11.22 instruct "Use additional code to identify stage of CKD (N18.1-N18.6)"; therefore, N18.9 is also retained as the mandatory secondary code.

- Clinical Specificity (Guideline I.B.1):
  On art_02, removed vague umbrella code I51.9 (Heart disease, unspecified) and replaced with explicitly documented conditions: I50.9 (Heart failure), I21.9 (Heart attack), and N19 (Kidney failure).

- Tabular Instructional Notes:
  On art_04, replaced F03.90 with F02.80 because Tabular note under G30 mandates "Use additional code F02.8-" and F03 has an Excludes1 conflict.

- Restored Article Fidelity:
  Removed J45.909 (Asthma) from art_09 (only present in rewritten summary); added E88.01 (Alpha-1-antitrypsin deficiency) which is explicitly in the source text.
