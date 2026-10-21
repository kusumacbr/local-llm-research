Prompt v1 vs Prompt v2 Benchmark Comparison (Adjudicated Key)

Evaluation across all 10 restored articles rescored against the 47-condition official adjudicated ICD-10-CM answer key.

| Model | Prompt | Codes Returned | Invalid Codes | Exact Matches | Exact Precision | Exact Recall | F1 Score | Cat Matches | Mean Latency |
|---|---|---|---|---|---|---|---|---|---|
| qwen2.5:1.5b | v1 (hints) | 20 | 7 (35.0%) | 6 | 30.0% | 12.8% | 17.9% | 9 | 4.19 s |
| qwen2.5:1.5b | v2 (neutral) | 18 | 8 (44.4%) | 1 | 5.6% | 2.1% | 3.1% | 4 | 4.26 s |
| qwen2.5:3b | v1 (hints) | 20 | 2 (10.0%) | 4 | 20.0% | 8.5% | 11.9% | 9 | 4.36 s |
| qwen2.5:3b | v2 (neutral) | 19 | 4 (21.1%) | 0 | 0.0% | 0.0% | 0.0% | 6 | 4.25 s |
| llama3.2:3b | v1 (hints) | 37 | 22 (59.5%) | 6 | 16.2% | 12.8% | 14.3% | 8 | 8.37 s |
| llama3.2:3b | v2 (neutral) | 40 | 30 (75.0%) | 1 | 2.5% | 2.1% | 2.3% | 4 | 7.38 s |
| qwen2.5:7b | v1 (hints) | 31 | 6 (19.4%) | 5 | 16.1% | 10.6% | 12.8% | 17 | 18.54 s |
| qwen2.5:7b | v2 (neutral) | 30 | 11 (36.7%) | 5 | 16.7% | 10.6% | 13.0% | 15 | 18.85 s |
