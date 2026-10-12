\# Research Log



\## 2026-10-12 (Day 1)

\*\*Done\*\*

\- Collected PC specs; created private repo with the required structure.

\- Installed Ollama 0.40.3. Tested llama3.2:3b, llama3.2:1b, qwen2.5:0.5b at 100% GPU (num\_ctx 2048).

\- Checked licences and quantization for all three models.

\- Wrote and ran the speed benchmark (45 runs). Pushed CSV to GitHub.

\- Pointed the hand-written agent at http://localhost:11434/v1 and ran 3 tasks on each model.



\*\*Found\*\*

\- llama3.2:3b at 4096 context spilled to 20%/80% CPU/GPU on 4 GB VRAM. At 2048 it ran 100% GPU.

\- Speed falls as size rises (about 218, 111, 67 tokens/sec). Time to first token stayed near 0.15 s.

\- No model answered all agent tasks correctly. The Llama models sent the wrong argument name (`fn`) to read\_doc. qwen2.5:0.5b used the correct name.



\*\*Went wrong\*\*

\- Ollama kept several models loaded at once, which inflated VRAM readings.

\- The first benchmark push uploaded nothing because files were in a different folder than the clone.

\- The `processor` CSV column has an MB/GB prefix bug.



\*\*Next\*\*

\- Map `fn` to `filename` in code; force read\_doc after search\_docs.

\- Test qwen2.5:1.5b and qwen2.5:3b (check licences first).

\- Stretch: 4k vs 16k context on llama3.2:1b.

