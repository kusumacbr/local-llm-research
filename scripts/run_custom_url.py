import os
import sys
import re
import json
import argparse
import requests
import trafilatura
from bs4 import BeautifulSoup

SCHEMA_FILE = os.path.join("schema", "icd10_schema.json")
PROMPT_FILE = os.path.join("prompts", "extraction_prompt_v3.txt")
CMS_ORDER_FILE = os.path.join("data", "icd10cm", "icd10cm_order_2026.txt")
OLLAMA_API_URL = "http://localhost:11434/api/chat"

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\r\n|\r', '\n', text)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'\[([^\]]+)\]\(\s*\)', r'\1', text)
    lines = [l.strip() for l in text.split('\n')]
    cleaned_lines = []
    for l in lines:
        if not l:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
        else:
            cleaned_lines.append(l)
    text = "\n".join(cleaned_lines)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_article_from_url(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    print(f"1. Fetching web page: {url}...")
    resp = requests.get(url, headers=headers, timeout=25)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, "html.parser")
    page_title = soup.title.string.strip() if soup.title and soup.title.string else "Custom Article"
    
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "button"]):
        tag.decompose()
        
    for span in soup.find_all(class_=re.compile(r'glossary|popover|tooltip')):
        span.unwrap()
        
    extracted = trafilatura.extract(str(soup), include_links=False, include_images=False, output_format="txt")
    if not extracted:
        extracted = trafilatura.extract(resp.text, include_links=False, include_images=False, output_format="txt")
        
    cleaned = clean_text(extracted)
    final_text = f"# {page_title}\n\n{cleaned}"
    return page_title, final_text

def load_valid_cms_codes():
    valid_codes = set()
    if os.path.exists(CMS_ORDER_FILE):
        with open(CMS_ORDER_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if len(line) >= 14:
                    code = line[6:14].strip()
                    if code:
                        valid_codes.add(code.upper())
    return valid_codes

def query_local_ollama(model_name, prompt_text, schema):
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt_text}],
        "stream": False,
        "format": schema,
        "options": {
            "temperature": 0,
            "num_predict": 450
        }
    }
    resp = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["message"]["content"]

def main():
    parser = argparse.ArgumentParser(description="Run ICD-10 extraction workflow on any custom URL")
    parser.add_argument("--url", type=str, default=None, help="The web URL of the health article to process")
    parser.add_argument("--model", type=str, default="qwen2.5:7b", help="Local model name (e.g. qwen2.5:1.5b, qwen2.5:7b)")
    parser.add_argument("--prompt", type=str, default=PROMPT_FILE, help="Prompt template file path")
    parser.add_argument("--output", type=str, default="results/custom_url_result.json", help="Output JSON path")
    args = parser.parse_args()

    url = args.url
    if not url:
        print("--------------------------------------------------------------------------------")
        print("Custom Health Article ICD-10 Extractor")
        print("--------------------------------------------------------------------------------")
        url = input("Enter custom health article URL: ").strip()

    if not url:
        print("Error: No URL provided.")
        sys.exit(1)

    try:
        title, article_text = extract_article_from_url(url)
    except Exception as e:
        print(f"Error fetching URL: {e}")
        sys.exit(1)

    word_count = len(article_text.split())
    print(f"   Article Title : {title}")
    print(f"   Extracted Text: {len(article_text)} characters, {word_count} words")

    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema = json.load(f)

    with open(args.prompt, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    full_prompt = prompt_template.replace("{{article_text}}", article_text).replace("{article_text}", article_text)

    print(f"\n2. Running local LLM inference with model: {args.model} (temperature: 0)...")
    try:
        raw_output = query_local_ollama(args.model, full_prompt, schema)
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        print("Make sure Ollama is running in background (e.g. `ollama serve`).")
        sys.exit(1)

    try:
        parsed_json = json.loads(raw_output)
    except Exception:
        print("Warning: Model output could not be parsed as valid JSON.")
        parsed_json = {"conditions": []}

    print("\n3. Validating extracted codes against official CMS ICD-10-CM dictionary...")
    cms_codes = load_valid_cms_codes()
    conditions = parsed_json.get("conditions", [])

    print("\n================================================================================")
    print("EXTRACTION RESULTS")
    print("================================================================================")
    print(f"Source URL   : {url}")
    print(f"Model Tested : {args.model}")
    print(f"Total Codes  : {len(conditions)}\n")

    if not conditions:
        print("No conditions were extracted by the model.")
    else:
        for idx, cond in enumerate(conditions, 1):
            name = cond.get("name", "Unknown")
            code = str(cond.get("icd10cm_code", "")).strip()
            tier = cond.get("tier", "unknown")
            norm_code = code.replace(".", "").upper()
            is_valid = norm_code in cms_codes
            valid_label = "VALID CMS CODE" if is_valid else "INVALID / HALLUCINATED"

            print(f"[{idx}] {name}")
            print(f"    Code : {code} ({valid_label})")
            print(f"    Tier : {tier}")

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({
            "url": url,
            "title": title,
            "model": args.model,
            "word_count": word_count,
            "extracted_json": parsed_json
        }, f, indent=2)

    print(f"\nResult saved to: {args.output}")
    print("================================================================================")

if __name__ == "__main__":
    main()
