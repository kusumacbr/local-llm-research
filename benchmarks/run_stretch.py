import os
import sys

sys.path.insert(0, os.path.abspath("."))

import json
import time
import subprocess
import requests
import csv

from benchmarks.run_eval import (
    load_cms_code_table,
    load_answer_key,
    load_sources,
    evaluate_prediction,
    SCHEMA_FILE,
    PROMPT_FILE,
    RESULTS_DIR,
    OLLAMA_API_URL
)

STRETCH_MODEL = "qwen2.5:7b"
TEST_ARTICLES = ["art_01", "art_02", "art_05", "art_06", "art_07"]

def get_ollama_processor_split(model_name):
    try:
        proc = subprocess.run(["ollama", "ps"], capture_output=True, text=True, check=True)
        lines = proc.stdout.strip().split("\n")
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 4 and parts[0] == model_name:
                # Find processor column (e.g. "60%/40% CPU/GPU" or "100% GPU")
                for i, p in enumerate(parts):
                    if "GPU" in p or "CPU" in p:
                        if i > 0 and ("%" in parts[i-1] or "CPU" in parts[i-1]):
                            return f"{parts[i-1]} {p}"
                        return p
        return "Not recorded"
    except Exception as e:
        return f"Error: {e}"

def run_stretch():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema = json.load(f)
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    cms_table = load_cms_code_table()
    answer_key = load_answer_key()
    sources = load_sources()

    print(f"\n=======================================================")
    print(f" Stretch Evaluation: {STRETCH_MODEL} with Partial CPU Offload")
    print(f"=======================================================")
    
    # Warm up call to trigger load into memory
    print(f"Warming up / loading {STRETCH_MODEL} ...")
    warm_start = time.time()
    try:
        w_resp = requests.post(OLLAMA_API_URL, json={
            "model": STRETCH_MODEL,
            "messages": [{"role": "user", "content": "ping"}],
            "options": {"temperature": 0, "num_predict": 10}
        }, timeout=120)
        warm_time = time.time() - warm_start
        print(f"Model loaded in {warm_time:.2f} s")
    except Exception as e:
        print(f"Warm up error: {e}")

    proc_split = get_ollama_processor_split(STRETCH_MODEL)
    print(f"Detected Ollama Processor Allocation: {proc_split}")

    results = []
    for art_id in TEST_ARTICLES:
        art_path = os.path.join("data", "articles", f"{art_id}.txt")
        with open(art_path, "r", encoding="utf-8") as f:
            art_text = f.read()

        source_info = sources.get(art_id, {})
        title = source_info.get("title", art_id)
        cond_type = source_info.get("condition_type", "unknown")
        art_gt = answer_key.get(art_id, [])

        print(f"  Evaluating {art_id} ({title}) ...", end="", flush=True)

        prompt_content = prompt_template.replace("{article_text}", art_text)
        payload = {
            "model": STRETCH_MODEL,
            "messages": [{"role": "user", "content": prompt_content}],
            "format": schema,
            "stream": False,
            "options": {"temperature": 0, "num_predict": 450}
        }

        t0 = time.time()
        try:
            r = requests.post(OLLAMA_API_URL, json=payload, timeout=180)
            wall_time = time.time() - t0
            if r.status_code != 200:
                print(f" HTTP Error {r.status_code}")
                continue
            data = r.json()
        except Exception as e:
            print(f" Error: {e}")
            continue

        raw_content = data.get("message", {}).get("content", "")
        prompt_eval_count = data.get("prompt_eval_count", 0)
        eval_count = data.get("eval_count", 0)

        eval_res = evaluate_prediction(raw_content, art_id, art_gt, cms_table)
        print(f" DONE in {wall_time:.2f}s | JSON: {eval_res['valid_json']} | Codes: {len(eval_res['codes_returned'])} | Exact: {len(eval_res['exact_matches'])} | Invalid: {len(eval_res['invalid_codes'])}")

        row = {
            "model": STRETCH_MODEL,
            "processor_split": proc_split,
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
            "num_chapter_matches": len(eval_res["chapter_matches"]),
            "chapter_matches": ";".join(eval_res["chapter_matches"]),
            "num_tier_matches": len(eval_res["tier_matches"]),
            "tier_matches": ";".join(eval_res["tier_matches"]),
            "time_taken_s": round(wall_time, 2),
            "prompt_eval_count": prompt_eval_count,
            "eval_count": eval_count,
            "raw_response": raw_content
        }
        results.append(row)

    out_csv = os.path.join(RESULTS_DIR, "stretch_7b_results.csv")
    fieldnames = [k for k in results[0].keys() if k != "raw_response"]
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            row_copy = {k: v for k, v in r.items() if k != "raw_response"}
            writer.writerow(row_copy)

    print(f"\nSaved stretch results to {out_csv}")

    # Summary table
    n_art = len(results)
    valid_c = sum(1 for r in results if r["valid_json"] == "yes")
    tot_ret = sum(r["num_codes_returned"] for r in results)
    tot_inv = sum(r["num_invalid_codes"] for r in results)
    tot_exact = sum(r["num_exact_matches"] for r in results)
    tot_chap = sum(r["num_chapter_matches"] for r in results)
    tot_tier = sum(r["num_tier_matches"] for r in results)
    avg_t = sum(r["time_taken_s"] for r in results) / n_art if n_art else 0

    print(f"\n=======================================================")
    print(f" Stretch Summary Table: {STRETCH_MODEL} ({proc_split})")
    print(f"=======================================================")
    print(f"  Articles evaluated        : {n_art}")
    print(f"  Processor Allocation      : {proc_split}")
    print(f"  Valid JSON rate           : {valid_c}/{n_art} ({valid_c/n_art*100:.1f}%)")
    print(f"  Total codes returned      : {tot_ret}")
    print(f"  Codes not in CMS table    : {tot_inv} ({tot_inv/tot_ret*100:.1f}% hallucinated)" if tot_ret else "  Codes not in CMS table    : 0")
    print(f"  Exact code matches        : {tot_exact}")
    print(f"  Chapter matches           : {tot_chap}")
    print(f"  Tier matches              : {tot_tier}")
    print(f"  Mean latency per article  : {avg_t:.2f} s")
    print(f"=======================================================\n")

if __name__ == "__main__":
    run_stretch()
