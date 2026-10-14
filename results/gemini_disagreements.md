Gemini vs Draft Answer Key Disagreement Analysis
================================================

Model: `gemini-flash-lite-latest`  
Evaluation Date: 2026-10-14  

This document details where `gemini-flash-lite-latest` agreed and disagreed with the 36-condition draft answer key.

art_01: Asthma
--------------

- Exact Matches: J45.909
- Missed by Gemini (in Answer Key, not in Gemini):
  - `J30.9 (Allergic rhinitis)`
- Extra Conditions Extracted by Gemini (not in Answer Key):
  - `T78.40 (Allergies)`
  - `J00 (Common cold)`
  - `J06.9 (Viral respiratory infections)`
  - `E66.9 (Obesity)`
  - `J11.1 (Influenza)`

---

art_02: High Blood Pressure
---------------------------

- Exact Matches: I63.9, I10
- Missed by Gemini (in Answer Key, not in Gemini):
  - `I51.9 (Heart disease, unspecified)`
- Extra Conditions Extracted by Gemini (not in Answer Key):
  - `I50.9 (Heart Failure)`
  - `I21.9 (Heart Attack)`
  - `N19 (Kidney Failure)`
- Tier Disagreements:
  - `I63.9` (Cerebral infarction (Stroke)): Expected `tertiary`, Gemini predicted `secondary`

---

art_03: Pneumonia
-----------------

- Exact Matches: J11.1, J18.9
- Missed by Gemini (in Answer Key, not in Gemini):
  - None
- Extra Conditions Extracted by Gemini (not in Answer Key):
  - `J96.90 (Respiratory failure)`
  - `K76.9 (Liver disease)`
  - `I63.9 (Stroke)`
  - `N19 (Kidney failure)`
  - `N18.9 (Kidney disease)`
  - `J00 (Common cold)`
  - `B38.9 (Coccidioidomycosis)`
  - `R65.21 (Septic shock)`
  - `U07.1 (COVID-19)`
  - `D57.1 (Sickle cell disease)`
  - `B45.1 (Cryptococcal pneumonia)`
  - `A48.1 (Legionnaires' disease)`
  - `B39.9 (Histoplasmosis)`
  - `J85.2 (Lung abscess)`
  - `B59 (Pneumocystis pneumonia)`
  - `I50.9 (Heart failure)`
  - `E11.9 (Diabetes)`
  - `J94.9 (Pleural disorder)`

---

art_04: Alzheimer's Disease
---------------------------

- Exact Matches: G30.9, F03.90
- Missed by Gemini (in Answer Key, not in Gemini):
  - None
- Extra Conditions Extracted by Gemini (not in Answer Key):
  - `I10 (High blood pressure)`
  - `G31.84 (Mild cognitive impairment)`
  - `F32.9 (Depression)`
  - `H91.90 (Hearing loss)`
  - `S06.9X0A (Traumatic brain injury)`

---

art_05: What is Chronic Kidney Disease?
---------------------------------------

- Exact Matches: N18.9, I51.9, E11.9, I10
- Missed by Gemini (in Answer Key, not in Gemini):
  - None
- Extra Conditions Extracted by Gemini (not in Answer Key):
  - `I21.9 (Heart Attack)`
  - `E46 (Malnutrition)`
  - `I63.9 (Stroke)`
  - `E87.2 (Metabolic Acidosis)`
  - `N19 (Kidney Failure)`
  - `N17.9 (Acute Kidney Injury)`
  - `R60.9 (Edema)`
  - `E66.9 (Overweight or Obesity)`
  - `D64.9 (Anemia)`
- Tier Disagreements:
  - `I51.9` (Heart disease, unspecified): Expected `tertiary`, Gemini predicted `secondary`

---

art_06: Chronic Kidney Disease and Diabetes
-------------------------------------------

- Exact Matches: N18.9, I10
- Missed by Gemini (in Answer Key, not in Gemini):
  - `E11.22 (Type 2 diabetes mellitus with diabetic chronic kidney disease)`
  - `I51.9 (Heart disease, unspecified)`
- Extra Conditions Extracted by Gemini (not in Answer Key):
  - `I63.9 (Stroke)`
  - `R73.09 (Prediabetes)`
  - `I25.10 (Heart disease)`
  - `E10.9 (Type 1 diabetes mellitus)`
  - `E11.9 (Diabetes mellitus)`

---

art_07: Metabolic Syndrome
--------------------------

- Exact Matches: E66.9, E88.81, E11.9, I10
- Missed by Gemini (in Answer Key, not in Gemini):
  - `I25.10 (Atherosclerotic heart disease (Coronary artery disease))`
  - `E78.5 (Hyperlipidemia, unspecified)`
- Extra Conditions Extracted by Gemini (not in Answer Key):
  - `E28.2 (Polycystic ovary syndrome)`
  - `R73.9 (Insulin resistance)`
  - `I51.9 (Heart disease)`
  - `I63.9 (Stroke)`

---

art_08: Stroke
--------------

- Exact Matches: I48.91, I63.9, G45.9, I10, E11.9
- Missed by Gemini (in Answer Key, not in Gemini):
  - None
- Extra Conditions Extracted by Gemini (not in Answer Key):
  - `Q28.2 (Arteriovenous malformation)`
  - `I67.1 (Aneurysm)`
  - `I51.9 (Heart diseases)`
  - `I65.2 (Carotid artery disease)`
  - `E66.9 (Obesity)`
  - `I61.9 (Hemorrhagic stroke)`
  - `E78.5 (High cholesterol)`
- Tier Disagreements:
  - `I48.91` (Unspecified atrial fibrillation): Expected `tertiary`, Gemini predicted `secondary`
  - `E11.9` (Type 2 diabetes mellitus): Expected `tertiary`, Gemini predicted `secondary`

---

art_09: Chronic Obstructive Pulmonary Disease (COPD)
----------------------------------------------------

- Exact Matches: J44.9, J42, J43.9
- Missed by Gemini (in Answer Key, not in Gemini):
  - `J45.909 (Unspecified asthma, uncomplicated)`
- Extra Conditions Extracted by Gemini (not in Answer Key):
  - `E88.01 (Alpha-1 Antitrypsin Deficiency)`

---

art_10: Heart Failure
---------------------

- Exact Matches: I25.10, I50.9, E11.9, I10
- Missed by Gemini (in Answer Key, not in Gemini):
  - None
- Extra Conditions Extracted by Gemini (not in Answer Key):
  - `I21.9 (Heart attack)`
  - `R05.9 (Coughing)`
  - `I26.99 (Blood clot in your lung)`
  - `N19 (Kidney damage)`
  - `I49.9 (Arrhythmia)`
  - `U07.1 (COVID-19)`
  - `I38 (Endocarditis)`
  - `J44.9 (COPD)`
  - `R60.9 (Edema)`
  - `E66.9 (Obesity)`
  - `G47.30 (Sleep apnea)`
  - `Q24.9 (Congenital heart defects)`
  - `D64.9 (Anemia)`
  - `E46 (Malnutrition)`
  - `K76.9 (Liver damage)`
  - `K74.60 (Cirrhosis)`
  - `I50.811 (Right-sided heart failure)`
  - `N18.9 (Chronic kidney disease)`
  - `E83.119 (Iron overload disease)`
  - `I50.1 (Left-sided heart failure)`
  - `B20 (HIV)`
  - `R53.83 (Fatigue)`
  - `I27.20 (Pulmonary hypertension)`
  - `E07.9 (Thyroid disease)`
  - `R11.0 (Nausea)`
  - `I42.9 (Cardiomyopathy)`
  - `F10.20 (Alcohol use disorder)`
  - `I46.9 (Sudden cardiac arrest)`
- Tier Disagreements:
  - `E11.9` (Type 2 diabetes mellitus): Expected `tertiary`, Gemini predicted `secondary`

---

