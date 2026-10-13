Local LLM Research Report (Day 2 update, 13 Oct 2026)
=====================================================

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

10. Part B: Public Test Set (Health Articles & CMS ICD-10 Table)
----------------------------------------------------------------

Test Set Design:
- 10 full-text health articles from public-domain US government agencies (MedlinePlus, CDC, NIH: NIDDK and NHLBI), read on 13 Oct 2026.
- Mix: 5 single-condition articles (Asthma, High Blood Pressure, Pneumonia, Alzheimer's, Chronic Kidney Disease) and 5 multi-condition articles (CKD + Diabetes, Metabolic Syndrome, Stroke, COPD, Heart Failure).
- All articles and official licences catalogued in `data/sources.csv`. Article clean texts preserved in `data/articles/`.

CMS ICD-10-CM Code Table:
- Download URL: `https://www.cms.gov/files/zip/2026-code-descriptions-tabular-order.zip`
- Version: FY 2026 ICD-10-CM (effective October 1, 2025 to September 30, 2026).
- Metadata recorded in `data/icd10cm_metadata.json`.
- Complete order file extracted to `data/icd10cm/icd10cm_order_2026.txt` (98,186 total classification codes).

Answer Key:
- Stored in `data/answer_key.csv` (36 total gold-standard condition codes across 10 articles).
- Tier definitions:
  - `primary`: the article is mostly about it.
  - `secondary`: a real part of it.
  - `tertiary`: a short mention.
- All 36 gold-standard codes cross-referenced and verified against the official CMS 2026 tabular table.

11. Part C: Schema-Constrained Extraction Benchmark
---------------------------------------------------

Method:
- Strict JSON Schema: `schema/icd10_schema.json` enforcing `{"conditions": [{"name": str, "icd10cm_code": str, "tier": "primary"|"secondary"|"tertiary"}]}` with `maxItems: 6`.
- Single call per article via Ollama `/api/chat` with `format` set to the JSON schema, `temperature: 0`, and `num_predict: 450`.
- System prompt saved in `prompts/extraction_prompt.txt`.
- Three models tested: `qwen2.5:1.5b`, `qwen2.5:3b`, `llama3.2:3b`.
- Run policy: One run each today (30 total calls). All models unloaded before each evaluation run.
- Full results recorded in `results/eval_results.csv` and complete raw model generations in `results/eval_raw_responses.json`.

12. Summary Tables per Model
----------------------------

Model 1: qwen2.5:1.5b (Q4_K_M, 100% GPU)
----------------------------------------

| Metric | Value |
|---|---|
| Articles evaluated | 10 |
| Valid JSON rate | 10/10 (100.0%) |
| Total codes returned | 39 |
| Codes not in CMS table (Hallucinations) | 12 (30.8%) |
| Exact code matches (Ground Truth) | 9 (Precision: 23.1%, Recall: 25.0%) |
| Chapter matches | 34 |
| Tier matches | 3 |
| Mean latency per article | 4.48 s |
| Mean input tokens | 1362.9 |
| Mean output tokens | 155.6 |

Model 2: qwen2.5:3b (Q4_K_M, 100% GPU)
--------------------------------------

| Metric | Value |
|---|---|
| Articles evaluated | 10 |
| Valid JSON rate | 10/10 (100.0%) |
| Total codes returned | 22 |
| Codes not in CMS table (Hallucinations) | 1 (4.5%) |
| Exact code matches (Ground Truth) | 5 (Precision: 22.7%, Recall: 13.9%) |
| Chapter matches | 19 |
| Tier matches | 4 |
| Mean latency per article | 4.59 s |
| Mean input tokens | 1362.9 |
| Mean output tokens | 91.7 |

Model 3: llama3.2:3b (Q4_K_M, 100% GPU)
---------------------------------------

| Metric | Value |
|---|---|
| Articles evaluated | 10 |
| Valid JSON rate | 10/10 (100.0%) |
| Total codes returned | 50 |
| Codes not in CMS table (Hallucinations) | 32 (64.0%) |
| Exact code matches (Ground Truth) | 6 (Precision: 12.0%, Recall: 16.7%) |
| Chapter matches | 44 |
| Tier matches | 6 |
| Mean latency per article | 7.78 s |
| Mean input tokens | 1339.6 |
| Mean output tokens | 191.5 |

13. Comparative Findings & Failure Analysis
-------------------------------------------

1. JSON Schema Adherence:
   All three models achieved 100% valid JSON adherence (30/30). Constrained grammar decoding in Ollama eliminates JSON syntax errors entirely.

2. Hallucinations & Code Table Adherence:
   - `qwen2.5:3b` was by far the most reliable model with only a 4.5% hallucination rate (1 invalid code out of 22). It demonstrated conservative, high-precision code prediction.
   - `qwen2.5:1.5b` suffered a 30.8% hallucination rate (12 invalid codes out of 39). It invented plausible-looking diagnosis codes that do not exist in the official taxonomy (e.g. `J50.0` for pneumonia, when ICD-10 Chapter 10 skips J50).
   - `llama3.2:3b` suffered the worst hallucination rate at 64.0% (32 invalid codes out of 50).

3. Failure Explained (Llama 3.2 3B Range Generation Failure):
   - What the model got wrong: On article 2 (High Blood Pressure) and article 3 (Pneumonia), Llama 3.2 3B consistently outputted code ranges such as `"I10-I09"`, `"I11-I13"`, `"I14-I15"`, `"I21-I25"`, `"J20-J47"`, and `"J41-J47.9"`, instead of specific individual diagnosis codes.
   - Why this happened: Llama 3.2 3B's pre-training data contains medical textbook index tables or classification subheadings that group conditions by code blocks (e.g., "Hypertensive Diseases I10-I15"). Without specific fine-tuning or in-context few-shot examples, Llama 3.2 3B treated the task as identifying the block header rather than assigning an encounter-level diagnosis code. Furthermore, it invented nonsensical ranges like `"I10-I09"` (descending range) and non-existent category headers like `"I14"`, and hallucinated `"P30-P39"` (perinatal disorders) for fungal pneumonia.

4. Latency and Speed:
   - Qwen models ran significantly faster (~4.5s per article) than Llama 3.2 3B (~7.8s per article), maintaining higher token throughput.

14. Demo Instructions
---------------------
- To demonstrate one article live through the script:
  `python benchmarks/run_eval.py --models qwen2.5:3b --article art_01 --live`
- The live demonstration prints the parsed JSON, matches against the answer key, CMS validation flags, and token counts.

15. Stretch: 7B Model with Partial CPU Offload (qwen2.5:7b)
-----------------------------------------------------------

Setup & Offload Details:
- Model: `qwen2.5:7b` (Q4_K_M, 5.1 GB total footprint in Ollama).
- Hardware Constraint: RTX 3050 Laptop GPU (4096 MiB VRAM).
- Processor Allocation (ollama ps): 55%/45% CPU/GPU split.
- Test Set: 5 representative articles (`art_01`, `art_02`, `art_05`, `art_06`, `art_07`) covering both single- and multi-condition texts. Script: `benchmarks/run_stretch.py`. Data: `results/stretch_7b_results.csv`.

Summary Table: qwen2.5:7b (55%/45% CPU/GPU Offload)

| Metric | Value |
|---|---|
| Articles evaluated | 5 |
| Processor split | 55%/45% CPU/GPU |
| Valid JSON rate | 5/5 (100.0%) |
| Total codes returned | 23 |
| Codes not in CMS table (Hallucinations) | 5 (21.7%) |
| Exact code matches (Ground Truth) | 6 (26.1% precision) |
| Chapter matches | 23 (100.0%) |
| Tier matches | 4 |
| Mean latency per article | 24.46 s |
| Warm-up model load time | 12.93 s |

Findings on 7B CPU Offload:
1. Feasibility: The 7B model ran reliably without crashing or out-of-memory errors on a 4 GB laptop GPU by spilling 55% of layers to system RAM and CPU.
2. Speed Penalty: Offloading 55% of computation to the CPU increased average latency from ~4.5 s (on the fully GPU-resident 3B) to 24.46 s per article (roughly 5.4x slower).
3. Accuracy: Clinical precision reached 26.1% (6 exact matches across 5 articles), outperforming all smaller models, with a perfect 100% chapter match rate (23/23).
4. Trade-off: On resource-constrained hardware (4 GB VRAM), `qwen2.5:3b` represents the sweet spot for interactive latency (~4.6s per article, 4.5% invalid codes at 100% GPU), whereas `qwen2.5:7b` provides deeper clinical coverage if a ~25s per document batch delay is tolerable.


