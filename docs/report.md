\# Local LLM Research Report (Draft v1, 12 Oct 2026)



\*\*Question:\*\* Are local models good enough, fast enough and safe enough for our agents? Dummy data only.



\## Summary

On a 4 GB RTX 3050, local models of 0.5B to 3B run entirely on the GPU at 67 to 218 tokens/sec with no per-call cost and no data leaving the machine. They are fast enough, but none was reliable enough for our multi-step tool-using agent. No model gave a fully correct answer on any of the three test tasks.



\## 1. Hardware

| Item | Value |

|---|---|

| GPU | NVIDIA GeForce RTX 3050 Laptop, 4096 MiB VRAM |

| CPU | Intel Core i7-12650H |

| RAM | 16 GB |

| Free disk | 53 GB on C: |

| Driver | 592.82 (CUDA 13.1) |

| OS | Windows 11 Home Single Language, Build 26200 |



\## 2. Software versions

Ollama 0.40.3, Python 3.14.3, requests 2.32.5, pandas 3.0.2. Ollama listens on localhost only.



\## 3. Models

| Model | Params | Quant | Licence | Commercial use |

|---|---|---|---|---|

| qwen2.5:0.5b | 494M | Q4\_K\_M | Apache 2.0 (Alibaba Cloud) | Yes |

| llama3.2:1b | 1.2B | Q8\_0 | Llama 3.2 Community License | Yes, with conditions |

| llama3.2:3b | 3.2B | Q4\_K\_M | Llama 3.2 Community License | Yes, with conditions |



Llama conditions: "Built with Llama" attribution and licence copy if distributed, Acceptable Use Policy, separate licence above 700M monthly active users. Summarised by me; not legal advice. Legal review recommended before production use.



Limitation: the 1B uses Q8\_0 while the others use Q4\_K\_M, so its speed and VRAM figures mix size and quantization effects.



\## 4. GPU fit (ollama ps, nvidia-smi)

| Model | num\_ctx | Size | Processor | VRAM (MiB) |

|---|---|---|---|---|

| qwen2.5:0.5b | 2048 | 454 MB | 100% GPU | 519 |

| qwen2.5:0.5b | 4096 | 481 MB | 100% GPU | 545 |

| llama3.2:1b | 2048 | 1.4 GB | 100% GPU | 1465 |

| llama3.2:3b | 2048 | 2.3 GB | 100% GPU | 2299 (benchmark) |

| llama3.2:3b | 4096 | 2.9 GB | 20%/80% CPU/GPU | 2313 |



Idle baseline: 0 MiB. The 3B spill is therefore due to the model's own memory need at 4k context, not other apps. The 1B and 0.5B also fit together at 100% GPU (1984 MiB total).



\## 5. Speed results

Settings: 5 fixed prompts x 3 runs, seed 42, temperature 0, num\_ctx 2048, warm-up excluded. Raw data: `results/speed\_results.csv`.



| Model | Tokens/sec | TTFT (s) | VRAM (MiB) |

|---|---|---|---|

| qwen2.5:0.5b | 217.9 | 0.14 | 519 |

| llama3.2:1b | 110.9 | 0.14 | 1465 |

| llama3.2:3b | 67.0 | 0.17 | 2299 |



(Averages of the 15 runs per model. Verify with the pandas command in setup.md.) Each step up in size roughly halves the speed. TTFT here is load plus prompt-processing time, which is only an approximation of time to first token. Token counts varied between identical runs despite a fixed seed, so outputs were not perfectly deterministic.



\## 6. Agent test (original 3 questions, no cloud fallback)

Raw logs: `results/agent\_original3\_raw.txt`.



| Task | llama3.2:3b | llama3.2:1b | qwen2.5:0.5b |

|---|---|---|---|

| 1. Leave policy (truth: 18 annual, 6 CL, 10 SL, carry-forward 8) | Failed: read\_doc called with `fn`, tool call leaked as text, no answer | Wrong: invented 20 days, never read the file | Mostly correct: 18 days, carry-forward 8, CL 6; omitted 10 sick days |

| 2. Approver above ₹5,000 and submission days (truth: Director, 30 days) | Partly: 30 days right, approver wrong, file never opened | Wrong: read the wrong file, invented "HR Manager, 10 days" | Partly: 30 days right, approvers confused |

| 3. CEO home address (truth: not in docs) | Refused, did not say "not in docs" | Same | Tried invented filename, asked user for file |



Time per task: 0.7 to 12.7 s. Earlier runs on llama3.2:3b with a stronger system prompt and a clearer tool description still failed (argument `fn` instead of `filename`; invented answers such as "25 days leave" and a US 401(k) plan).



Findings:

1\. Switching the agent needed only a new provider entry (base URL http://localhost:11434/v1) and removal of the cloud fallback. The loop and tools were unchanged.

2\. Llama models sent the wrong argument name; Qwen used `filename` correctly. Tool-calling training mattered more than size.

3\. No model said "the docs do not contain this."

4\. Small models gave confident answers that were not grounded in the documents.

5\. Limits: 3 questions, one run each, one agent.



\## 7. Problems hit

\- 3B spilled to CPU at 4096 context; fixed by using 2048.

\- `/set parameter num\_ctx` applies only after the model reloads.

\- Several loaded models inflated VRAM readings; fixed with `ollama stop`.

\- Benchmark push was empty because the files were in a different folder than the clone.

\- CSV `processor` column has an MB/GB prefix (value is correct).

\- At the start, an earlier agent test used different questions; the original three were re-run for a fair comparison.



\## 8. Recommendation

\- Fast enough: yes. Safe for data: yes, nothing left the machine. Good enough: not on this 4 GB hardware for multi-step tool use.

\- Do not replace the cloud model for this agent yet.

\- Next steps: map `fn`/`f`/`doc` to `filename` in code; force read\_doc after search\_docs; test qwen2.5:1.5b/3b (check licences); test 7B to 14B models on a GPU with 8 to 16 GB; run the 4k vs 16k context stretch; add a 1B Q4\_K\_M row.

