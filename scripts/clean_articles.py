import os
import re
import requests
from bs4 import BeautifulSoup

def clean_html_to_markdown(html_element, title):
    out = []
    out.append(title)
    out.append("=" * len(title))
    out.append("")

    for elem in html_element.find_all(['h2', 'h3', 'p', 'ul', 'ol', 'table']):
        # Ignore elements inside other processed elements
        if elem.parent and elem.parent.name in ['p', 'li', 'ul', 'ol']:
            continue
            
        if elem.name in ['h2', 'h3']:
            text = elem.get_text(" ", strip=True)
            if text:
                out.append("")
                out.append(text)
                out.append("-" * len(text))
                out.append("")
        elif elem.name == 'p':
            text = elem.get_text(" ", strip=True)
            # Fix spacing before commas/periods that might have been in child tags
            text = re.sub(r'\s+([,.:;?!])', r'\1', text)
            if text:
                out.append(text)
                out.append("")
        elif elem.name in ['ul', 'ol']:
            items = []
            for li in elem.find_all('li', recursive=False):
                li_text = li.get_text(" ", strip=True)
                li_text = re.sub(r'\s+([,.:;?!])', r'\1', li_text)
                if li_text:
                    items.append(f"- {li_text}")
            if items:
                out.append("\n".join(items))
                out.append("")
        elif elem.name == 'table':
            rows = []
            for tr in elem.find_all('tr'):
                cells = [c.get_text(" ", strip=True) for c in tr.find_all(['th', 'td'])]
                cells = [re.sub(r'\s+([,.:;?!])', r'\1', c) for c in cells]
                if cells and any(cells):
                    rows.append(" | ".join(cells))
            if rows:
                out.append("\n".join(rows))
                out.append("")

    # Join and clean multiple newlines
    full = "\n".join(out)
    full = re.sub(r'\n{3,}', '\n\n', full)
    # Ensure no # and no *
    full = full.replace('#', '').replace('*', '')
    return full.strip()

if __name__ == "__main__":
    url = "https://medlineplus.gov/asthma.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()
    summary = soup.find("div", id="topic-summary")
    for btn in summary.find_all(class_=re.compile(r'share|button|related')):
        btn.decompose()
    res = clean_html_to_markdown(summary, "Asthma")
    print(res[:1200])
