import os
import csv

ANSWER_KEY_DATA = [
    # art_01: Asthma
    {"article_id": "art_01", "condition_name": "Asthma", "icd10cm_code": "J45.909", "tier": "primary", "rationale": "Article is primarily focused on asthma definition, triggers, symptoms and management."},
    {"article_id": "art_01", "condition_name": "Allergic rhinitis", "icd10cm_code": "J30.9", "tier": "secondary", "rationale": "Allergies and allergic triggers are discussed as significant cofactors."},
    
    # art_02: High Blood Pressure
    {"article_id": "art_02", "condition_name": "Essential (primary) hypertension", "icd10cm_code": "I10", "tier": "primary", "rationale": "Article is primarily focused on high blood pressure / hypertension diagnosis and control."},
    {"article_id": "art_02", "condition_name": "Heart disease, unspecified", "icd10cm_code": "I51.9", "tier": "secondary", "rationale": "Heart disease is highlighted as a major risk and complication of uncontrolled blood pressure."},
    {"article_id": "art_02", "condition_name": "Cerebral infarction (Stroke)", "icd10cm_code": "I63.9", "tier": "tertiary", "rationale": "Mentioned as a life-threatening complication of hypertension."},
    
    # art_03: Pneumonia
    {"article_id": "art_03", "condition_name": "Pneumonia, unspecified organism", "icd10cm_code": "J18.9", "tier": "primary", "rationale": "Article is entirely dedicated to pneumonia causes, symptoms, and treatment."},
    {"article_id": "art_03", "condition_name": "Influenza", "icd10cm_code": "J11.1", "tier": "secondary", "rationale": "Flu virus is covered as a prominent cause leading to viral pneumonia."},
    
    # art_04: Alzheimer's Disease
    {"article_id": "art_04", "condition_name": "Alzheimer's disease, unspecified", "icd10cm_code": "G30.9", "tier": "primary", "rationale": "Article is specifically focused on Alzheimer's disease progression and care."},
    {"article_id": "art_04", "condition_name": "Dementia, unspecified", "icd10cm_code": "F03.90", "tier": "secondary", "rationale": "Dementia syndrome and memory loss symptoms are core components of discussion."},
    
    # art_05: What is Chronic Kidney Disease?
    {"article_id": "art_05", "condition_name": "Chronic kidney disease, unspecified", "icd10cm_code": "N18.9", "tier": "primary", "rationale": "Article explains what chronic kidney disease is, its stages, and consequences."},
    {"article_id": "art_05", "condition_name": "Essential (primary) hypertension", "icd10cm_code": "I10", "tier": "secondary", "rationale": "High blood pressure is identified as a primary cause and risk factor for CKD."},
    {"article_id": "art_05", "condition_name": "Type 2 diabetes mellitus", "icd10cm_code": "E11.9", "tier": "secondary", "rationale": "Diabetes is highlighted as the leading cause damaging kidney filters."},
    {"article_id": "art_05", "condition_name": "Heart disease, unspecified", "icd10cm_code": "I51.9", "tier": "tertiary", "rationale": "Heart disease is mentioned as an elevated risk consequence of CKD."},
    
    # art_06: Chronic Kidney Disease and Diabetes
    {"article_id": "art_06", "condition_name": "Type 2 diabetes mellitus with diabetic chronic kidney disease", "icd10cm_code": "E11.22", "tier": "primary", "rationale": "Core focus is the direct intersection of diabetes and diabetic kidney disease."},
    {"article_id": "art_06", "condition_name": "Chronic kidney disease, unspecified", "icd10cm_code": "N18.9", "tier": "primary", "rationale": "Article focuses equally on the development and detection of CKD."},
    {"article_id": "art_06", "condition_name": "Essential (primary) hypertension", "icd10cm_code": "I10", "tier": "secondary", "rationale": "Managing blood pressure is detailed as a vital component to slow CKD progression."},
    {"article_id": "art_06", "condition_name": "Heart disease, unspecified", "icd10cm_code": "I51.9", "tier": "tertiary", "rationale": "Mentioned as an increased risk for people with both diabetes and CKD."},
    
    # art_07: Metabolic Syndrome
    {"article_id": "art_07", "condition_name": "Metabolic syndrome", "icd10cm_code": "E88.81", "tier": "primary", "rationale": "Article defines metabolic syndrome and its criteria."},
    {"article_id": "art_07", "condition_name": "Type 2 diabetes mellitus", "icd10cm_code": "E11.9", "tier": "secondary", "rationale": "High blood glucose and progression to diabetes is one of the key pillars."},
    {"article_id": "art_07", "condition_name": "Essential (primary) hypertension", "icd10cm_code": "I10", "tier": "secondary", "rationale": "High blood pressure is another defining pillar of metabolic syndrome."},
    {"article_id": "art_07", "condition_name": "Obesity, unspecified", "icd10cm_code": "E66.9", "tier": "secondary", "rationale": "Large waistline / abdominal obesity is a core diagnostic criterion."},
    {"article_id": "art_07", "condition_name": "Hyperlipidemia, unspecified", "icd10cm_code": "E78.5", "tier": "secondary", "rationale": "High blood triglycerides and low HDL cholesterol are core criteria."},
    {"article_id": "art_07", "condition_name": "Atherosclerotic heart disease (Coronary artery disease)", "icd10cm_code": "I25.10", "tier": "tertiary", "rationale": "Heart attack and coronary disease mentioned as the major consequence."},
    
    # art_08: Stroke
    {"article_id": "art_08", "condition_name": "Cerebral infarction, unspecified (Stroke)", "icd10cm_code": "I63.9", "tier": "primary", "rationale": "Article is centered around stroke types, symptoms, and emergency care."},
    {"article_id": "art_08", "condition_name": "Transient cerebral ischemic attack (TIA)", "icd10cm_code": "G45.9", "tier": "secondary", "rationale": "Mini-strokes (TIAs) are explained in depth as warning events."},
    {"article_id": "art_08", "condition_name": "Essential (primary) hypertension", "icd10cm_code": "I10", "tier": "secondary", "rationale": "High blood pressure is highlighted as the single biggest treatable risk factor."},
    {"article_id": "art_08", "condition_name": "Unspecified atrial fibrillation", "icd10cm_code": "I48.91", "tier": "tertiary", "rationale": "Atrial fibrillation mentioned as an important cardiac cause of embolic stroke."},
    {"article_id": "art_08", "condition_name": "Type 2 diabetes mellitus", "icd10cm_code": "E11.9", "tier": "tertiary", "rationale": "Diabetes mentioned as a contributing vascular risk factor."},
    
    # art_09: Chronic Obstructive Pulmonary Disease (COPD)
    {"article_id": "art_09", "condition_name": "Chronic obstructive pulmonary disease, unspecified", "icd10cm_code": "J44.9", "tier": "primary", "rationale": "Article is directly focused on COPD definition, mechanism, and treatment."},
    {"article_id": "art_09", "condition_name": "Emphysema, unspecified", "icd10cm_code": "J43.9", "tier": "secondary", "rationale": "Emphysema is explained as one of the two main conditions making up COPD."},
    {"article_id": "art_09", "condition_name": "Unspecified chronic bronchitis", "icd10cm_code": "J42", "tier": "secondary", "rationale": "Chronic bronchitis is explained as the second main condition making up COPD."},
    {"article_id": "art_09", "condition_name": "Unspecified asthma, uncomplicated", "icd10cm_code": "J45.909", "tier": "tertiary", "rationale": "Asthma is discussed in the differential diagnosis and overlap with COPD."},
    
    # art_10: Heart Failure
    {"article_id": "art_10", "condition_name": "Heart failure, unspecified", "icd10cm_code": "I50.9", "tier": "primary", "rationale": "Article is primarily on heart failure etiology, symptoms, and lifestyle changes."},
    {"article_id": "art_10", "condition_name": "Atherosclerotic heart disease (Coronary artery disease)", "icd10cm_code": "I25.10", "tier": "secondary", "rationale": "Coronary artery disease is cited as the most common underlying cause."},
    {"article_id": "art_10", "condition_name": "Essential (primary) hypertension", "icd10cm_code": "I10", "tier": "secondary", "rationale": "High blood pressure is cited as a major underlying driver of heart failure."},
    {"article_id": "art_10", "condition_name": "Type 2 diabetes mellitus", "icd10cm_code": "E11.9", "tier": "tertiary", "rationale": "Diabetes is mentioned as a key comorbid condition worsening prognosis."}
]

def get_chapter(code_str):
    c = code_str.replace(".", "").upper()
    letter = c[0]
    num = int(c[1:3]) if c[1:3].isdigit() else 0
    if letter in ['A', 'B']:
        return "1: Infectious (A00-B99)"
    elif letter == 'C' or (letter == 'D' and num <= 49):
        return "2: Neoplasms (C00-D49)"
    elif letter == 'D' and num >= 50:
        return "3: Blood & Immune (D50-D89)"
    elif letter == 'E':
        return "4: Endocrine & Metabolic (E00-E89)"
    elif letter == 'F':
        return "5: Mental & Behavioral (F01-F99)"
    elif letter == 'G':
        return "6: Nervous System (G00-G99)"
    elif letter == 'H' and num <= 59:
        return "7: Eye & Adnexa (H00-H59)"
    elif letter == 'H' and num >= 60:
        return "8: Ear & Mastoid (H60-H95)"
    elif letter == 'I':
        return "9: Circulatory System (I00-I99)"
    elif letter == 'J':
        return "10: Respiratory System (J00-J99)"
    elif letter == 'K':
        return "11: Digestive System (K00-K95)"
    elif letter == 'L':
        return "12: Skin (L00-L99)"
    elif letter == 'M':
        return "13: Musculoskeletal (M00-M99)"
    elif letter == 'N':
        return "14: Genitourinary (N00-N99)"
    elif letter == 'O':
        return "15: Pregnancy (O00-O9A)"
    elif letter == 'P':
        return "16: Perinatal (P00-P96)"
    elif letter == 'Q':
        return "17: Congenital (Q00-Q99)"
    elif letter == 'R':
        return "18: Symptoms & Signs (R00-R99)"
    elif letter in ['S', 'T']:
        return "19: Injury & Poisoning (S00-T88)"
    elif letter in ['V', 'W', 'X', 'Y']:
        return "20: External Causes (V00-Y99)"
    elif letter == 'Z':
        return "21: Health Status Factors (Z00-Z99)"
    elif letter == 'U':
        return "22: Special Purposes (U00-U85)"
    return "Unknown"

def main():
    order_file = os.path.join("data", "icd10cm", "icd10cm_order_2026.txt")
    cms_codes = {}
    if os.path.exists(order_file):
        with open(order_file, "r", encoding="latin1") as f:
            for line in f:
                parts = line.strip().split(maxsplit=3)
                if len(parts) >= 4:
                    cms_codes[parts[1]] = parts[3]
                    
    out_csv = os.path.join("data", "answer_key.csv")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["article_id", "condition_name", "icd10cm_code", "tier", "icd10cm_chapter", "cms_description", "rationale"])
        for item in ANSWER_KEY_DATA:
            norm = item["icd10cm_code"].replace(".", "").upper()
            cms_desc = cms_codes.get(norm, "NOT IN CMS TABLE")
            chap = get_chapter(item["icd10cm_code"])
            writer.writerow([
                item["article_id"],
                item["condition_name"],
                item["icd10cm_code"],
                item["tier"],
                chap,
                cms_desc,
                item["rationale"]
            ])
            
    print(f"Wrote {len(ANSWER_KEY_DATA)} rows to {out_csv}")

if __name__ == "__main__":
    main()
