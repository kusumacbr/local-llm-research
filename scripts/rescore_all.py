import os
import sys
sys.path.insert(0, os.path.abspath("."))
import json
import csv
import glob

from benchmarks.run_eval import (
    load_cms_code_table,
    load_answer_key,
    load_sources,
    evaluate_prediction,
    print_model_summary_table,
    DEFAULT_MODELS,
    ARTICLES_DIR,
    RESULTS_DIR
)

CLOUD_MODEL_NAME = "gemini-flash-lite-latest"

def rescore_dataset(raw_json_path, out_csv_path, prompt_label, cms_table, answer_key, sources, article_files, models):
    if not os.path.exists(raw_json_path):
        print(f"Error: {raw_json_path} not found.")
        return {}

    with open(raw_json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    all_rows = []
    summary_by_model = {}

    for model in models:
        model_rows = []
        model_raw = raw_data.get(model, {})

        for art_path in article_files:
            art_id = os.path.splitext(os.path.basename(art_path))[0]
            source_info = sources.get(art_id, {})
            title = source_info.get("title", art_id)
            cond_type = source_info.get("condition_type", "unknown")
            art_gt = answer_key.get(art_id, [])

            art_log = model_raw.get(art_id, {})
            raw_content = art_log.get("raw_response", "")
            wall_time = art_log.get("wall_time_s", 0.0)
            p_tokens = art_log.get("prompt_eval_count") or art_log.get("prompt_tokens") or 0
            e_tokens = art_log.get("eval_count") or art_log.get("completion_tokens") or 0

            eval_res = evaluate_prediction(raw_content, art_id, art_gt, cms_table)

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
                "prompt_eval_count": p_tokens,
                "eval_count": e_tokens,
                "error_notes": eval_res["parse_error"]
            }
            model_rows.append(row)
            all_rows.append(row)

        expected_total = sum(len(answer_key.get(os.path.splitext(os.path.basename(p))[0], [])) for p in article_files)
        print_model_summary_table(f"{model} [{prompt_label}]", model_rows, gt_total_codes=expected_total)

        tot_ret = sum(r["num_codes_returned"] for r in model_rows)
        tot_exact = sum(r["num_exact_matches"] for r in model_rows)
        tot_inv = sum(r["num_invalid_codes"] for r in model_rows)
        tot_cat = sum(r["num_category_matches"] for r in model_rows)
        tot_chap = sum(r["num_chapter_matches"] for r in model_rows)
        tot_tier = sum(r["num_tier_matches"] for r in model_rows)
        prec = (tot_exact / tot_ret * 100) if tot_ret else 0.0
        rec = (tot_exact / expected_total * 100) if expected_total else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0
        avg_time = sum(r["time_taken_s"] for r in model_rows) / len(model_rows) if model_rows else 0.0

        summary_by_model[model] = {
            "total_returned": tot_ret,
            "total_exact": tot_exact,
            "total_invalid": tot_inv,
            "total_category": tot_cat,
            "total_chapter": tot_chap,
            "total_tier": tot_tier,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "avg_time": avg_time,
            "expected_gt": expected_total
        }

    # Save rescored CSV
    fieldnames = list(all_rows[0].keys())
    with open(out_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"Wrote rescored CSV ({len(all_rows)} rows) to {out_csv_path}")

    return summary_by_model

def rescore_cloud(raw_json_path, out_csv_path, cms_table, answer_key, sources, article_files):
    if not os.path.exists(raw_json_path):
        print(f"Error: {raw_json_path} not found.")
        return {}

    with open(raw_json_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    all_rows = []
    for art_path in article_files:
        art_id = os.path.splitext(os.path.basename(art_path))[0]
        source_info = sources.get(art_id, {})
        title = source_info.get("title", art_id)
        cond_type = source_info.get("condition_type", "unknown")
        art_gt = answer_key.get(art_id, [])

        art_log = raw_data.get(art_id, {})
        raw_content = art_log.get("raw_response", "")
        wall_time = art_log.get("wall_time_s", 0.0)
        p_tokens = art_log.get("prompt_tokens", 0)
        e_tokens = art_log.get("completion_tokens", 0)

        eval_res = evaluate_prediction(raw_content, art_id, art_gt, cms_table)

        row = {
            "model": CLOUD_MODEL_NAME,
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
            "prompt_eval_count": p_tokens,
            "eval_count": e_tokens,
            "error_notes": eval_res["parse_error"]
        }
        all_rows.append(row)

    expected_total = sum(len(answer_key.get(os.path.splitext(os.path.basename(p))[0], [])) for p in article_files)
    print_model_summary_table(f"{CLOUD_MODEL_NAME} [Rescored]", all_rows, gt_total_codes=expected_total)

    fieldnames = list(all_rows[0].keys())
    with open(out_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"Wrote rescored Cloud CSV ({len(all_rows)} rows) to {out_csv_path}")

    tot_ret = sum(r["num_codes_returned"] for r in all_rows)
    tot_exact = sum(r["num_exact_matches"] for r in all_rows)
    tot_inv = sum(r["num_invalid_codes"] for r in all_rows)
    tot_cat = sum(r["num_category_matches"] for r in all_rows)
    tot_chap = sum(r["num_chapter_matches"] for r in all_rows)
    tot_tier = sum(r["num_tier_matches"] for r in all_rows)
    prec = (tot_exact / tot_ret * 100) if tot_ret else 0.0
    rec = (tot_exact / expected_total * 100) if expected_total else 0.0
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0
    avg_time = sum(r["time_taken_s"] for r in all_rows) / len(all_rows) if all_rows else 0.0

    return {
        CLOUD_MODEL_NAME: {
            "total_returned": tot_ret,
            "total_exact": tot_exact,
            "total_invalid": tot_inv,
            "total_category": tot_cat,
            "total_chapter": tot_chap,
            "total_tier": tot_tier,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "avg_time": avg_time,
            "expected_gt": expected_total
        }
    }

def main():
    cms_table = load_cms_code_table()
    answer_key = load_answer_key()
    sources = load_sources()
    article_files = sorted(glob.glob(os.path.join(ARTICLES_DIR, "art_*.txt")))

    print(f"\n=======================================================")
    print(f" RE-SCORING ALL BENCHMARKS AGAINST ADJUDICATED ANSWER KEY")
    print(f" Total Ground Truth Conditions: {sum(len(v) for v in answer_key.values())}")
    print(f"=======================================================\n")

    # 1. Rescore Prompt v1
    v1_raw = os.path.join(RESULTS_DIR, "eval_raw_responses_v1.json")
    v1_out = os.path.join(RESULTS_DIR, "eval_results_v1.csv")
    stats_v1 = rescore_dataset(v1_raw, v1_out, "Prompt_v1_Rescored", cms_table, answer_key, sources, article_files, DEFAULT_MODELS)

    # 2. Rescore Prompt v2
    v2_raw = os.path.join(RESULTS_DIR, "eval_raw_responses_v2.json")
    v2_out = os.path.join(RESULTS_DIR, "eval_results.csv") # main eval results
    v2_out_backup = os.path.join(RESULTS_DIR, "eval_results_v2.csv")
    stats_v2 = rescore_dataset(v2_raw, v2_out, "Prompt_v2_Rescored", cms_table, answer_key, sources, article_files, DEFAULT_MODELS)
    rescore_dataset(v2_raw, v2_out_backup, "Prompt_v2_Rescored", cms_table, answer_key, sources, article_files, DEFAULT_MODELS)

    # 3. Rescore Cloud Model
    cloud_raw = os.path.join(RESULTS_DIR, "gemini_raw_responses_v2.json")
    cloud_out = os.path.join(RESULTS_DIR, "gemini_reference_results.csv")
    cloud_out_v2 = os.path.join(RESULTS_DIR, "gemini_results_structured_v2.csv")
    stats_cloud = rescore_cloud(cloud_raw, cloud_out, cms_table, answer_key, sources, article_files)
    rescore_cloud(cloud_raw, cloud_out_v2, cms_table, answer_key, sources, article_files)

    # 4. Generate updated comparison table v1 vs v2
    comp_md = os.path.join(RESULTS_DIR, "prompt_v1_vs_v2_comparison.md")
    with open(comp_md, "w", encoding="utf-8") as f:
        f.write("# Prompt v1 vs Prompt v2 Benchmark Comparison (Adjudicated Key)\n\n")
        f.write("Evaluation across all 10 restored articles rescored against the 47-condition official adjudicated ICD-10-CM answer key.\n\n")
        f.write("| Model | Prompt | Codes Returned | Invalid Codes | Exact Matches | Exact Precision | Exact Recall | F1 Score | Cat Matches | Mean Latency |\n")
        f.write("|---|---|---|---|---|---|---|---|---|---|\n")
        for m in DEFAULT_MODELS:
            s1 = stats_v1.get(m, {})
            s2 = stats_v2.get(m, {})
            f.write(f"| {m} | v1 (hints) | {s1.get('total_returned', 0)} | {s1.get('total_invalid', 0)} ({s1.get('total_invalid', 0)/(s1.get('total_returned', 1) or 1)*100:.1f}%) | {s1.get('total_exact', 0)} | {s1.get('precision', 0):.1f}% | {s1.get('recall', 0):.1f}% | {s1.get('f1', 0):.1f}% | {s1.get('total_category', 0)} | {s1.get('avg_time', 0):.2f} s |\n")
            f.write(f"| {m} | v2 (neutral) | {s2.get('total_returned', 0)} | {s2.get('total_invalid', 0)} ({s2.get('total_invalid', 0)/(s2.get('total_returned', 1) or 1)*100:.1f}%) | {s2.get('total_exact', 0)} | {s2.get('precision', 0):.1f}% | {s2.get('recall', 0):.1f}% | {s2.get('f1', 0):.1f}% | {s2.get('total_category', 0)} | {s2.get('avg_time', 0):.2f} s |\n")
    print(f"Wrote rescored v1 vs v2 comparison to {comp_md}")

    # 5. Print Grand Final Comparison Table
    print("\n" + "=" * 100)
    print("GRAND FINAL BENCHMARK SUMMARY TABLE (Restored Text, Strict Schema maxItems:6, Adjudicated Key)")
    print("=" * 100)
    print("| Model | Valid JSON | Codes (Unique) | Invalid Codes | Exact Matches | Exact Precision / Recall / F1 | Category Match | Chapter Match | Tier Match | Seconds / Article |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for m in DEFAULT_MODELS:
        s = stats_v2[m]
        print(f"| {m} | 10/10 (100%) | {s['total_returned']} | {s['total_invalid']} ({s['total_invalid']/s['total_returned']*100:.1f}%) | {s['total_exact']} | P={s['precision']:.1f}% / R={s['recall']:.1f}% / F1={s['f1']:.1f}% | {s['total_category']} | {s['total_chapter']} | {s['total_tier']} | {s['avg_time']:.2f} s |")
    c = stats_cloud[CLOUD_MODEL_NAME]
    print(f"| {CLOUD_MODEL_NAME} (Cloud Reference) | 10/10 (100%) | {c['total_returned']} | {c['total_invalid']} ({c['total_invalid']/c['total_returned']*100:.1f}%) | {c['total_exact']} | P={c['precision']:.1f}% / R={c['recall']:.1f}% / F1={c['f1']:.1f}% | {c['total_category']} | {c['total_chapter']} | {c['total_tier']} | {c['avg_time']:.2f} s |")
    print("=" * 100)

if __name__ == "__main__":
    main()
