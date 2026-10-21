import csv
import os

CMS_ORDER_FILE = os.path.join("data", "icd10cm", "icd10cm_order_2026.txt")
ANSWER_KEY_FILE = os.path.join("data", "answer_key.csv")
BACKUP_KEY_FILE = os.path.join("data", "answer_key_day3_backup.csv")

# Load CMS codes
cms_codes = {}
with open(CMS_ORDER_FILE, "r", encoding="latin1") as f:
    for line in f:
        parts = line.strip().split(maxsplit=3)
        if len(parts) >= 4:
            code_raw = parts[1].upper()
            desc = parts[3]
            cms_codes[code_raw] = desc

def get_chapter_label(code_str):
    c = code_str.replace(".", "").strip().upper()
    letter = c[0]
    num = int(c[1:3]) if len(c) >= 3 and c[1:3].isdigit() else 0
    if letter in ['A', 'B']: return "1: Certain Infectious & Parasitic (A00-B99)"
    elif letter == 'C' or (letter == 'D' and num <= 49): return "2: Neoplasms (C00-D49)"
    elif letter == 'D' and num >= 50: return "3: Blood & Blood-forming Organs (D50-D89)"
    elif letter == 'E': return "4: Endocrine & Metabolic (E00-E89)"
    elif letter == 'F': return "5: Mental & Behavioral (F01-F99)"
    elif letter == 'G': return "6: Nervous System (G00-G99)"
    elif letter == 'H' and num <= 59: return "7: Eye & Adnexa (H00-H59)"
    elif letter == 'H' and num >= 60: return "8: Ear & Mastoid (H60-H95)"
    elif letter == 'I': return "9: Circulatory System (I00-I99)"
    elif letter == 'J': return "10: Respiratory System (J00-J99)"
    elif letter == 'K': return "11: Digestive System (K00-K95)"
    elif letter == 'L': return "12: Skin & Subcutaneous (L00-L99)"
    elif letter == 'M': return "13: Musculoskeletal (M00-M99)"
    elif letter == 'N': return "14: Genitourinary (N00-N99)"
    elif letter == 'O': return "15: Pregnancy & Childbirth (O00-O9A)"
    elif letter == 'P': return "16: Perinatal Period (P00-P96)"
    elif letter == 'Q': return "17: Congenital Malformations (Q00-Q99)"
    elif letter == 'R': return "18: Symptoms & Abnormal Findings (R00-R99)"
    elif letter in ['S', 'T']: return "19: Injury, Poisoning & External (S00-T88)"
    elif letter in ['V', 'W', 'X', 'Y']: return "20: External Causes of Morbidity (V00-Y99)"
    elif letter == 'Z': return "21: Health Status & Contact (Z00-Z99)"
    elif letter == 'U': return "22: Codes for Special Purposes (U00-U85)"
    return "Unknown"

# Define updated conditions list (46 rows)
UPDATED_KEY = [
    # art_01
    ("art_01", "Asthma, unspecified", "J45.909", "primary", "Article is primarily focused on asthma definition, triggers, symptoms and management."),
    ("art_01", "Allergy, unspecified", "T78.40", "secondary", "Allergies documented as significant trigger and comorbid risk factor."),
    ("art_01", "Obesity, unspecified", "E66.9", "secondary", "Obesity explicitly documented as a major comorbid condition and risk factor."),

    # art_02
    ("art_02", "Essential (primary) hypertension", "I10", "primary", "Article is primarily focused on high blood pressure / hypertension diagnosis and control."),
    ("art_02", "Heart failure, unspecified", "I50.9", "secondary", "Heart failure explicitly listed as major cardiovascular complication of hypertension."),
    ("art_02", "Acute myocardial infarction, unspecified (Heart attack)", "I21.9", "secondary", "Heart attack explicitly listed as major complication."),
    ("art_02", "Cerebral infarction (Stroke)", "I63.9", "secondary", "Stroke listed with equal prominence as life-threatening cardiovascular complication."),
    ("art_02", "Kidney failure, unspecified", "N19", "secondary", "Kidney failure explicitly named as target organ damage."),

    # art_03
    ("art_03", "Pneumonia, unspecified organism", "J18.9", "primary", "Article is entirely dedicated to pneumonia causes, symptoms, and treatment."),
    ("art_03", "Influenza", "J11.1", "secondary", "Flu virus covered as prominent cause leading to viral pneumonia."),
    ("art_03", "COVID-19", "U07.1", "secondary", "SARS-CoV-2 / COVID-19 explicitly named under viral etiologies."),
    ("art_03", "Legionnaires' disease", "A48.1", "secondary", "Legionella pneumophila explicitly named under bacterial causes of pneumonia."),

    # art_04
    ("art_04", "Alzheimer's disease, unspecified", "G30.9", "primary", "Article is specifically focused on Alzheimer's disease progression and care."),
    ("art_04", "Dementia in other diseases classified elsewhere without behavioral disturbance", "F02.80", "secondary", "Tabular note under G30 requires coding dementia F02.8-; F03 has an Excludes1 note with G30."),
    ("art_04", "Mild cognitive impairment, so stated", "G31.84", "secondary", "Dedicated section defining mild cognitive impairment as early transition stage to AD."),

    # art_05
    ("art_05", "Chronic kidney disease, unspecified", "N18.9", "primary", "Article explains what chronic kidney disease is, its stages, and consequences."),
    ("art_05", "Essential (primary) hypertension", "I10", "secondary", "High blood pressure is identified as a primary cause and risk factor for CKD."),
    ("art_05", "Type 2 diabetes mellitus", "E11.9", "secondary", "Diabetes is highlighted as the leading cause damaging kidney filters."),
    ("art_05", "Heart disease, unspecified", "I51.9", "tertiary", "Heart disease is mentioned as an elevated risk consequence of CKD."),
    ("art_05", "Anemia, unspecified", "D64.9", "tertiary", "Anemia explicitly detailed as a direct hematologic complication of CKD."),

    # art_06
    ("art_06", "Type 2 diabetes mellitus with diabetic chronic kidney disease", "E11.22", "primary", "Guideline I.B.9 mandates combination code E11.22 when both diabetes and CKD are present."),
    ("art_06", "Chronic kidney disease, unspecified", "N18.9", "primary", "Tabular instruction under E11.22 mandates 'Use additional code to identify stage of CKD (N18.-)'."),
    ("art_06", "Essential (primary) hypertension", "I10", "secondary", "Managing blood pressure is detailed as a vital component to slow CKD progression."),
    ("art_06", "Heart disease, unspecified", "I51.9", "tertiary", "Mentioned as an increased risk for people with both diabetes and CKD."),
    ("art_06", "Cerebral infarction (Stroke)", "I63.9", "tertiary", "Stroke explicitly stated alongside heart disease as major risk."),

    # art_07
    ("art_07", "Metabolic syndrome", "E88.81", "primary", "Article defines metabolic syndrome and its criteria."),
    ("art_07", "Type 2 diabetes mellitus", "E11.9", "secondary", "High blood glucose and progression to diabetes is one of the key pillars."),
    ("art_07", "Essential (primary) hypertension", "I10", "secondary", "High blood pressure is another defining pillar of metabolic syndrome."),
    ("art_07", "Obesity, unspecified", "E66.9", "secondary", "Large waistline / abdominal obesity is a core diagnostic criterion."),
    ("art_07", "Hyperlipidemia, unspecified", "E78.5", "secondary", "High blood triglycerides and low HDL cholesterol are core criteria (E78.2 also acceptable)."),
    ("art_07", "Heart disease, unspecified", "I51.9", "tertiary", "Heart disease mentioned as major vascular consequence."),

    # art_08
    ("art_08", "Cerebral infarction, unspecified (Ischemic stroke)", "I63.9", "primary", "Article is centered around stroke types, symptoms, and emergency care."),
    ("art_08", "Nontraumatic intracerebral hemorrhage (Hemorrhagic stroke)", "I61.9", "primary", "Hemorrhagic stroke defined with equal clinical weight as one of the two main stroke types."),
    ("art_08", "Transient cerebral ischemic attack (TIA)", "G45.9", "secondary", "Mini-strokes (TIAs) are explained in depth as warning events."),
    ("art_08", "Essential (primary) hypertension", "I10", "secondary", "High blood pressure is highlighted as the single biggest treatable risk factor."),
    ("art_08", "Unspecified atrial fibrillation", "I48.91", "tertiary", "Atrial fibrillation mentioned as an important cardiac cause of embolic stroke."),
    ("art_08", "Type 2 diabetes mellitus", "E11.9", "tertiary", "Diabetes mentioned as a contributing vascular risk factor."),

    # art_09
    ("art_09", "Chronic obstructive pulmonary disease, unspecified", "J44.9", "primary", "Article is directly focused on COPD definition, mechanism, and treatment."),
    ("art_09", "Emphysema, unspecified", "J43.9", "secondary", "Emphysema is explained as one of the two main conditions making up COPD."),
    ("art_09", "Unspecified chronic bronchitis", "J42", "secondary", "Chronic bronchitis is explained as the second main condition making up COPD."),
    ("art_09", "Alpha-1-antitrypsin deficiency", "E88.01", "secondary", "Explicitly named genetic etiology of COPD in restored text."),

    # art_10
    ("art_10", "Heart failure, unspecified", "I50.9", "primary", "Article is primarily on heart failure etiology, symptoms, and lifestyle changes."),
    ("art_10", "Atherosclerotic heart disease (Coronary artery disease)", "I25.10", "secondary", "Coronary artery disease is cited as the most common underlying cause."),
    ("art_10", "Essential (primary) hypertension", "I10", "secondary", "High blood pressure is cited as a major underlying driver of heart failure."),
    ("art_10", "Cardiomyopathy, unspecified", "I42.9", "secondary", "Cardiomyopathy explicitly documented under causes of heart failure."),
    ("art_10", "Cardiac arrhythmia, unspecified", "I49.9", "secondary", "Arrhythmias explicitly documented under causes of heart failure."),
    ("art_10", "Type 2 diabetes mellitus", "E11.9", "tertiary", "Diabetes is mentioned as a key comorbid condition worsening prognosis.")
]

# Backup old key
if os.path.exists(ANSWER_KEY_FILE) and not os.path.exists(BACKUP_KEY_FILE):
    import shutil
    shutil.copyfile(ANSWER_KEY_FILE, BACKUP_KEY_FILE)
    print(f"Backed up Day 3 answer key to {BACKUP_KEY_FILE}")

# Write updated answer key
fieldnames = ["article_id", "condition_name", "icd10cm_code", "tier", "icd10cm_chapter", "cms_description", "rationale"]
with open(ANSWER_KEY_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for art_id, cond_name, code, tier, rationale in UPDATED_KEY:
        norm = code.replace(".", "").upper()
        cms_desc = cms_codes.get(norm, cond_name)
        chapter = get_chapter_label(code)
        writer.writerow({
            "article_id": art_id,
            "condition_name": cond_name,
            "icd10cm_code": code,
            "tier": tier,
            "icd10cm_chapter": chapter,
            "cms_description": cms_desc,
            "rationale": rationale
        })

print(f"Wrote updated answer key with {len(UPDATED_KEY)} rows to {ANSWER_KEY_FILE}")
