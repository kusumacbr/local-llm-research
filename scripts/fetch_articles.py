import os
import re
import csv
import requests
from bs4 import BeautifulSoup

ARTICLES_DIR = os.path.join("data", "articles")
os.makedirs(ARTICLES_DIR, exist_ok=True)

SOURCES = [
    {
        "id": "art_01",
        "title": "Asthma",
        "org": "US National Library of Medicine (NIH MedlinePlus)",
        "url": "https://medlineplus.gov/asthma.html",
        "condition_type": "single",
        "date_read": "2026-10-13",
        "licence": "Public Domain (MedlinePlus/NLM/NIH): Most information on MedlinePlus is in the public domain and may be reproduced, published, or otherwise used without permission.",
        "extractor": "medlineplus"
    },
    {
        "id": "art_02",
        "title": "High Blood Pressure",
        "org": "US National Library of Medicine (NIH MedlinePlus)",
        "url": "https://medlineplus.gov/highbloodpressure.html",
        "condition_type": "single",
        "date_read": "2026-10-13",
        "licence": "Public Domain (MedlinePlus/NLM/NIH): Most information on MedlinePlus is in the public domain and may be reproduced, published, or otherwise used without permission.",
        "extractor": "medlineplus"
    },
    {
        "id": "art_03",
        "title": "Pneumonia",
        "org": "US National Library of Medicine (NIH MedlinePlus)",
        "url": "https://medlineplus.gov/pneumonia.html",
        "condition_type": "single",
        "date_read": "2026-10-13",
        "licence": "Public Domain (MedlinePlus/NLM/NIH): Most information on MedlinePlus is in the public domain and may be reproduced, published, or otherwise used without permission.",
        "extractor": "medlineplus"
    },
    {
        "id": "art_04",
        "title": "Alzheimer's Disease",
        "org": "US National Library of Medicine (NIH MedlinePlus)",
        "url": "https://medlineplus.gov/alzheimersdisease.html",
        "condition_type": "single",
        "date_read": "2026-10-13",
        "licence": "Public Domain (MedlinePlus/NLM/NIH): Most information on MedlinePlus is in the public domain and may be reproduced, published, or otherwise used without permission.",
        "extractor": "medlineplus"
    },
    {
        "id": "art_05",
        "title": "What is Chronic Kidney Disease?",
        "org": "National Institute of Diabetes and Digestive and Kidney Diseases (NIH NIDDK)",
        "url": "https://www.niddk.nih.gov/health-information/kidney-disease/chronic-kidney-disease-ckd/what-is-chronic-kidney-disease",
        "condition_type": "single",
        "date_read": "2026-10-13",
        "licence": "Public Domain (NIH/NIDDK): Information available on this site is in the public domain, unless otherwise stated. It may be reproduced, published or otherwise used without NIH permission.",
        "extractor": "niddk"
    },
    {
        "id": "art_06",
        "title": "Chronic Kidney Disease and Diabetes",
        "org": "Centers for Disease Control and Prevention (CDC)",
        "url": "https://www.cdc.gov/diabetes/managing/diabetes-kidney-disease.html",
        "condition_type": "several",
        "date_read": "2026-10-13",
        "licence": "Public Domain (CDC): Works created by the CDC/US Government are not subject to copyright in the US (17 U.S.C. 105). Unless otherwise stated, information on CDC.gov is in the public domain.",
        "extractor": "cdc"
    },
    {
        "id": "art_07",
        "title": "Metabolic Syndrome",
        "org": "US National Library of Medicine (NIH MedlinePlus)",
        "url": "https://medlineplus.gov/metabolicsyndrome.html",
        "condition_type": "several",
        "date_read": "2026-10-13",
        "licence": "Public Domain (MedlinePlus/NLM/NIH): Most information on MedlinePlus is in the public domain and may be reproduced, published, or otherwise used without permission.",
        "extractor": "medlineplus"
    },
    {
        "id": "art_08",
        "title": "Stroke",
        "org": "US National Library of Medicine (NIH MedlinePlus)",
        "url": "https://medlineplus.gov/stroke.html",
        "condition_type": "several",
        "date_read": "2026-10-13",
        "licence": "Public Domain (MedlinePlus/NLM/NIH): Most information on MedlinePlus is in the public domain and may be reproduced, published, or otherwise used without permission.",
        "extractor": "medlineplus"
    },
    {
        "id": "art_09",
        "title": "Chronic Obstructive Pulmonary Disease (COPD)",
        "org": "National Heart, Lung, and Blood Institute (NIH NHLBI)",
        "url": "https://www.nhlbi.nih.gov/health/copd",
        "condition_type": "several",
        "date_read": "2026-10-13",
        "licence": "Public Domain (NIH/NHLBI): Works of the United States Government. Information available on this site is in the public domain, unless otherwise stated.",
        "extractor": "nhlbi"
    },
    {
        "id": "art_10",
        "title": "Heart Failure",
        "org": "US National Library of Medicine (NIH MedlinePlus)",
        "url": "https://medlineplus.gov/heartfailure.html",
        "condition_type": "several",
        "date_read": "2026-10-13",
        "licence": "Public Domain (MedlinePlus/NLM/NIH): Most information on MedlinePlus is in the public domain and may be reproduced, published, or otherwise used without permission.",
        "extractor": "medlineplus"
    }
]

def clean_text(text):
    text = re.sub(r'\r\n|\r', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    return text.strip()

def extract_article_text(source):
    url = source["url"]
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    if source["id"] == "art_06":
        # CDC page pre-fetched in brain steps/90/content.md or direct read
        cache_path = r"C:\Users\Victus\.gemini\antigravity-ide\brain\eaf67630-18c6-49bd-9f7f-56eb8cb08c98\.system_generated\steps\90\content.md"
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Find the main text starting at "## What to know"
            idx = content.find("## What to know")
            if idx != -1:
                # trim off trailing footer
                end_idx = content.find("### Related topics", idx)
                if end_idx == -1:
                    end_idx = content.find("Was this page helpful?", idx)
                if end_idx == -1:
                    end_idx = len(content)
                body = content[idx:end_idx]
                return f"# {source['title']}\n\n" + clean_text(body)

    r = requests.get(url, headers=headers, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")
    
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()
        
    if source["extractor"] == "medlineplus":
        # MedlinePlus summary section
        summary = soup.find("div", id="topic-summary") or soup.find("div", class_="main-single") or soup.find("div", id="mplus-content")
        if summary:
            # remove sharing/buttons
            for btn in summary.find_all(class_=re.compile(r'share|button|related')):
                btn.decompose()
            text = summary.get_text(separator="\n", strip=True)
            return f"# {source['title']}\n\n" + clean_text(text)
            
    elif source["extractor"] == "niddk":
        main = soup.find("main") or soup.find("article") or soup.find("div", class_="content")
        if main:
            text = main.get_text(separator="\n", strip=True)
            return f"# {source['title']}\n\n" + clean_text(text)
            
    elif source["extractor"] == "nhlbi":
        main = soup.find("div", class_="node__content") or soup.find("main") or soup.find("article")
        if main:
            text = main.get_text(separator="\n", strip=True)
            return f"# {source['title']}\n\n" + clean_text(text)
            
    # Default fallback
    body = soup.find("body")
    return f"# {source['title']}\n\n" + clean_text(body.get_text(separator="\n", strip=True)[:4000])

def main():
    print("Fetching and saving 10 public-domain articles...")
    for s in SOURCES:
        txt = extract_article_text(s)
        filepath = os.path.join(ARTICLES_DIR, f"{s['id']}.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(txt)
        print(f"Saved {s['id']}: {s['title']} ({len(txt)} chars) to {filepath}")

    # Write sources.csv
    sources_csv = os.path.join("data", "sources.csv")
    with open(sources_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["article_id", "title", "source_organization", "url", "condition_type", "date_read", "licence_statement"])
        for s in SOURCES:
            writer.writerow([s["id"], s["title"], s["org"], s["url"], s["condition_type"], s["date_read"], s["licence"]])
    print(f"\nWrote {sources_csv}")

if __name__ == "__main__":
    main()
