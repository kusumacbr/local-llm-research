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

2026-10-14 (Day 3)
------------------

Done:
- Corrected evaluation scoring: deduplicated model codes per article, added recall and F1 against all 36 gold-standard codes, strictly disqualified hyphenated range strings, and added 3-character category match scoring.
- Replaced answer-key prompt examples with out-of-key codes (`prompts/extraction_prompt_v2.txt`) to eliminate prompt memorization contamination.
- Re-evaluated all 4 local models (`qwen2.5:1.5b`, `qwen2.5:3b`, `llama3.2:3b`, and `qwen2.5:7b`) across all 10 articles under identical settings (`results/eval_results.csv`, `results/eval_raw_responses.json`).
- Evaluated cloud reference model `gemini-flash-lite-latest` across all 10 articles (`results/gemini_reference_results.csv`) and documented disagreements with draft answer key in `results/gemini_disagreements.md`.
- Evaluated cloud reference on the multi-step agent test with 100% ground-truth accuracy (`results/results_original3_gemini-flash-lite-latest.md`).
- Cleaned and curated all 10 articles in `data/articles/` via `scripts/curate_clean_articles.py` to remove web scraping noise, broken HTML line breaks, and navigation text.
- Added automated assertions to `benchmarks/run_eval.py` to verify deduplication, range disqualification, and category matching before every benchmark run.
- Completed final consolidated documentation in `docs/report.md` (including Section 10), `results/summary.md`, `README.md`, and `docs/setup.md`.

Found:
- On unique codes, Qwen 1.5B precision dropped from 23.1% to 16.7% and Qwen 7B precision dropped from 26.1% to 12.2%.
- Small local models achieved only 2.8% to 13.9% recall (F1 of 3.4% to 13.0%) across all 36 gold-standard codes.
- Llama 3.2 3B returned 75.0% invalid codes due to persistent range blocks (e.g. `I10-I15`).
- Qwen 2.5 7B with 55% CPU offload required 25.37 s per article (142 articles/hour), compared to 4.38 s to 4.58 s for GPU-resident 1.5B and 3B models (~800 articles/hour).
- Cloud reference gemini-flash-lite-latest produced 0 invalid codes (100% taxonomy validity) and achieved 80.6% recall (29/36 hits).
- Cloud reference scored 3/3 (100%) on the agent test, while local models failed tool arguments or grounded answering.

Went wrong:
- Ollama CPU offloading for 7B caused a 5.8x throughput drop on 4 GB laptop GPU.
- Range strings were emitted by Llama 3.2 3B even when instructed to extract discrete ICD-10-CM codes.

Next:
- Implement RAG over CMS code descriptions to eliminate parametric hallucination.
- Add negative prompt constraints against hyphenated ranges.
- Test domain-specialized clinical models on larger GPU hardware.

2026-10-21 (Day 4: Fair Comparison Update)
-----------------------------------------

Done:
- Restored real page text for all 10 articles from US Government sources using Trafilatura 2.3.1 with purely mechanical cleaning (stripped navigation menus, breadcrumbs, link URLs, unwrapped glossary modals; 0 added, deleted, or reworded sentences). Archived rewritten summaries to `data/articles_curated_rewritten/`.
- Isolated prompt leakage: Evaluated all 4 local models on identical restored text under Prompt v1 (with in-key hints) vs Prompt v2 (neutral examples). Saved data in `results/eval_results_v1.csv` and `results/prompt_v1_vs_v2_comparison.md`.
- Enforced strict JSON schema (`maxItems: 6`) on Cloud Model (`gemini-flash-lite-latest`) under Gemini OpenAI compatibility, eliminating unconstrained code emission. Saved data in `results/gemini_results_structured_v2.csv`.
- Measured temperature 0 determinism: Repeated both local (`qwen2.5:1.5b`) and cloud (`gemini-flash-lite-latest`) 3 times across all 10 articles. Documented results in `results/repeat_variance_local_1.5b.md` and `results/repeat_variance_cloud_gemini.md`.
- Adjudicated answer key disagreements using official CMS ICD-10-CM coding guidelines (Section I.B.9 combination codes, Section I.B.1 specificity) and Tabular List instructional notes (Excludes1 and "Use additional code"). Updated `data/answer_key.csv` from 36 to 47 conditions (16 row changes) and documented in `results/answer_key_changes.md`.
- Re-scored all model runs against the adjudicated key via `scripts/rescore_all.py` and consolidated final tables into `docs/report.md` and `results/summary.md`.

Found:
- Prompt leakage accounted for virtually all exact match recall on models <= 3B: Qwen 2.5 3B recall fell from 8.5% (v1) to 0.0% (v2), Qwen 1.5B from 12.8% to 2.1%, and Llama 3B from 12.8% to 2.1%. Only Qwen 7B maintained 10.6% recall across both prompts.
- Under equal rules (`maxItems: 6`), Cloud reference Gemini Flash Lite achieved 78.8% exact precision, 87.2% recall (41/47 hits), and 0% taxonomy hallucinations.
- At temperature 0, local models on Ollama are 100% bit-for-bit deterministic (10/10 identical runs), whereas cloud models exhibit run-to-run variance (1/10 identical) due to distributed GPU execution.
- Guideline adjudication affirmed that combination code `E11.22` and stage code `N18.9` must both be reported for diabetic kidney disease, resolving the bundling question.

Went wrong:
- Gemini free-tier rate limit (15 RPM) triggered 429 errors on rapid repeat runs. Solved by introducing a 4.5s pacing delay and exponential retry backoff.

Next:
- Prepare demonstration: side-by-side restored article text vs source page, main table, v1 vs v2, and cloud model under equal rules.

