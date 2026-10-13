Research Log
============

2026-10-12 (Day 1)
------------------

Done:
- Collected PC specs; created private repo with the required structure.
- Installed Ollama 0.40.3. Tested llama3.2:3b, llama3.2:1b, qwen2.5:0.5b at 100% GPU (num_ctx 2048).
- Checked licences and quantization for all three models.
- Wrote and ran the speed benchmark (45 runs). Pushed CSV to GitHub.
- Pointed the hand-written agent at http://localhost:11434/v1 and ran 3 tasks on each model.

Found:
- llama3.2:3b at 4096 context spilled to 20%/80% CPU/GPU on 4 GB VRAM. At 2048 it ran 100% GPU.
- Speed falls as size rises (about 218, 111, 67 tokens/sec). Time to first token stayed near 0.15 s.
- No model answered all agent tasks correctly. The Llama models sent the wrong argument name (`fn`) to read_doc. qwen2.5:0.5b used the correct name.

Went wrong:
- Ollama kept several models loaded at once, which inflated VRAM readings.
- The first benchmark push uploaded nothing because files were in a different folder than the clone.
- The `processor` CSV column has an MB/GB prefix bug.

Next:
- Map `fn` to `filename` in code; force read_doc after search_docs.
- Test qwen2.5:1.5b and qwen2.5:3b (check licences first).
- Stretch: 4k vs 16k context on llama3.2:1b.

2026-10-13 (Day 2)
------------------

Done:
- Curated 10 public-domain health articles from US Government sources (MedlinePlus, CDC, NIH: NIDDK & NHLBI) covering single- and multi-condition topics. Recorded URLs, date read (2026-10-13), and licence statements in `data/sources.csv`. Saved clean article texts in `data/articles/`.
- Downloaded and extracted the official CMS FY 2026 ICD-10-CM code table (`2026-code-descriptions-tabular-order.zip`, 98,186 records) into `data/icd10cm/` and documented download URL and version in `data/icd10cm_metadata.json`.
- Built expert clinical answer key in `data/answer_key.csv` (36 conditions across 10 articles, with primary/secondary/tertiary tiers and verified CMS codes).
- Defined strict JSON Schema `schema/icd10_schema.json` and prompt `prompts/extraction_prompt.txt`.
- Implemented automated evaluation harness `benchmarks/run_eval.py` calling Ollama `/api/chat` with temperature 0 and schema enforcement. Tested `qwen2.5:1.5b`, `qwen2.5:3b`, and `llama3.2:3b` across all 10 articles (30 runs, one run each).
- Generated full metrics in `results/eval_results.csv` and detailed response traces in `results/eval_raw_responses.json`.

Found:
- Schema-constrained decoding achieved 100% valid JSON rate across all models (30/30).
- `qwen2.5:3b` demonstrated superior coding precision with only 1 hallucinated code out of 22 (4.5% invalid rate), compared to 30.8% for `qwen2.5:1.5b` (12/39 invalid) and 64.0% for `llama3.2:3b` (32/50 invalid).
- Llama 3.2 3B consistently hallucinated code ranges (e.g. `I10-I09`, `I11-I13`, `I21-I25`, `J20-J47`) rather than single codes.
- `qwen2.5:1.5b` hallucinated plausibly sounding codes outside the classification (e.g., `J50.0` for pneumonia, when chapter 10 skips J50).
- Qwen models were faster (4.48s and 4.59s per article) than Llama 3.2 3B (7.78s per article).

Went wrong:
- Initial schema lacked `maxItems`, causing `qwen2.5:1.5b` to enter a repetitive generation loop on `art_04` before reaching timeout. Fixed by setting `maxItems: 6` and `num_predict: 450`.
- CDC website blocked automated scraper requests with 403; resolved using pre-cached government reader pipeline and verified public domain statement.

Stretch completed:
- Evaluated `qwen2.5:7b` with 55%/45% CPU/GPU offload on 5 articles (`results/stretch_7b_results.csv`). Average latency was 24.46s per article, achieving 26.1% exact match precision and 100% chapter match rate.

Next:
- Present live demonstration of extraction pipeline (`python benchmarks/run_eval.py --models qwen2.5:3b --article art_01 --live`).
- Synthesize final recommendations for small local models in clinical coding workflows.
