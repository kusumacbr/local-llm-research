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

9. Recommendation
-----------------

- Fast enough: yes, once loaded (67 to 214 tokens/sec). Cold start is about 6 s.
- Safe for data: yes, nothing left the machine.
- Good enough: not on this 4 GB hardware for multi-step tool use.
- Do not replace the cloud model for this agent yet.
