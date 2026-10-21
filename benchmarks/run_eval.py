import os
import sys
import json
import time
import glob
import csv
import argparse
import subprocess
import requests

DATA_DIR = "data"
ARTICLES_DIR = os.path.join(DATA_DIR, "articles")
CMS_ORDER_FILE = os.path.join(DATA_DIR, "icd10cm", "icd10cm_order_2026.txt")
ANSWER_KEY_FILE = os.path.join(DATA_DIR, "answer_key.csv")
SOURCES_FILE = os.path.join(DATA_DIR, "sources.csv")
SCHEMA_FILE = os.path.join("schema", "icd10_schema.json")
PROMPT_FILE = os.path.join("prompts", "extraction_prompt_v2.txt")
RESULTS_DIR = "results"
OLLAMA_API_URL = "http://localhost:11434/api/chat"

DEFAULT_MODELS = ["qwen2.5:1.5b", "qwen2.5:3b", "llama3.2:3b", "qwen2.5:7b"]

def get_git_commit():
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        return out
    except Exception:
        return "unknown"

def get_ollama_version():
    try:
        out = subprocess.check_output(["ollama", "--version"], text=True).strip()
        return out.replace("ollama version is", "").strip()
    except Exception:
        return "0.40.4"

def is_range_string(code_str):
    if not code_str:
        return False
    return "-" in str(code_str)

def normalize_code(code_str):
    if not code_str:
        return ""
    return str(code_str).replace(".", "").strip().upper()

def get_category(code_str):
    c = normalize_code(code_str)
    if is_range_string(code_str) or len(c) < 3:
        return ""
    return c[:3]

def get_chapter(code_str):
    if is_range_string(code_str):
        return 0
    c = normalize_code(code_str)
    if not c or len(c) < 3:
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
                "category": get_category(row["icd10cm_code"]),
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
        resp = requests.post(OLLAMA_API_URL, json=payload, timeout=180)
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
    raw_conditions = []
    codes_returned = []
    invalid_codes = []
    exact_matches = []
    category_matches = []
    chapter_matches = []
    tier_matches = []
    parse_error = ""

    if model_output:
        try:
            parsed = json.loads(model_output)
            if isinstance(parsed, dict) and "conditions" in parsed and isinstance(parsed["conditions"], list):
                is_valid_json = "yes"
                raw_conditions = parsed["conditions"]
            else:
                parse_error = "JSON root is not {'conditions': [...]}"
        except Exception as e:
            parse_error = f"JSON parse error: {e}"

    # Deduplicate codes per article: evaluate unique codes only
    seen_norm_codes = set()
    unique_items = []
    for item in raw_conditions:
        if not isinstance(item, dict):
            continue
        raw_code = str(item.get("icd10cm_code", "")).strip()
        if not raw_code:
            continue
        norm_code = normalize_code(raw_code)
        if norm_code not in seen_norm_codes:
            seen_norm_codes.add(norm_code)
            unique_items.append(item)

    # Ground truth lookups
    gt_codes_map = {item["normalized_code"]: item for item in answer_key_art}
    gt_categories = {item["category"] for item in answer_key_art if item["category"]}
    gt_chapters = {item["chapter"] for item in answer_key_art if item["chapter"] > 0}

    for item in unique_items:
        raw_code = str(item.get("icd10cm_code", "")).strip()
        norm_code = normalize_code(raw_code)
        tier = str(item.get("tier", "")).strip().lower()
        codes_returned.append(raw_code)

        # Range check: range strings never count as exact, category, or chapter match
        if is_range_string(raw_code):
            invalid_codes.append(raw_code)
            continue

        # 1. Validation in CMS table
        if norm_code not in cms_table:
            invalid_codes.append(raw_code)

        # 2. Exact match
        if norm_code in gt_codes_map:
            exact_matches.append(raw_code)
            # Tier match only assessed on exact match
            gt_item = gt_codes_map[norm_code]
            if tier == gt_item["tier"]:
                tier_matches.append(raw_code)

        # 3. Category match (first 3 chars, e.g. E11 vs E11.9, range strings excluded)
        pred_cat = get_category(raw_code)
        if pred_cat and pred_cat in gt_categories:
            category_matches.append(raw_code)

        # 4. Chapter match per expected condition (range strings excluded)
        pred_chap = get_chapter(raw_code)
        if pred_chap > 0 and pred_chap in gt_chapters:
            chapter_matches.append(raw_code)

    return {
        "valid_json": is_valid_json,
        "parse_error": parse_error,
        "conditions": unique_items,
        "codes_returned": codes_returned,
        "invalid_codes": invalid_codes,
        "exact_matches": exact_matches,
        "category_matches": category_matches,
        "chapter_matches": chapter_matches,
        "tier_matches": tier_matches
    }

def run_evaluation_assert_checks(cms_table):
    print("Running evaluation test assertion checks ...", end=" ")
    test_gt = [
        {
            "condition_name": "Type 2 diabetes mellitus",
            "icd10cm_code": "E11.9",
            "normalized_code": "E119",
            "tier": "primary",
            "category": "E11",
            "chapter": 4
        },
        {
            "condition_name": "Essential hypertension",
            "icd10cm_code": "I10",
            "normalized_code": "I10",
            "tier": "primary",
            "category": "I10",
            "chapter": 9
        }
    ]

    # Test Case 1: Duplicates (I10;I10;I10 counts as 1 unique code and 1 hit)
    dup_json = json.dumps({"conditions": [
        {"name": "Hypertension", "icd10cm_code": "I10", "tier": "primary"},
        {"name": "Hypertension", "icd10cm_code": "I10", "tier": "primary"},
        {"name": "High BP", "icd10cm_code": "I10", "tier": "primary"}
    ]})
    res_dup = evaluate_prediction(dup_json, "test_dup", test_gt, cms_table)
    assert len(res_dup["codes_returned"]) == 1, f"Duplicate check failed: {res_dup['codes_returned']}"
    assert len(res_dup["exact_matches"]) == 1, f"Duplicate exact match failed: {res_dup['exact_matches']}"
    assert len(res_dup["category_matches"]) == 1
    assert len(res_dup["chapter_matches"]) == 1
    assert len(res_dup["tier_matches"]) == 1
    assert len(res_dup["invalid_codes"]) == 0

    # Test Case 2: Range string (range strings never count for exact, category, or chapter)
    range_json = json.dumps({"conditions": [
        {"name": "Hypertensive diseases", "icd10cm_code": "I10-I15", "tier": "primary"}
    ]})
    res_range = evaluate_prediction(range_json, "test_range", test_gt, cms_table)
    assert len(res_range["codes_returned"]) == 1
    assert len(res_range["exact_matches"]) == 0, "Range string must not match exact"
    assert len(res_range["category_matches"]) == 0, "Range string must not match category"
    assert len(res_range["chapter_matches"]) == 0, "Range string must not match chapter"
    assert len(res_range["invalid_codes"]) == 1, "Range string must be counted invalid"

    # Test Case 3: Category-only match (E11.2 predicted, GT has E11.9)
    cat_json = json.dumps({"conditions": [
        {"name": "Diabetic nephropathy", "icd10cm_code": "E11.2", "tier": "primary"}
    ]})
    res_cat = evaluate_prediction(cat_json, "test_cat", test_gt, cms_table)
    assert len(res_cat["codes_returned"]) == 1
    assert len(res_cat["exact_matches"]) == 0, "Category-only must not count as exact match"
    assert len(res_cat["category_matches"]) == 1, "Category-only must match category"
    assert len(res_cat["chapter_matches"]) == 1, "Category-only must match chapter"
    assert len(res_cat["tier_matches"]) == 0, "Tier match must be 0 when exact match is 0"
    assert len(res_cat["invalid_codes"]) == 0, "E11.2 should be recognized in CMS table"

    print("ALL ASSERT CHECKS PASSED.")

def print_model_summary_table(model, model_results, gt_total_codes=36):
    n_articles = len(model_results)
    valid_count = sum(1 for r in model_results if r["valid_json"] == "yes")
    total_returned = sum(r["num_codes_returned"] for r in model_results)
    total_invalid = sum(r["num_invalid_codes"] for r in model_results)
    total_exact = sum(r["num_exact_matches"] for r in model_results)
    total_category = sum(r["num_category_matches"] for r in model_results)
    total_chapter = sum(r["num_chapter_matches"] for r in model_results)
    total_tier = sum(r["num_tier_matches"] for r in model_results)
    avg_time = sum(r["time_taken_s"] for r in model_results) / n_articles if n_articles else 0
    avg_in_tokens = sum(r["prompt_eval_count"] for r in model_results) / n_articles if n_articles else 0
    avg_out_tokens = sum(r["eval_count"] for r in model_results) / n_articles if n_articles else 0
    
    precision = (total_exact / total_returned * 100) if total_returned > 0 else 0.0
    recall = (total_exact / gt_total_codes * 100) if gt_total_codes > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    articles_per_hour = (3600 / avg_time) if avg_time > 0 else 0.0

    print(f"\n=======================================================")
    print(f" Summary Table: {model}")
    print(f"=======================================================")
    print(f"  Articles evaluated        : {n_articles}")
    print(f"  Valid JSON rate           : {valid_count}/{n_articles} ({valid_count/n_articles*100:.1f}%)")
    print(f"  Total unique codes        : {total_returned}")
    print(f"  Invalid / Hallucinated    : {total_invalid} ({total_invalid/total_returned*100:.1f}%)" if total_returned else "  Invalid / Hallucinated    : 0")
    print(f"  Exact matches (GT)        : {total_exact}")
    print(f"  Exact Precision / Recall  : P={precision:.1f}%, R={recall:.1f}%, F1={f1:.1f}%")
    print(f"  Category matches (3-char) : {total_category}")
    print(f"  Chapter matches           : {total_chapter}")
    print(f"  Tier matches              : {total_tier}")
    print(f"  Mean latency per article  : {avg_time:.2f} s ({articles_per_hour:.1f} art/hr)")
    print(f"  Mean input / output tokens: in={avg_in_tokens:.1f}, out={avg_out_tokens:.1f}")
    print(f"=======================================================\n")

def main():
    parser = argparse.ArgumentParser(description="Evaluate Local LLMs on Health Articles ICD-10 Extraction")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS, help="Models to benchmark")
    parser.add_argument("--articles", nargs="+", default=None, help="Specific article ids (e.g. --articles art_01 art_02)")
    parser.add_argument("--article", type=str, default=None, help="Run only on a specific article id (e.g. art_01)")
    parser.add_argument("--prompt-file", type=str, default=PROMPT_FILE, help="Path to prompt file")
    parser.add_argument("--output-csv", type=str, default=None, help="Output CSV path")
    parser.add_argument("--live", action="store_true", help="Print live article extraction details (demo mode)")
    args = parser.parse_args()

    selected_articles = []
    if args.articles:
        selected_articles = args.articles
    elif args.article:
        selected_articles = [args.article]

    if args.output_csv is None:
        if selected_articles:
            args.output_csv = os.path.join(RESULTS_DIR, "demo_live_result.csv")
        else:
            args.output_csv = os.path.join(RESULTS_DIR, "eval_results.csv")

    os.makedirs(RESULTS_DIR, exist_ok=True)

    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema = json.load(f)
    with open(args.prompt_file, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    cms_table = load_cms_code_table()
    answer_key = load_answer_key()
    sources = load_sources()

    # Run assertion checks
    run_evaluation_assert_checks(cms_table)

    article_files = sorted(glob.glob(os.path.join(ARTICLES_DIR, "art_*.txt")))
    if selected_articles:
        article_files = [f for f in article_files if any(os.path.basename(f).startswith(a) for a in selected_articles)]
        if not article_files:
            print(f"Error: None of the articles {selected_articles} found in {ARTICLES_DIR}")
            sys.exit(1)

    print(f"Found {len(article_files)} articles to test on models: {args.models}")
    print(f"Using prompt template from: {args.prompt_file}")

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
                    "num_category_matches": 0,
                    "category_matches": "",
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

            if model not in raw_logs:
                raw_logs[model] = {}
            raw_logs[model][art_id] = {
                "raw_response": raw_content,
                "prompt_eval_count": prompt_eval_count,
                "eval_count": eval_count,
                "wall_time_s": wall_time
            }

            eval_res = evaluate_prediction(raw_content, art_id, art_gt, cms_table)
            print(f" DONE in {wall_time:.2f}s | JSON: {eval_res['valid_json']} | Unique: {len(eval_res['codes_returned'])} | Exact: {len(eval_res['exact_matches'])} | Cat: {len(eval_res['category_matches'])} | Inv: {len(eval_res['invalid_codes'])}")

            if args.live:
                print(f"\n    [LIVE DETAIL] Model Output:\n{raw_content}")
                print(f"    [LIVE DETAIL] Ground Truth codes: {[k['icd10cm_code'] + ' (' + k['tier'] + ')' for k in art_gt]}")
                print(f"    [LIVE DETAIL] Unique Codes Returned: {eval_res['codes_returned']}")
                print(f"    [LIVE DETAIL] Exact Matches: {eval_res['exact_matches']}")
                print(f"    [LIVE DETAIL] Category Matches: {eval_res['category_matches']}")
                print(f"    [LIVE DETAIL] Chapter Matches: {eval_res['chapter_matches']}")
                print(f"    [LIVE DETAIL] Invalid / Hallucinated Codes: {eval_res['invalid_codes']}\n")

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
                "num_category_matches": len(eval_res["category_matches"]),
                "category_matches": ";".join(eval_res["category_matches"]),
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

        expected_total = sum(len(answer_key.get(os.path.splitext(os.path.basename(p))[0], [])) for p in article_files)
        print_model_summary_table(model, model_rows, gt_total_codes=expected_total)
        unload_model(model)

    fieldnames = [
        "model", "article_id", "title", "condition_type", "valid_json",
        "num_codes_returned", "codes_returned",
        "num_invalid_codes", "invalid_codes",
        "num_exact_matches", "exact_matches",
        "num_category_matches", "category_matches",
        "num_chapter_matches", "chapter_matches",
        "num_tier_matches", "tier_matches",
        "time_taken_s", "prompt_eval_count", "eval_count", "error_notes"
    ]

    git_commit = get_git_commit()
    ollama_ver = get_ollama_version()
    run_date = "2026-10-14"

    with open(args.output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"\nWrote evaluation results ({len(all_rows)} rows) to {args.output_csv}")

    # Only update global eval_raw_responses.json if running the full evaluation
    if not selected_articles:
        raw_logs_path = os.path.join(RESULTS_DIR, "eval_raw_responses.json")
        with open(raw_logs_path, "w", encoding="utf-8") as f:
            json.dump(raw_logs, f, indent=2)
        print(f"Saved raw model response logs to {raw_logs_path}")

if __name__ == "__main__":
    main()
