import os
import sys
sys.path.insert(0, os.path.abspath("."))
import json
import time
import glob
import csv
from dotenv import load_dotenv
from openai import OpenAI

from benchmarks.run_eval import (
    load_cms_code_table,
    load_answer_key,
    load_sources,
    evaluate_prediction,
    run_evaluation_assert_checks,
    print_model_summary_table,
    normalize_code,
    PROMPT_FILE,
    ARTICLES_DIR,
    RESULTS_DIR
)

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
MODEL_NAME = "gemini-flash-lite-latest"

def main():
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY is not set.")
        sys.exit(1)

    client = OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=GEMINI_API_KEY,
        timeout=60.0
    )

    cms_table = load_cms_code_table()
    answer_key = load_answer_key()
    sources = load_sources()

    run_evaluation_assert_checks(cms_table)

    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    article_files = sorted(glob.glob(os.path.join(ARTICLES_DIR, "art_*.txt")))
    print(f"\nRunning Cloud Reference Evaluation with {MODEL_NAME} on {len(article_files)} articles...")

    all_rows = []
    raw_logs = {}
    disagreements = []

    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema = json.load(f)

    for art_path in article_files:
        art_id = os.path.splitext(os.path.basename(art_path))[0]
        with open(art_path, "r", encoding="utf-8") as f:
            art_text = f.read()

        source_info = sources.get(art_id, {})
        title = source_info.get("title", art_id)
        cond_type = source_info.get("condition_type", "unknown")
        art_gt = answer_key.get(art_id, [])

        print(f"  Evaluating {art_id} ({title}) ...", end="", flush=True)

        prompt_content = prompt_template.replace("{article_text}", art_text)

        t0 = time.time()
        try:
            resp = client.chat.completions.create(
                model=MODEL_NAME,
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
        except Exception as e:
            wall_time = time.time() - t0
            raw_content = ""
            prompt_tokens = 0
            completion_tokens = 0
            err = str(e)

        if err:
            print(f" FAILED: {err}")
            continue

        raw_logs[art_id] = {
            "raw_response": raw_content,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "wall_time_s": wall_time
        }

        eval_res = evaluate_prediction(raw_content, art_id, art_gt, cms_table)
        print(f" DONE in {wall_time:.2f}s | Codes: {len(eval_res['codes_returned'])} | Exact: {len(eval_res['exact_matches'])} | Cat: {len(eval_res['category_matches'])} | Inv: {len(eval_res['invalid_codes'])}")

        # Track detailed disagreements with answer key
        gt_norm_map = {item["normalized_code"]: item for item in art_gt}
        pred_norm_map = {}
        for c_item in eval_res["conditions"]:
            code_str = c_item.get("icd10cm_code", "").strip()
            if code_str:
                pred_norm_map[normalize_code(code_str)] = c_item

        gt_norm_set = set(gt_norm_map.keys())
        pred_norm_set = set(pred_norm_map.keys())

        matched_codes = gt_norm_set & pred_norm_set
        missed_by_gemini = gt_norm_set - pred_norm_set
        extra_by_gemini = pred_norm_set - gt_norm_set

        # Tier mismatches among exact matches
        tier_mismatches = []
        for m in matched_codes:
            pred_tier = str(pred_norm_map[m].get("tier", "")).strip().lower()
            gt_tier = gt_norm_map[m]["tier"]
            if pred_tier != gt_tier:
                tier_mismatches.append({
                    "code": gt_norm_map[m]["icd10cm_code"],
                    "condition": gt_norm_map[m]["condition_name"],
                    "expected_tier": gt_tier,
                    "gemini_tier": pred_tier
                })

        disagreements.append({
            "article_id": art_id,
            "title": title,
            "exact_matches": [gt_norm_map[m]["icd10cm_code"] for m in matched_codes],
            "missed_by_gemini": [gt_norm_map[m]["icd10cm_code"] + f" ({gt_norm_map[m]['condition_name']})" for m in missed_by_gemini],
            "extra_predicted_by_gemini": [pred_norm_map[m].get("icd10cm_code", "") + f" ({pred_norm_map[m].get('name', '')})" for m in extra_by_gemini],
            "tier_mismatches": tier_mismatches
        })

        row = {
            "model": MODEL_NAME,
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
        all_rows.append(row)

    expected_total = sum(len(answer_key.get(os.path.splitext(os.path.basename(p))[0], [])) for p in article_files)
    print_model_summary_table(MODEL_NAME, all_rows, gt_total_codes=expected_total)

    # Write reference CSV
    csv_out = os.path.join(RESULTS_DIR, "gemini_reference_results.csv")
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
    with open(csv_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"Wrote reference CSV to {csv_out}")

    # Write raw responses
    raw_out = os.path.join(RESULTS_DIR, "gemini_raw_responses.json")
    with open(raw_out, "w", encoding="utf-8") as f:
        json.dump(raw_logs, f, indent=2)
    print(f"Wrote raw responses to {raw_out}")

    # Write detailed disagreements report
    disagree_out = os.path.join(RESULTS_DIR, "gemini_disagreements.md")
    with open(disagree_out, "w", encoding="utf-8") as f:
        f.write("# Gemini vs Draft Answer Key Disagreement Analysis\n\n")
        f.write(f"**Model:** `{MODEL_NAME}`  \n")
        f.write("**Evaluation Date:** 2026-10-14  \n\n")
        f.write("This document details where `gemini-flash-lite-latest` agreed and disagreed with the 36-condition draft answer key.\n\n")

        for d in disagreements:
            f.write(f"## {d['article_id']}: {d['title']}\n\n")
            f.write(f"- **Exact Matches:** {', '.join(d['exact_matches']) if d['exact_matches'] else 'None'}\n")
            f.write(f"- **Missed by Gemini (in Answer Key, not in Gemini):**\n")
            if d['missed_by_gemini']:
                for m in d['missed_by_gemini']:
                    f.write(f"  - `{m}`\n")
            else:
                f.write("  - None\n")

            f.write(f"- **Extra Conditions Extracted by Gemini (not in Answer Key):**\n")
            if d['extra_predicted_by_gemini']:
                for m in d['extra_predicted_by_gemini']:
                    f.write(f"  - `{m}`\n")
            else:
                f.write("  - None\n")

            if d['tier_mismatches']:
                f.write(f"- **Tier Disagreements:**\n")
                for tm in d['tier_mismatches']:
                    f.write(f"  - `{tm['code']}` ({tm['condition']}): Expected `{tm['expected_tier']}`, Gemini predicted `{tm['gemini_tier']}`\n")
            f.write("\n---\n\n")
    print(f"Wrote disagreement analysis to {disagree_out}")

if __name__ == "__main__":
    main()
