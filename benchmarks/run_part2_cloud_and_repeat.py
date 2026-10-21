import os
import sys
sys.path.insert(0, os.path.abspath("."))
import json
import time
import glob
import csv
import subprocess
from dotenv import load_dotenv
from openai import OpenAI

from benchmarks.run_eval import (
    load_cms_code_table,
    load_answer_key,
    load_sources,
    evaluate_prediction,
    run_article_call,
    unload_model,
    print_model_summary_table,
    normalize_code,
    DEFAULT_MODELS,
    ARTICLES_DIR,
    SCHEMA_FILE,
    RESULTS_DIR
)

load_dotenv()

PROMPT_V1_FILE = os.path.join("prompts", "extraction_prompt.txt")
PROMPT_V2_FILE = os.path.join("prompts", "extraction_prompt_v2.txt")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
CLOUD_MODEL_NAME = "gemini-flash-lite-latest"

def save_csv(rows, out_path):
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved {len(rows)} rows to {out_path}")

def run_cloud_evaluation_safe(prompt_file, run_label, schema, cms_table, answer_key, sources, article_files, repeat_count=3):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set.")

    client = OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=GEMINI_API_KEY,
        timeout=60.0
    )

    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    print(f"\n=======================================================")
    print(f" Running Cloud Model ({CLOUD_MODEL_NAME}) on {run_label}")
    print(f" Structured Output Schema: maxItems=6 strictly enforced")
    print(f" Repeat Count: {repeat_count} (with 4s spacing to respect free tier RPM)")
    print(f"=======================================================")

    all_repeat_rows = []
    all_repeat_logs = []

    for rep in range(1, repeat_count + 1):
        rep_label = f"rep_{rep}"
        print(f"\n>>> Cloud Run {rep}/{repeat_count}...")
        model_rows = []
        raw_logs = {}

        for art_path in article_files:
            art_id = os.path.splitext(os.path.basename(art_path))[0]
            with open(art_path, "r", encoding="utf-8") as f:
                art_text = f.read()

            source_info = sources.get(art_id, {})
            title = source_info.get("title", art_id)
            cond_type = source_info.get("condition_type", "unknown")
            art_gt = answer_key.get(art_id, [])

            print(f"  [{run_label}-{rep_label}] {art_id} ({title}) ...", end="", flush=True)

            prompt_content = prompt_template.replace("{article_text}", art_text)

            # Retry loop with backoff for rate limits
            max_retries = 5
            resp = None
            err = None
            wall_time = 0
            prompt_tokens = 0
            completion_tokens = 0
            raw_content = ""

            for attempt in range(max_retries):
                t0 = time.time()
                try:
                    resp = client.chat.completions.create(
                        model=CLOUD_MODEL_NAME,
                        messages=[{"role": "user", "content": prompt_content}],
                        response_format={
                            "type": "json_schema",
                            "json_schema": {
                                "name": "HealthArticleConditions",
                                "strict": True,
                                "schema": schema
                            }
                        },
                        temperature=0
                    )
                    wall_time = time.time() - t0
                    raw_content = resp.choices[0].message.content or ""
                    prompt_tokens = resp.usage.prompt_tokens if resp.usage else 0
                    completion_tokens = resp.usage.completion_tokens if resp.usage else 0
                    err = None
                    break
                except Exception as e:
                    wall_time = time.time() - t0
                    err = str(e)
                    if "429" in err or "quota" in err.lower():
                        wait_sec = 20 * (attempt + 1)
                        print(f" [Rate limit 429, sleeping {wait_sec}s] ", end="", flush=True)
                        time.sleep(wait_sec)
                    else:
                        break

            # Respect free tier rate limits (15 requests/min => ~4.5s delay)
            time.sleep(4.5)

            if err:
                print(f" FAILED: {err}")
                raw_logs[art_id] = {"error": err, "wall_time_s": wall_time}
                continue

            raw_logs[art_id] = {
                "raw_response": raw_content,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "wall_time_s": wall_time
            }

            eval_res = evaluate_prediction(raw_content, art_id, art_gt, cms_table)
            print(f" DONE in {wall_time:.2f}s | JSON: {eval_res['valid_json']} | Codes: {len(eval_res['codes_returned'])} | Exact: {len(eval_res['exact_matches'])} | Cat: {len(eval_res['category_matches'])} | Inv: {len(eval_res['invalid_codes'])}")

            row = {
                "model": CLOUD_MODEL_NAME,
                "repeat_index": rep,
                "article_id": art_id,
                "title": title,
                "condition_type": cond_type,
                "valid_json": eval_res["valid_json"],
                "num_codes_returned": len(eval_res["codes_returned"]),
                "codes_returned": ";".join(eval_res["codes_returned"]),
                "num_invalid_codes": len(eval_res["invalid_codes"]),
                "invalid_codes": ";".join(eval_res["invalid_codes"]),
                "num_exact_matches": len(eval_res["exact_matches"]),
                "exact_matches": ";".join(eval_res["exact_matches"]),
                "num_category_matches": len(eval_res["category_matches"]),
                "category_matches": ";".join(eval_res["category_matches"]),
                "num_chapter_matches": len(eval_res["chapter_matches"]),
                "chapter_matches": ";".join(eval_res["chapter_matches"]),
                "num_tier_matches": len(eval_res["tier_matches"]),
                "tier_matches": ";".join(eval_res["tier_matches"]),
                "time_taken_s": round(wall_time, 2),
                "prompt_eval_count": prompt_tokens,
                "eval_count": completion_tokens,
                "error_notes": eval_res["parse_error"]
            }
            model_rows.append(row)

        expected_total = sum(len(answer_key.get(os.path.splitext(os.path.basename(p))[0], [])) for p in article_files)
        print_model_summary_table(f"{CLOUD_MODEL_NAME} ({rep_label})", model_rows, gt_total_codes=expected_total)
        all_repeat_rows.append(model_rows)
        all_repeat_logs.append(raw_logs)

    return all_repeat_rows, all_repeat_logs

def run_local_repeat(model_name, prompt_file, schema, cms_table, answer_key, sources, article_files, repeat_count=3):
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    print(f"\n=======================================================")
    print(f" Repeating Local Model {model_name} {repeat_count} times at temp=0")
    print(f"=======================================================")

    all_repeat_rows = []
    all_repeat_logs = []

    for rep in range(1, repeat_count + 1):
        rep_label = f"rep_{rep}"
        print(f"\n>>> Local Repeat Run {rep}/{repeat_count}...")
        unload_model(model_name)
        model_rows = []
        raw_logs = {}

        for art_path in article_files:
            art_id = os.path.splitext(os.path.basename(art_path))[0]
            with open(art_path, "r", encoding="utf-8") as f:
                art_text = f.read()

            source_info = sources.get(art_id, {})
            title = source_info.get("title", art_id)
            cond_type = source_info.get("condition_type", "unknown")
            art_gt = answer_key.get(art_id, [])

            print(f"  [Repeat-{rep}] {model_name} on {art_id} ...", end="", flush=True)

            data, wall_time, err = run_article_call(model_name, art_text, schema, prompt_template)
            if err:
                print(f" FAILED ({err})")
                continue

            raw_content = data.get("message", {}).get("content", "")
            raw_logs[art_id] = {
                "raw_response": raw_content,
                "prompt_eval_count": data.get("prompt_eval_count", 0),
                "eval_count": data.get("eval_count", 0),
                "wall_time_s": wall_time
            }

            eval_res = evaluate_prediction(raw_content, art_id, art_gt, cms_table)
            print(f" DONE in {wall_time:.2f}s | Codes: {len(eval_res['codes_returned'])} | Exact: {len(eval_res['exact_matches'])}")

            row = {
                "model": model_name,
                "repeat_index": rep,
                "article_id": art_id,
                "title": title,
                "condition_type": cond_type,
                "valid_json": eval_res["valid_json"],
                "num_codes_returned": len(eval_res["codes_returned"]),
                "codes_returned": ";".join(eval_res["codes_returned"]),
                "num_invalid_codes": len(eval_res["invalid_codes"]),
                "invalid_codes": ";".join(eval_res["invalid_codes"]),
                "num_exact_matches": len(eval_res["exact_matches"]),
                "exact_matches": ";".join(eval_res["exact_matches"]),
                "time_taken_s": round(wall_time, 2)
            }
            model_rows.append(row)

        unload_model(model_name)
        all_repeat_rows.append(model_rows)
        all_repeat_logs.append(raw_logs)

    return all_repeat_rows, all_repeat_logs

def analyze_repeat_variance(model_name, repeat_logs, out_md_path):
    n_reps = len(repeat_logs)
    articles = sorted(repeat_logs[0].keys())
    identical_count = 0
    diff_details = []

    for art_id in articles:
        resp_1 = repeat_logs[0][art_id]["raw_response"]
        all_same = True
        for rep in range(1, n_reps):
            resp_k = repeat_logs[rep][art_id]["raw_response"]
            if resp_k != resp_1:
                all_same = False
                break
        if all_same:
            identical_count += 1
        else:
            diff_details.append(art_id)

    with open(out_md_path, "w", encoding="utf-8") as f:
        f.write(f"# Repeat Run Variance Analysis at Temperature 0\n\n")
        f.write(f"**Model:** `{model_name}`  \n")
        f.write(f"**Repeats:** {n_reps} runs per article  \n")
        f.write(f"**Total Articles:** {len(articles)}  \n")
        f.write(f"**Identical Outputs Across All {n_reps} Runs:** {identical_count}/{len(articles)} ({identical_count/len(articles)*100:.1f}%)\n\n")
        if diff_details:
            f.write("## Articles with Differences Across Runs:\n")
            for art in diff_details:
                f.write(f"- `{art}`: Raw JSON outputs differed between runs\n")
        else:
            f.write("All outputs across all runs were 100% bit-for-bit identical.\n")
    print(f"Wrote variance analysis to {out_md_path}")
    return identical_count, len(articles), diff_details

def build_v1_v2_comparison_table():
    v1_csv = os.path.join(RESULTS_DIR, "eval_results_v1.csv")
    v2_csv = os.path.join(RESULTS_DIR, "eval_results_v2.csv")

    with open(v1_csv, "r", encoding="utf-8") as f:
        rows_v1 = list(csv.DictReader(f))
    with open(v2_csv, "r", encoding="utf-8") as f:
        rows_v2 = list(csv.DictReader(f))

    gt_count = 36 # will be updated if key changes

    def compute_stats(rows):
        by_model = {}
        for r in rows:
            m = r["model"]
            if m not in by_model:
                by_model[m] = {"ret": 0, "inv": 0, "exact": 0, "cat": 0, "time": 0.0, "n": 0}
            by_model[m]["ret"] += int(r["num_codes_returned"])
            by_model[m]["inv"] += int(r["num_invalid_codes"])
            by_model[m]["exact"] += int(r["num_exact_matches"])
            by_model[m]["cat"] += int(r["num_category_matches"])
            by_model[m]["time"] += float(r["time_taken_s"])
            by_model[m]["n"] += 1
        return by_model

    s1 = compute_stats(rows_v1)
    s2 = compute_stats(rows_v2)

    out_md = os.path.join(RESULTS_DIR, "prompt_v1_vs_v2_comparison.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("# Prompt v1 vs Prompt v2 Benchmark Comparison (Restored Text)\n\n")
        f.write("Shows how much the answer hints in prompt v1 (`I10, E11.9, J45.909, G30.9, N18.9`) were worth compared to out-of-key neutral examples in prompt v2 (`M54.50, K21.9, R51.9, L20.9, H10.9`).\n\n")
        f.write("| Model | Prompt | Codes Returned | Invalid Codes | Exact Matches | Exact Precision | Exact Recall | F1 Score | Cat Matches | Mean Latency |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|\n")
        for m in DEFAULT_MODELS:
            v1_data = s1.get(m, {})
            v2_data = s2.get(m, {})
            p1 = (v1_data["exact"] / v1_data["ret"] * 100) if v1_data.get("ret") else 0
            r1 = (v1_data["exact"] / gt_count * 100)
            f1_1 = (2 * p1 * r1 / (p1 + r1)) if (p1 + r1) else 0
            t1 = (v1_data["time"] / v1_data["n"]) if v1_data.get("n") else 0

            p2 = (v2_data["exact"] / v2_data["ret"] * 100) if v2_data.get("ret") else 0
            r2 = (v2_data["exact"] / gt_count * 100)
            f1_2 = (2 * p2 * r2 / (p2 + r2)) if (p2 + r2) else 0
            t2 = (v2_data["time"] / v2_data["n"]) if v2_data.get("n") else 0

            f.write(f"| {m} | v1 (hints) | {v1_data.get('ret', 0)} | {v1_data.get('inv', 0)} ({v1_data.get('inv', 0)/(v1_data.get('ret', 1) or 1)*100:.1f}%) | {v1_data.get('exact', 0)} | {p1:.1f}% | {r1:.1f}% | {f1_1:.1f}% | {v1_data.get('cat', 0)} | {t1:.2f} s |\n")
            f.write(f"| {m} | v2 (neutral) | {v2_data.get('ret', 0)} | {v2_data.get('inv', 0)} ({v2_data.get('inv', 0)/(v2_data.get('ret', 1) or 1)*100:.1f}%) | {v2_data.get('exact', 0)} | {p2:.1f}% | {r2:.1f}% | {f1_2:.1f}% | {v2_data.get('cat', 0)} | {t2:.2f} s |\n")

    print(f"Wrote v1 vs v2 comparison to {out_md}")

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema = json.load(f)

    cms_table = load_cms_code_table()
    answer_key = load_answer_key()
    sources = load_sources()
    article_files = sorted(glob.glob(os.path.join(ARTICLES_DIR, "art_*.txt")))

    # 1. Run Cloud Model on Prompt v2 with Structured Output (Schema + maxItems: 6) 3 times
    cloud_rows, cloud_raw = run_cloud_evaluation_safe(
        PROMPT_V2_FILE, "Prompt_v2_Structured", schema, cms_table, answer_key, sources, article_files, repeat_count=3
    )
    save_csv(cloud_rows[0], os.path.join(RESULTS_DIR, "gemini_results_structured_v2.csv"))
    with open(os.path.join(RESULTS_DIR, "gemini_raw_responses_v2.json"), "w", encoding="utf-8") as f:
        json.dump(cloud_raw[0], f, indent=2)

    # 2. Run Local Repeat: 3 runs of qwen2.5:1.5b at temp=0
    repeat_model = "qwen2.5:1.5b"
    loc_rep_rows, loc_rep_logs = run_local_repeat(
        repeat_model, PROMPT_V2_FILE, schema, cms_table, answer_key, sources, article_files, repeat_count=3
    )
    save_csv(loc_rep_rows[0], os.path.join(RESULTS_DIR, "local_1.5b_repeat_results.csv"))

    # 3. Variance analysis
    var_loc = analyze_repeat_variance(
        repeat_model, loc_rep_logs, os.path.join(RESULTS_DIR, "repeat_variance_local_1.5b.md")
    )
    var_cloud = analyze_repeat_variance(
        CLOUD_MODEL_NAME, cloud_raw, os.path.join(RESULTS_DIR, "repeat_variance_cloud_gemini.md")
    )

    # 4. Prompt v1 vs v2 comparison
    build_v1_v2_comparison_table()

    print("\nALL CLOUD AND REPEAT BENCHMARKS COMPLETED.")

if __name__ == "__main__":
    main()
