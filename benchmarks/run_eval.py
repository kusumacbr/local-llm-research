import os
import sys
import json
import time
import glob
import csv
import argparse
import requests

DATA_DIR = "data"
ARTICLES_DIR = os.path.join(DATA_DIR, "articles")
CMS_ORDER_FILE = os.path.join(DATA_DIR, "icd10cm", "icd10cm_order_2026.txt")
ANSWER_KEY_FILE = os.path.join(DATA_DIR, "answer_key.csv")
SOURCES_FILE = os.path.join(DATA_DIR, "sources.csv")
SCHEMA_FILE = os.path.join("schema", "icd10_schema.json")
PROMPT_FILE = os.path.join("prompts", "extraction_prompt.txt")
RESULTS_DIR = "results"
OLLAMA_API_URL = "http://localhost:11434/api/chat"

DEFAULT_MODELS = ["qwen2.5:1.5b", "qwen2.5:3b", "llama3.2:3b"]

def normalize_code(code_str):
    if not code_str:
        return ""
    return str(code_str).replace(".", "").strip().upper()

def get_chapter(code_str):
    c = normalize_code(code_str)
    if not c:
        return 0
    letter = c[0]
    num = int(c[1:3]) if len(c) >= 3 and c[1:3].isdigit() else 0
    if letter in ['A', 'B']:
        return 1
    elif letter == 'C' or (letter == 'D' and num <= 49):
        return 2
    elif letter == 'D' and num >= 50:
        return 3
    elif letter == 'E':
        return 4
    elif letter == 'F':
        return 5
    elif letter == 'G':
        return 6
    elif letter == 'H' and num <= 59:
        return 7
    elif letter == 'H' and num >= 60:
        return 8
    elif letter == 'I':
        return 9
    elif letter == 'J':
        return 10
    elif letter == 'K':
        return 11
    elif letter == 'L':
        return 12
    elif letter == 'M':
        return 13
    elif letter == 'N':
        return 14
    elif letter == 'O':
        return 15
    elif letter == 'P':
        return 16
    elif letter == 'Q':
        return 17
    elif letter == 'R':
        return 18
    elif letter in ['S', 'T']:
        return 19
    elif letter in ['V', 'W', 'X', 'Y']:
        return 20
    elif letter == 'Z':
        return 21
    elif letter == 'U':
        return 22
    return 0

def load_cms_code_table():
    if not os.path.exists(CMS_ORDER_FILE):
        raise FileNotFoundError(f"CMS order file not found at {CMS_ORDER_FILE}. Run scripts/fetch_articles.py first.")
    cms_codes = {}
    with open(CMS_ORDER_FILE, "r", encoding="latin1") as f:
        for line in f:
            parts = line.strip().split(maxsplit=3)
            if len(parts) >= 4:
                code_raw = parts[1]
                desc = parts[3]
                cms_codes[code_raw.upper()] = desc
    print(f"Loaded {len(cms_codes)} CMS ICD-10-CM codes from {CMS_ORDER_FILE}")
    return cms_codes

def load_answer_key():
    if not os.path.exists(ANSWER_KEY_FILE):
        raise FileNotFoundError(f"Answer key not found at {ANSWER_KEY_FILE}.")
    answer_key = {}
    with open(ANSWER_KEY_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            art_id = row["article_id"]
            if art_id not in answer_key:
                answer_key[art_id] = []
            answer_key[art_id].append({
                "condition_name": row["condition_name"],
                "icd10cm_code": row["icd10cm_code"],
                "normalized_code": normalize_code(row["icd10cm_code"]),
                "tier": row["tier"].strip().lower(),
                "chapter": get_chapter(row["icd10cm_code"])
            })
    print(f"Loaded answer key for {len(answer_key)} articles from {ANSWER_KEY_FILE}")
    return answer_key

def load_sources():
    sources = {}
    if os.path.exists(SOURCES_FILE):
        with open(SOURCES_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sources[row["article_id"]] = row
    return sources

def unload_model(model_name):
    try:
        requests.post("http://localhost:11434/api/generate", json={"model": model_name, "keep_alive": 0}, timeout=5)
    except Exception:
        pass

def run_article_call(model, article_text, schema, prompt_template):
    prompt_content = prompt_template.replace("{article_text}", article_text)
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt_content}
        ],
        "format": schema,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 450
        }
    }
    
    start_time = time.time()
    try:
        resp = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        wall_time = time.time() - start_time
        if resp.status_code != 200:
            return None, wall_time, f"HTTP Error {resp.status_code}: {resp.text}"
        data = resp.json()
        return data, wall_time, None
    except Exception as e:
        wall_time = time.time() - start_time
        return None, wall_time, str(e)

def evaluate_prediction(model_output, article_id, answer_key_art, cms_table):
    is_valid_json = "no"
    conditions = []
    codes_returned = []
    invalid_codes = []
    exact_matches = []
    chapter_matches = []
    tier_matches = []
    parse_error = ""

    if model_output:
        try:
            parsed = json.loads(model_output)
            if isinstance(parsed, dict) and "conditions" in parsed and isinstance(parsed["conditions"], list):
                is_valid_json = "yes"
                conditions = parsed["conditions"]
            else:
                parse_error = "JSON root is not {'conditions': [...]}"
        except Exception as e:
            parse_error = f"JSON parse error: {e}"
            
    # Key lookups for ground truth
    gt_codes_map = {item["normalized_code"]: item for item in answer_key_art}
    gt_chapters = {item["chapter"] for item in answer_key_art if item["chapter"] > 0}

    for item in conditions:
        if not isinstance(item, dict):
            continue
        raw_code = item.get("icd10cm_code", "").strip()
        norm_code = normalize_code(raw_code)
        tier = str(item.get("tier", "")).strip().lower()
        
        if not raw_code:
            continue
            
        codes_returned.append(raw_code)
        
        # 1. Valid code in CMS table?
        if norm_code not in cms_table:
            invalid_codes.append(raw_code)
            
        # 2. Exact code match with answer key?
        if norm_code in gt_codes_map:
            exact_matches.append(raw_code)
            # 3. Tier match?
            gt_item = gt_codes_map[norm_code]
            if tier == gt_item["tier"]:
                tier_matches.append(raw_code)
                
        # 4. Chapter match?
        pred_chap = get_chapter(raw_code)
        if pred_chap in gt_chapters:
            chapter_matches.append(raw_code)

    return {
        "valid_json": is_valid_json,
        "parse_error": parse_error,
        "conditions": conditions,
        "codes_returned": codes_returned,
        "invalid_codes": invalid_codes,
        "exact_matches": exact_matches,
        "chapter_matches": chapter_matches,
        "tier_matches": tier_matches
    }

def print_model_summary_table(model, model_results, gt_total_codes=36):
    n_articles = len(model_results)
    valid_count = sum(1 for r in model_results if r["valid_json"] == "yes")
    total_returned = sum(r["num_codes_returned"] for r in model_results)
    total_invalid = sum(r["num_invalid_codes"] for r in model_results)
    total_exact = sum(r["num_exact_matches"] for r in model_results)
    total_chapter = sum(r["num_chapter_matches"] for r in model_results)
    total_tier = sum(r["num_tier_matches"] for r in model_results)
    avg_time = sum(r["time_taken_s"] for r in model_results) / n_articles if n_articles else 0
    avg_in_tokens = sum(r["prompt_eval_count"] for r in model_results) / n_articles if n_articles else 0
    avg_out_tokens = sum(r["eval_count"] for r in model_results) / n_articles if n_articles else 0
    
    precision = (total_exact / total_returned * 100) if total_returned > 0 else 0.0
    recall = (total_exact / gt_total_codes * 100) if gt_total_codes > 0 else 0.0

    print(f"\n=======================================================")
    print(f" Summary Table: {model}")
    print(f"=======================================================")
    print(f"  Articles evaluated        : {n_articles}")
    print(f"  Valid JSON rate           : {valid_count}/{n_articles} ({valid_count/n_articles*100:.1f}%)")
    print(f"  Total codes returned      : {total_returned}")
    print(f"  Codes not in CMS table    : {total_invalid} ({total_invalid/total_returned*100:.1f}% hallucinated)" if total_returned else "  Codes not in CMS table    : 0")
    print(f"  Exact code matches (GT)   : {total_exact} (Precision: {precision:.1f}%, Recall: {recall:.1f}%)")
    print(f"  Chapter matches           : {total_chapter}")
    print(f"  Tier matches              : {total_tier}")
    print(f"  Mean latency per article  : {avg_time:.2f} s")
    print(f"  Mean input tokens         : {avg_in_tokens:.1f}")
    print(f"  Mean output tokens        : {avg_out_tokens:.1f}")
    print(f"=======================================================\n")

def main():
    parser = argparse.ArgumentParser(description="Evaluate Local LLMs on Health Articles ICD-10 Extraction")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS, help="Models to benchmark")
    parser.add_argument("--article", type=str, default=None, help="Run only on a specific article id (e.g. art_01)")
    parser.add_argument("--output-csv", type=str, default=None, help="Output CSV path")
    parser.add_argument("--live", action="store_true", help="Print live article extraction details (demo mode)")
    args = parser.parse_args()

    if args.output_csv is None:
        if args.article:
            args.output_csv = os.path.join(RESULTS_DIR, "demo_live_result.csv")
        else:
            args.output_csv = os.path.join(RESULTS_DIR, "eval_results.csv")

    os.makedirs(RESULTS_DIR, exist_ok=True)

    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema = json.load(f)
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    cms_table = load_cms_code_table()
    answer_key = load_answer_key()
    sources = load_sources()

    article_files = sorted(glob.glob(os.path.join(ARTICLES_DIR, "art_*.txt")))
    if args.article:
        article_files = [f for f in article_files if os.path.basename(f).startswith(args.article)]
        if not article_files:
            print(f"Error: article '{args.article}' not found in {ARTICLES_DIR}")
            sys.exit(1)

    print(f"Found {len(article_files)} articles to test on models: {args.models}")

    all_rows = []
    raw_logs = {}

    for model in args.models:
        print(f"\n>>> Running evaluation for model: {model} (one run each)")
        unload_model(model)
        model_rows = []

        for art_path in article_files:
            art_id = os.path.splitext(os.path.basename(art_path))[0]
            with open(art_path, "r", encoding="utf-8") as f:
                art_text = f.read()

            source_info = sources.get(art_id, {})
            title = source_info.get("title", art_id)
            cond_type = source_info.get("condition_type", "unknown")
            art_gt = answer_key.get(art_id, [])

            print(f"  Evaluating {art_id} ({title}) ...", end="", flush=True)

            data, wall_time, err = run_article_call(model, art_text, schema, prompt_template)
            
            if err:
                print(f" FAILED ({err}) in {wall_time:.2f}s")
                row = {
                    "model": model,
                    "article_id": art_id,
                    "title": title,
                    "condition_type": cond_type,
                    "valid_json": "no",
                    "num_codes_returned": 0,
                    "codes_returned": "",
                    "num_invalid_codes": 0,
                    "invalid_codes": "",
                    "num_exact_matches": 0,
                    "exact_matches": "",
                    "num_chapter_matches": 0,
                    "chapter_matches": "",
                    "num_tier_matches": 0,
                    "tier_matches": "",
                    "time_taken_s": round(wall_time, 2),
                    "prompt_eval_count": 0,
                    "eval_count": 0,
                    "error_notes": err
                }
                model_rows.append(row)
                all_rows.append(row)
                continue

            raw_content = data.get("message", {}).get("content", "")
            prompt_eval_count = data.get("prompt_eval_count", 0)
            eval_count = data.get("eval_count", 0)

            # Store in raw logs
            if model not in raw_logs:
                raw_logs[model] = {}
            raw_logs[model][art_id] = {
                "raw_response": raw_content,
                "prompt_eval_count": prompt_eval_count,
                "eval_count": eval_count,
                "wall_time_s": wall_time
            }

            eval_res = evaluate_prediction(raw_content, art_id, art_gt, cms_table)
            print(f" DONE in {wall_time:.2f}s | JSON: {eval_res['valid_json']} | Codes: {len(eval_res['codes_returned'])} | Exact: {len(eval_res['exact_matches'])} | Invalid: {len(eval_res['invalid_codes'])}")

            if args.live:
                print(f"    [LIVE DETAIL] Model output JSON:\n{raw_content}")
                print(f"    [LIVE DETAIL] Answer Key codes: {[k['icd10cm_code'] + ' (' + k['tier'] + ')' for k in art_gt]}")
                print(f"    [LIVE DETAIL] Exact matches: {eval_res['exact_matches']}")
                print(f"    [LIVE DETAIL] Invalid CMS codes: {eval_res['invalid_codes']}")

            row = {
                "model": model,
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
                "error_notes": eval_res["parse_error"]
            }
            model_rows.append(row)
            all_rows.append(row)

        print_model_summary_table(model, model_rows, gt_total_codes=len(answer_key) if args.article else 36)
        unload_model(model)

    # Save CSV
    fieldnames = [
        "model", "article_id", "title", "condition_type", "valid_json",
        "num_codes_returned", "codes_returned",
        "num_invalid_codes", "invalid_codes",
        "num_exact_matches", "exact_matches",
        "num_chapter_matches", "chapter_matches",
        "num_tier_matches", "tier_matches",
        "time_taken_s", "prompt_eval_count", "eval_count", "error_notes"
    ]
    with open(args.output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"\nWrote full evaluation results ({len(all_rows)} rows) to {args.output_csv}")

    # Save raw logs
    raw_logs_path = os.path.join(RESULTS_DIR, "eval_raw_responses.json")
    with open(raw_logs_path, "w", encoding="utf-8") as f:
        json.dump(raw_logs, f, indent=2)
    print(f"Saved raw model response logs to {raw_logs_path}")

if __name__ == "__main__":
    main()
