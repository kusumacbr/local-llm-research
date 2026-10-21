import os
import re
import csv
import subprocess
import requests
import trafilatura
from bs4 import BeautifulSoup

DATA_DIR = "data"
ARTICLES_DIR = os.path.join(DATA_DIR, "articles")
REWRITTEN_DIR = os.path.join(DATA_DIR, "articles_curated_rewritten")
SOURCES_FILE = os.path.join(DATA_DIR, "sources.csv")

DAY3_COMMIT = "9388ee2f47269a167b8f79e3ae4cd5f7c9308712"

def get_day3_text(art_id):
    cmd = ["git", "show", f"{DAY3_COMMIT}:data/articles/{art_id}.txt"]
    return subprocess.check_output(cmd, text=True, encoding="utf-8")

def clean_text(text):
    if not text:
        return ""
    # Normalize line endings
    text = re.sub(r'\r\n|\r', '\n', text)
    # Remove link URLs (e.g. https://... or http://...)
    text = re.sub(r'https?://\S+', '', text)
    # Remove any stray link markdown brackets [text]()
    text = re.sub(r'\[([^\]]+)\]\(\s*\)', r'\1', text)
    # Fix broken line breaks: preserve double newline for paragraphs, single space for broken lines
    lines = [l.strip() for l in text.split('\n')]
    # Reassemble paragraphs
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

def fetch_and_extract(source):
    url = source["url"]
    art_id = source["article_id"]
    title = source["title"]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    resp = requests.get(url, headers=headers, timeout=25)
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Decompose noisy script/style/nav/header/footer tags
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "button"]):
        tag.decompose()
        
    if "medlineplus.gov" in url:
        ts = soup.find("div", id="topic-summary")
        if not ts:
            ts = soup.find("main") or soup.find("article")
        # Remove share buttons/widgets
        for btn in ts.find_all(class_=re.compile(r'share|button|related')):
            btn.decompose()
        wrapped = f"<!DOCTYPE html><html><head><title>{title}</title></head><body><h1>{title}</h1><main>{str(ts)}</main></body></html>"
        extracted = trafilatura.extract(wrapped, include_links=False, include_images=False, output_format="txt")
        
    elif "niddk.nih.gov" in url:
        # NIDDK main content
        main_el = soup.find("main") or soup.find("article")
        # Remove breadcrumbs
        for b in main_el.find_all(class_=re.compile(r'breadcrumb|share|sidebar')):
            b.decompose()
        wrapped = f"<!DOCTYPE html><html><head><title>{title}</title></head><body><h1>{title}</h1><main>{str(main_el)}</main></body></html>"
        extracted = trafilatura.extract(wrapped, include_links=False, include_images=False, output_format="txt")
        
    elif "cdc.gov" in url:
        main_el = soup.find("main") or soup.find("div", class_=re.compile(r'cdc-main|content')) or soup.find("article")
        wrapped = f"<!DOCTYPE html><html><head><title>{title}</title></head><body><h1>{title}</h1><main>{str(main_el)}</main></body></html>"
        extracted = trafilatura.extract(wrapped, include_links=False, include_images=False, output_format="txt")
        
    elif "nhlbi.nih.gov" in url:
        # Decompose modals
        for m in soup.find_all(class_="usa-modal"):
            m.decompose()
        for span in soup.find_all(class_="entity-embed-glossary_term"):
            span.unwrap()
        for a in soup.find_all("a"):
            a.unwrap()
        main_el = soup.find("div", class_="field--name-field-component-section-content") or soup.find("div", class_="node__content") or soup.find("main")
        wrapped = f"<!DOCTYPE html><html><head><title>{title}</title></head><body><h1>{title}</h1><main>{str(main_el)}</main></body></html>"
        extracted = trafilatura.extract(wrapped, include_links=False, include_images=False, output_format="txt")
        
    else:
        wrapped = f"<!DOCTYPE html><html><head><title>{title}</title></head><body><h1>{title}</h1><main>{str(soup.find('body'))}</main></body></html>"
        extracted = trafilatura.extract(wrapped, include_links=False, include_images=False, output_format="txt")

    if not extracted:
        extracted = trafilatura.extract(resp.text, include_links=False, include_images=False, output_format="txt")

    # Mechanical cleaning
    final_text = f"# {title}\n\n" + clean_text(extracted)
    return final_text

def main():
    os.makedirs(ARTICLES_DIR, exist_ok=True)
    os.makedirs(REWRITTEN_DIR, exist_ok=True)
    
    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        sources = list(csv.DictReader(f))
        
    results_table = []
    
    print("=" * 80)
    print("Restoring real text from source pages via trafilatura + mechanical cleaning")
    print("=" * 80)
    
    for s in sources:
        art_id = s["article_id"]
        title = s["title"]
        print(f"Processing {art_id}: {title}...")
        
        restored_text = fetch_and_extract(s)
        
        # Save to data/articles/
        out_path = os.path.join(ARTICLES_DIR, f"{art_id}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(restored_text)
            
        # Day 3 text
        day3_text = get_day3_text(art_id)
        
        # Rewritten text (from backup)
        rewritten_path = os.path.join(REWRITTEN_DIR, f"{art_id}.txt")
        if os.path.exists(rewritten_path):
            with open(rewritten_path, "r", encoding="utf-8") as f:
                rewritten_text = f.read()
        else:
            rewritten_text = ""
            
        # Word counts and vocabulary matching
        d3_words = re.findall(r'\b\w+\b', day3_text.lower())
        restored_words = re.findall(r'\b\w+\b', restored_text.lower())
        rewritten_words = re.findall(r'\b\w+\b', rewritten_text.lower())
        
        # Set overlap with Day 3
        d3_vocab = set(d3_words)
        restored_vocab = set(restored_words)
        vocab_overlap = len(d3_vocab.intersection(restored_vocab))
        vocab_match_pct = (vocab_overlap / len(d3_vocab) * 100) if d3_vocab else 0.0
        
        # New words in rewritten vs Day 3
        rewritten_vocab = set(rewritten_words)
        new_in_rewritten = len(rewritten_vocab - d3_vocab)
        pct_new_rewritten = (new_in_rewritten / len(rewritten_vocab) * 100) if rewritten_vocab else 0.0

        results_table.append({
            "art_id": art_id,
            "title": title,
            "d3_words": len(d3_words),
            "restored_words": len(restored_words),
            "rewritten_words": len(rewritten_words),
            "vocab_match_pct": vocab_match_pct,
            "pct_new_rewritten": pct_new_rewritten
        })
        print(f"  -> Restored words: {len(restored_words)} | Day 3 words: {len(d3_words)} | Vocab match: {vocab_match_pct:.1f}%")

    print("\n" + "=" * 80)
    print("Article Text Comparison Table (Day 3 vs Rewritten vs Restored)")
    print("=" * 80)
    print("| Article | Title | Day 3 Words | Restored Words | Day 3 Match (%) | Rewritten Words | New Words in Rewritten (%) |")
    print("|---|---|---|---|---|---|---|")
    for r in results_table:
        print(f"| {r['art_id']} | {r['title']} | {r['d3_words']} | {r['restored_words']} | {r['vocab_match_pct']:.1f}% | {r['rewritten_words']} | {r['pct_new_rewritten']:.1f}% |")

if __name__ == "__main__":
    main()
