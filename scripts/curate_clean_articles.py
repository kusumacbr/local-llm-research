# ==============================================================================
# DEPRECATED / ARCHIVED - DO NOT USE FOR SCORING OR PIPELINE
# The rewritten articles in this script have been archived to data/articles_curated_rewritten/.
# Active benchmarks strictly use the restored real page text in data/articles/.
# ==============================================================================
import os
import re

raise RuntimeError("scripts/curate_clean_articles.py is deprecated. Use scripts/restore_articles.py instead.")

ARTICLES_DIR = os.path.join("data", "articles_curated_rewritten")
os.makedirs(ARTICLES_DIR, exist_ok=True)

ARTICLES = {}

# ==============================================================================
# Article 1: Asthma
# ==============================================================================
ARTICLES["art_01"] = """Asthma
======

What is asthma?
---------------
Asthma is a chronic (long-term) lung disease. It affects your airways, the tubes that carry air in and out of your lungs. When you have asthma, your airways can become inflamed and narrowed. This can cause wheezing, coughing, and tightness in your chest. When these symptoms get worse than usual, it is called an asthma attack or flare-up.

What causes asthma?
-------------------
The exact cause of asthma is unknown. Genetics and your environment likely play a role in who gets asthma.

An asthma attack can happen when you are exposed to an asthma trigger. An asthma trigger is something that can set off or worsen your asthma symptoms. Different triggers can cause different types of asthma:

- Allergic asthma is caused by allergens. Allergens are substances that cause an allergic reaction, including dust mites, mold, pets, pollen from grass, trees, and weeds, and waste from pests such as cockroaches and mice.
- Nonallergic asthma is caused by triggers that are not allergens, such as breathing in cold air, certain medicines, household chemicals, infections such as colds and the flu, outdoor air pollution, and tobacco smoke.
- Occupational asthma is caused by breathing in chemicals or industrial dusts at work.
- Exercise-induced asthma happens during physical exercise, especially when the air is dry.

Asthma triggers may be different for each person and can change over time.

Who is at risk for asthma?
--------------------------
Asthma affects people of all ages, but it often starts during childhood. Certain factors can raise your risk of having asthma:
- Being exposed to secondhand smoke when your mother is pregnant with you or when you are a small child.
- Being exposed to certain substances at work, such as chemical irritants or industrial dusts.
- Genetics and family history: you are more likely to have asthma if one of your parents has it, especially if it is your mother.
- Race or ethnicity: Black and African Americans and Puerto Ricans are at higher risk of asthma than people of other races or ethnicities.
- Having other diseases or conditions such as obesity and allergic rhinitis or allergies.
- Often having viral respiratory infections as a young child.
- Sex: in children, asthma is more common in boys; in teens and adults, it is more common in women.

What are the symptoms of asthma?
--------------------------------
The symptoms of asthma include:
- Chest tightness
- Coughing, especially at night or early morning
- Shortness of breath
- Wheezing, which causes a whistling sound when you breathe out

These symptoms can range from mild to severe. You may have them every day or only once in a while. When you are having an asthma attack, your symptoms get much worse. The attacks may come on gradually or suddenly and can be life-threatening.

How is asthma diagnosed?
------------------------
Your health care provider may use many tools to diagnose asthma:
- Physical exam and personal medical history.
- Lung function tests, including spirometry, to test how well your lungs work.
- Challenge tests to measure how your airways react to specific exposures (inhaling allergens or medicines that tighten airway muscles).
- Peak expiratory flow (PEF) tests to measure how fast you can blow air out using maximum effort.
- Fractional exhaled nitric oxide (FeNO) tests to measure levels of nitric oxide in your breath to check for lung inflammation.
- Allergy skin or blood tests if you have a history of allergies to identify immune triggers.

What are the treatments for asthma?
-----------------------------------
If you have asthma, you will work with your health care provider to create a treatment plan:
- Strategies to avoid triggers: for example, keeping homes and cars free from tobacco smoke.
- Short-term relief medicines (quick-relief medicines): these help relieve symptoms during an asthma attack, including fast-acting bronchodilator inhalers.
- Control medicines: daily medications (such as inhaled corticosteroids) that reduce airway inflammation and prevent narrowing.
- Bronchial thermoplasty: for adults with severe uncontrolled asthma, a procedure using heat to shrink airway smooth muscle to reduce constriction.
"""

# ==============================================================================
# Article 2: High Blood Pressure
# ==============================================================================
ARTICLES["art_02"] = """High Blood Pressure
===================

What is blood pressure?
-----------------------
Blood pressure is the force of your blood pushing against the walls of your arteries. Each time your heart beats, it pumps blood into the arteries. Your blood pressure is highest when your heart beats, pumping the blood. This is called systolic pressure. When your heart is at rest, between beats, your blood pressure falls. This is called diastolic pressure.

Your blood pressure reading uses these two numbers, usually with systolic written before or above diastolic (for example, 120/80 mm Hg means a systolic of 120 and a diastolic of 80).

How is high blood pressure diagnosed?
-------------------------------------
High blood pressure usually has no symptoms. The only way to find out if you have it is to get regular blood pressure checks from your health care provider using a blood pressure cuff, gauge, and stethoscope or electronic sensor. Providers take two or more readings at separate appointments before making a formal diagnosis.

Blood Pressure Categories for Adults:
- Normal: Systolic less than 120 and Diastolic less than 80 mm Hg.
- Elevated: Systolic 120 to 129 and Diastolic less than 80 mm Hg.
- High Blood Pressure Stage 1: Systolic 130 to 139 or Diastolic 80 to 89 mm Hg.
- High Blood Pressure Stage 2: Systolic 140 or higher or Diastolic 90 mm Hg or higher.
- Hypertensive Crisis: Systolic higher than 180 and/or Diastolic higher than 120 mm Hg (requires emergency medical care).

What are the different types of high blood pressure?
----------------------------------------------------
There are two main types of high blood pressure:
- Primary (essential) hypertension: This is the most common type of high blood pressure. For most people, it develops gradually over time as they age without a single identifiable secondary cause.
- Secondary hypertension: This type is caused by another underlying medical condition (such as kidney disease, thyroid disorders, or sleep apnea) or the use of certain medications. It often improves once the primary cause is treated.

Why is high blood pressure dangerous?
-------------------------------------
When blood pressure stays high over time, it forces the heart to work harder to circulate blood. Uncontrolled high blood pressure can damage blood vessel walls and lead to life-threatening complications, including:
- Heart attack (myocardial infarction)
- Heart disease and coronary artery disease
- Stroke and cerebral infarction
- Heart failure
- Kidney failure and chronic kidney disease
- Vision loss and vascular dementia

Treatments for high blood pressure
----------------------------------
Treatments include heart-healthy lifestyle changes and prescription antihypertensive medications:
- Lifestyle modifications: eating a low-sodium, heart-healthy diet (such as the DASH diet), exercising regularly, maintaining a healthy body weight, limiting alcohol, and quitting smoking.
- Medications: blood pressure lowering drugs such as ACE inhibitors, angiotensin receptor blockers (ARBs), calcium channel blockers, and thiazide diuretics. Many patients require two or more medicines to achieve their target blood pressure.
"""

# ==============================================================================
# Article 3: Pneumonia
# ==============================================================================
ARTICLES["art_03"] = """Pneumonia
=========

What is pneumonia?
------------------
Pneumonia is an infection in one or both of your lungs. It causes the air sacs (alveoli) of your lungs to fill up with fluid or pus. Pneumonia can range from mild (sometimes referred to as walking pneumonia) to life-threatening, depending on the pathogen, patient age, and underlying health.

What causes pneumonia?
----------------------
Bacterial, viral, and fungal infections can all cause pneumonia:

1. Bacterial pneumonia:
Bacteria are the most common cause of community-acquired pneumonia. Bacterial pneumonia can occur on its own or develop after a viral upper respiratory infection such as a cold or influenza. Common bacterial causes include:
- Streptococcus pneumoniae (pneumococcus)
- Legionella pneumophila (the cause of Legionnaires' disease)
- Mycoplasma pneumoniae (common cause of atypical or mild pneumonia)
- Chlamydia pneumoniae
- Haemophilus influenzae type b (Hib)

2. Viral pneumonia:
Viruses that infect the respiratory tract can cause pneumonia. Viral pneumonia is often mild, but can become severe and predispose individuals to secondary bacterial pneumonia. Common viral causes include:
- Influenza viruses (flu)
- Respiratory syncytial virus (RSV)
- SARS-CoV-2 (the coronavirus that causes COVID-19)
- Common cold viruses (rhinoviruses and adenoviruses)

3. Fungal pneumonia:
Fungal pneumonia is most common in individuals with chronic health problems or compromised immune systems. Types include:
- Pneumocystis pneumonia (PCP), caused by Pneumocystis jirovecii
- Coccidioidomycosis (Valley fever), found in southwestern United States
- Histoplasmosis, associated with bird and bat droppings
- Cryptococcal pneumonia

4. Aspiration pneumonia:
Occurs when food, saliva, liquid, or vomit is accidentally breathed into the lungs, allowing oral bacteria to colonize the lower airways.

Risk factors
------------
Risk factors include older age (65 and older), young age (children under 2), chronic medical conditions (such as asthma, chronic obstructive pulmonary disease, heart disease, diabetes, and sickle cell disease), weakened immune systems, smoking, hospitalization, and being on a ventilator.

Symptoms of pneumonia
---------------------
Symptoms can vary from mild to severe and include:
- High fever, shaking chills, and sweating
- Cough, which may produce greenish, yellow, or bloody mucus
- Shortness of breath and rapid breathing
- Sharp or stabbing chest pain that gets worse with deep breathing or coughing
- Fatigue, loss of appetite, nausea, vomiting, or diarrhea
- Confusion or changes in mental awareness, especially in older adults

Diagnosis and Treatment
-----------------------
Pneumonia is diagnosed through medical history, physical examination (listening to lung crackles with a stethoscope), chest X-rays, blood tests (complete blood count, blood cultures), pulse oximetry, and sputum tests. Treatment depends on the type of pneumonia:
- Antibiotics are used to treat bacterial pneumonia.
- Antiviral medicines may be prescribed for viral pneumonia (such as oseltamivir for influenza).
- Antifungal medications treat fungal pneumonia.
- Supportive care includes fever reducers, cough medicine, rest, fluids, and supplemental oxygen or hospitalization for severe cases.
"""

# ==============================================================================
# Article 4: Alzheimer's Disease
# ==============================================================================
ARTICLES["art_04"] = """Alzheimer's Disease
===================

What is Alzheimer's disease?
----------------------------
Alzheimer's disease is a progressive neurological brain disorder and the most common cause of dementia among older adults. Dementia is the loss of cognitive functioning (thinking, remembering, and reasoning) to such an extent that it interferes with a person's daily life and activities. Alzheimer's disease destroys brain cells and neural connections, beginning in regions of the brain that control memory, thought, and language.

Stages and progression
----------------------
Alzheimer's progresses gradually through stages:
- Preclinical stage: Brain changes begin years before noticeable symptoms develop.
- Mild cognitive impairment (MCI): A condition characterized by subtle memory lapses or cognitive changes greater than expected for normal aging, without preventing independent living. Many people with MCI eventually progress to Alzheimer's disease.
- Mild Alzheimer's disease: Symptoms become apparent. People experience greater memory loss, wander and get lost in familiar places, repeat questions, and take longer to complete normal daily tasks.
- Moderate Alzheimer's disease: Damage spreads to areas controlling language, reasoning, conscious thought, and sensory processing. Individuals may have trouble recognizing family members, develop hallucinations or paranoia, and require assistance with bathing and dressing.
- Severe Alzheimer's disease: Plaques and tangles spread throughout the brain tissue. Patients lose the ability to communicate, cannot recognize loved ones, become bedridden, and require around-the-clock intensive nursing care.

Risk factors
------------
While the exact etiology remains under research, known risk factors include:
- Age: The greatest known risk factor; most individuals with late-onset Alzheimer's are diagnosed at age 65 or older. Early-onset Alzheimer's occurs before age 65 and is rare.
- Genetics and family history: Having a first-degree relative with Alzheimer's increases personal risk.
- Cardiovascular and metabolic conditions: Uncontrolled high blood pressure, diabetes, heart disease, and high cholesterol.
- Neurological factors: History of traumatic brain injury (TBI) or repetitive head concussions.
- Sensory and psychiatric comorbidities: Untreated hearing loss and chronic depression.

Diagnosis and Management
------------------------
Doctors diagnose Alzheimer's through clinical evaluation, cognitive assessments (memory and problem-solving tests), neurological examinations, brain imaging (MRI, CT, PET scans to detect amyloid plaques and brain atrophy), and ruling out other conditions such as vitamin deficiencies or stroke. 

While there is currently no cure for Alzheimer's disease, treatments include medications to manage cognitive symptoms (cholinesterase inhibitors and memantine), disease-modifying therapies targeting amyloid pathology, behavioral symptom management, and supportive caregiver resources.
"""

# ==============================================================================
# Article 5: Chronic Kidney Disease
# ==============================================================================
ARTICLES["art_05"] = """What is Chronic Kidney Disease?
================================

Overview
--------
Chronic kidney disease (CKD) is a medical condition in which the kidneys are damaged and cannot filter blood as effectively as healthy kidneys. Normally, the kidneys filter extra water and wastes out of your blood to produce urine. When kidneys are damaged over months and years, waste products, toxins, and fluid build up in the blood, leading to complications throughout the body.

CKD is a major public health concern affecting more than 35 million adults in the United States (more than 1 in 7 adults). Because kidney damage typically happens slowly over time, many people have no symptoms in the early stages and do not know they have kidney disease.

Causes and Risk Factors
-----------------------
The two leading causes of chronic kidney disease are:
- Diabetes: High blood glucose levels damage the millions of microscopic filtering units (nephrons) inside each kidney over time.
- High blood pressure (hypertension): Uncontrolled elevated blood pressure damages the delicate blood vessels in the kidneys, reducing their ability to clean blood.

Other conditions that can cause or contribute to CKD include:
- Glomerulonephritis: Inflammation of the kidney's filtering units.
- Polycystic kidney disease: An inherited genetic condition causing large fluid-filled cysts to grow in kidney tissue.
- Cardiovascular disease: Heart and blood vessel conditions.
- Autoimmune diseases such as lupus nephritis.
- Repeated urinary tract infections or prolonged urinary tract obstructions (from kidney stones or enlarged prostate).

Stages of Chronic Kidney Disease
--------------------------------
CKD is classified into five stages based on the estimated glomerular filtration rate (eGFR), which measures how many milliliters of blood the kidneys clean per minute:
- Stage 1: Kidney damage with normal or high kidney function (eGFR 90 or greater with persistent protein in urine).
- Stage 2: Kidney damage with mild loss of kidney function (eGFR 60 to 89).
- Stage 3: Moderate loss of kidney function, divided into Stage 3a (eGFR 45 to 59) and Stage 3b (eGFR 30 to 44).
- Stage 4: Severe loss of kidney function (eGFR 15 to 29).
- Stage 5: Kidney failure or End-Stage Renal Disease (eGFR less than 15), requiring kidney replacement therapy (dialysis or kidney transplant) to sustain life.

Complications of CKD
--------------------
As kidney function declines, patients frequently experience serious health complications:
- High blood pressure (both a cause and a consequence of kidney damage)
- Heart disease, heart failure, and elevated risk of heart attacks
- Anemia, caused by reduced production of the hormone erythropoietin (EPO) by diseased kidneys
- Fluid retention (edema) causing swelling in the feet, ankles, and lungs
- Hyperkalemia (high blood potassium levels), which can trigger dangerous cardiac arrhythmias
- Metabolic acidosis (buildup of acid in bodily fluids)
- Mineral and bone disorder, leading to weak, brittle bones and vascular calcification

Symptoms and Diagnosis
----------------------
Early CKD is usually silent. Advanced CKD produces symptoms such as fatigue, swollen ankles or feet, puffiness around the eyes, changes in urination frequency, loss of appetite, nausea, itchy skin, and muscle cramps. CKD is diagnosed using two simple tests:
1. eGFR blood test: Measures creatinine levels to estimate filtering capacity.
2. Urine albumin-to-creatinine ratio (uACR): Detects albumin (protein) leaking into urine, a marker of kidney filter damage.

Treatment focuses on slowing kidney damage through blood pressure control (using ACE inhibitors or ARBs), diabetes management, dietary modifications (reducing sodium, potassium, and phosphorus), and preparing for renal replacement therapy if stage 5 occurs.
"""

# ==============================================================================
# Article 6: Chronic Kidney Disease and Diabetes
# ==============================================================================
ARTICLES["art_06"] = """Chronic Kidney Disease and Diabetes
===================================

What to know
------------
Chronic kidney disease (CKD) is common in people with diabetes. Approximately 1 in 3 adults with diabetes develops kidney disease (often referred to as diabetic kidney disease or diabetic nephropathy). Both type 1 and type 2 diabetes can cause kidney damage. Because CKD develops slowly with few symptoms in early stages, routine clinical screening is essential to catch and treat kidney damage early.

How diabetes causes kidney damage
---------------------------------
Each human kidney contains approximately one million microscopic filtering units called nephrons. Over years, chronically high blood sugar levels damage the delicate microvascular blood vessels inside the nephrons, causing them to thicken and leak. Damaged filters allow essential proteins like albumin to leak into the urine rather than remaining in the bloodstream.

In addition, many people with diabetes also develop high blood pressure. High blood pressure further strains and stiffens renal blood vessels, accelerating kidney tissue scarring and loss of filtration capacity. If left untreated, diabetic kidney disease can progress to end-stage kidney failure, requiring dialysis or a kidney transplant.

Risk factors for kidney disease in diabetes
-------------------------------------------
Your risk of developing kidney disease increases if you have:
- Long-standing diabetes or poorly controlled blood glucose levels
- High blood pressure (hypertension)
- High blood cholesterol and triglyceride levels
- A history of cigarette smoking
- A family history of kidney failure
- Overweight or obesity

Tips for protecting your kidneys
--------------------------------
Managing your diabetes effectively is the most important step to prevent or slow diabetic kidney disease:
- Keep blood sugar levels in your target range and check your A1C regularly (typically at least twice a year).
- Manage blood pressure to your target goal (generally below 130/80 or 140/90 mm Hg as prescribed by your doctor).
- Take prescribed kidney-protective blood pressure medications, such as ACE inhibitors or angiotensin receptor blockers (ARBs), which protect kidney filters even in patients without hypertension.
- Maintain target blood cholesterol and lipid levels.
- Follow a kidney-friendly nutrition plan: consume lower sodium foods to control blood pressure and avoid excess protein that overburdens kidneys.
- Engage in regular physical activity and avoid over-the-counter NSAID pain relievers (like ibuprofen and naproxen) that can harm kidney function.

Testing and Prevention
----------------------
Individuals with diabetes should undergo annual kidney screening:
1. A urine test for albumin (proteinuria) to detect early leakage.
2. A blood test for serum creatinine to calculate eGFR.

For individuals with prediabetes, taking proactive steps through healthy diet and weight loss can prevent progression to type 2 diabetes and avoid kidney complications altogether.
"""

# ==============================================================================
# Article 7: Metabolic Syndrome
# ==============================================================================
ARTICLES["art_07"] = """Metabolic Syndrome
==================

What is metabolic syndrome?
---------------------------
Metabolic syndrome is the clinical name for a cluster of interrelated metabolic risk factors that occur together, dramatically increasing a person's risk of cardiovascular disease, type 2 diabetes, and stroke. Having just one risk factor raises cardiovascular risk, but when three or more of the specific criteria occur simultaneously, a diagnosis of metabolic syndrome is made.

The 5 defining diagnostic criteria:
A diagnosis requires at least 3 of the following 5 factors:
1. Abdominal obesity (large waistline): Waist circumference of 40 inches or more in men, or 35 inches or more in women (often described as an apple-shaped body). Excess visceral abdominal fat is a stronger predictor of heart disease than subcutaneous fat in other parts of the body.
2. High blood triglycerides: Fasting triglyceride level of 150 mg/dL or higher, or being on medication for high triglycerides.
3. Low HDL cholesterol: HDL (good) cholesterol less than 40 mg/dL in men or less than 50 mg/dL in women, or taking medication for low HDL.
4. High blood pressure: Systolic pressure of 130 mm Hg or higher, diastolic pressure of 85 mm Hg or higher, or taking prescription blood pressure medication.
5. High fasting blood glucose: Fasting blood sugar level of 100 mg/dL or higher (impaired fasting glucose), or taking medication for high blood glucose.

Causes of metabolic syndrome
----------------------------
Metabolic syndrome arises from complex interactions between genetic predisposition and lifestyle factors:
- Insulin resistance: A condition in which muscle, fat, and liver cells do not respond effectively to the hormone insulin. As a consequence, the pancreas produces extra insulin, but blood glucose remains elevated, triggering abnormal lipid metabolism and endothelial dysfunction.
- Overweight and physical inactivity: Sedentary lifestyle and excess adipose tissue directly promote insulin resistance and chronic systemic inflammation.
- Genetics and ethnicity: Risk is higher in Mexican Americans, followed by non-Hispanic Whites and African Americans.
- Underlying conditions: Women with polycystic ovary syndrome (PCOS) or a history of gestational diabetes are at substantially elevated risk.
- Medications: Certain antipsychotics, antidepressants, and corticosteroids can trigger weight gain and metabolic disruptions.

Health consequences
-------------------
Metabolic syndrome doubles the risk of heart disease and stroke, and increases the risk of developing type 2 diabetes by up to five-fold. It is also linked to nonalcoholic fatty liver disease (NAFLD), chronic kidney disease, sleep apnea, and peripheral vascular disease.

Treatment and prevention
------------------------
The primary approach is therapeutic lifestyle change:
- Heart-healthy diet: Emphasizing fruits, vegetables, whole grains, lean protein, and reduced saturated fats, refined carbohydrates, and added sugars.
- Routine physical activity: At least 150 minutes of moderate-intensity aerobic exercise per week.
- Weight loss: Losing 7% to 10% of total body weight substantially improves insulin sensitivity, lowers blood pressure, and normalizes lipid profiles.
- Medications: When lifestyle changes are insufficient, doctors prescribe medications to control individual components, including antihypertensives, statins, fibrates, and metformin.
"""

# ==============================================================================
# Article 8: Stroke
# ==============================================================================
ARTICLES["art_08"] = """Stroke
======

What is a stroke?
-----------------
A stroke (cerebrovascular accident) occurs when blood flow to a region of the brain is interrupted or reduced, depriving brain tissue of oxygen and vital nutrients. Within minutes, brain cells begin to die. A stroke is a medical emergency that can lead to permanent brain injury, long-term physical and cognitive disability, or death. Immediate emergency care is critical to limit brain damage.

Types of stroke
---------------
There are two primary categories of stroke, as well as a related warning event:

1. Ischemic stroke:
The most common type, accounting for roughly 87% of all strokes. It occurs when a blood clot (thrombus or embolus) blocks or narrows an artery leading to or within the brain. Ischemic strokes can result from atherosclerosis (plaque buildup inside arteries) or cardiac conditions like atrial fibrillation that launch blood clots into cerebral circulation.

2. Hemorrhagic stroke:
Occurs when a weakened blood vessel in the brain ruptures and leaks blood into or around surrounding brain tissue. Causes include chronic untreated high blood pressure, cerebral aneurysms, arteriovenous malformations (AVMs), and head trauma.

3. Transient ischemic attack (TIA):
Often called a mini-stroke, a TIA is a temporary blockage of blood flow to the brain that resolves without causing permanent infarction. However, a TIA is a serious warning sign indicating high immediate risk for a full ischemic stroke.

Major risk factors
------------------
The leading treatable risk factors for stroke include:
- High blood pressure (hypertension): The single most important modifiable risk factor for both ischemic and hemorrhagic stroke.
- Heart disease: Including coronary artery disease, heart valve disorders, and especially atrial fibrillation, which causes irregular heart contractions that promote clot formation.
- Diabetes: Damages blood vessels and promotes atherosclerosis.
- Smoking and tobacco use: Damages arterial lining and doubles ischemic stroke risk.
- High blood cholesterol and dyslipidemia: Contributes to carotid artery stenosis.
- Obesity, lack of exercise, and unhealthy diet.
- Non-modifiable factors: Older age, family history, and race/ethnicity (African American and Hispanic populations have elevated stroke incidence).

Symptoms of a stroke
--------------------
Stroke symptoms appear suddenly. The FAST acronym outlines key warning signs:
- F - Face: One side of the face droops or is numb; smile is uneven.
- A - Arms: One arm drifts downward when both arms are raised.
- S - Speech: Slurred speech or difficulty speaking and understanding.
- T - Time: Time to call 911 immediately if any of these signs are present.

Other symptoms include sudden numbness or weakness on one side of the body, sudden confusion, trouble seeing in one or both eyes, loss of balance or coordination, and a sudden severe headache with no known cause.

Treatment
---------
Emergency treatment depends on the stroke type:
- Ischemic stroke: Intravenous thrombolytic therapy (clot-dissolving tissue plasminogen activator, or tPA) administered within 3 to 4.5 hours of symptom onset, or mechanical thrombectomy (catheter-based clot retrieval).
- Hemorrhagic stroke: Emergency surgery to repair ruptured aneurysms or relieve intracranial pressure, along with medications to reverse blood thinners and control blood pressure.
- Long-term rehabilitation: Physical, occupational, and speech therapy alongside antiplatelet medications (aspirin), statins, and antihypertensive drugs to prevent recurrence.
"""

# ==============================================================================
# Article 9: COPD
# ==============================================================================
ARTICLES["art_09"] = """Chronic Obstructive Pulmonary Disease (COPD)
=============================================

What is COPD?
-------------
Chronic obstructive pulmonary disease (COPD) is a progressive inflammatory lung disease that causes obstructed airflow from the lungs. COPD develops gradually over many years and makes breathing increasingly difficult. It is a leading cause of disability and death worldwide.

Main conditions composing COPD
------------------------------
COPD primarily comprises two interrelated conditions:
- Emphysema: The walls between the tiny air sacs (alveoli) in the lungs are damaged and destroyed. As a result, the air sacs lose their natural elasticity, become enlarged, and trap air inside, reducing the surface area available for oxygen and carbon dioxide exchange.
- Chronic bronchitis: The lining of the bronchial airways is constantly irritated and inflamed. This chronic inflammation causes the airway lining to swell and produce excessive thick mucus, leading to a persistent productive cough.

Many individuals with COPD also experience asthma overlap, where reversible airway hyperresponsiveness coexists with chronic airflow limitation.

Causes and Risk Factors
-----------------------
- Cigarette smoking: The primary cause of COPD, responsible for up to 85% to 90% of cases. Long-term pipe, cigar, and secondhand smoke exposure also increase risk.
- Environmental exposures: Workplace dusts, chemical fumes, and indoor or outdoor air pollution.
- Genetic factors: Alpha-1 antitrypsin deficiency (AATD), an inherited disorder causing severe early-onset emphysema even in non-smokers due to lack of a protective lung enzyme.
- Childhood respiratory history: Severe childhood lung infections or poorly controlled asthma.

Symptoms of COPD
----------------
Symptoms often do not appear until significant lung tissue damage has occurred:
- Chronic cough (often referred to as smoker's cough) that produces clear, white, yellow, or greenish mucus
- Progressive shortness of breath (dyspnea), especially during physical exertion
- Wheezing and chest tightness
- Frequent respiratory infections (like acute bronchitis and pneumonia)
- Fatigue and lack of energy
- In advanced stages: swelling in ankles, feet, or legs (cor pulmonale or right-sided heart failure), unintended weight loss, and cyanosis (bluish tint to lips and fingernails).

Diagnosis and Treatment
-----------------------
Diagnosis is confirmed through spirometry, a simple pulmonary function test that measures how much air you can inhale and exhale and how quickly you blow air out (FEV1 and FVC). Other diagnostic tools include chest X-rays, CT scans, and arterial blood gas analysis.

While COPD has no cure, treatments relieve symptoms, improve exercise tolerance, and prevent acute exacerbations:
- Smoking cessation: The most critical intervention to halt rapid disease progression.
- Bronchodilators: Inhaled medications that relax bronchial smooth muscles (short-acting for rescue relief and long-acting for maintenance).
- Inhaled corticosteroids: Reduce airway inflammation in patients with frequent flare-ups.
- Pulmonary rehabilitation: A supervised program of exercise training, breathing techniques, and nutritional counseling.
- Supplemental oxygen therapy: For patients with severe chronic hypoxemia.
- Vaccines: Annual influenza, pneumococcal, and COVID-19 immunizations to prevent life-threatening pulmonary infections.
"""

# ==============================================================================
# Article 10: Heart Failure
# ==============================================================================
ARTICLES["art_10"] = """Heart Failure
=============

What is heart failure?
----------------------
Heart failure (congestive heart failure) is a chronic, progressive condition in which the heart muscle is unable to pump enough blood to meet the body's requirements for oxygen and nutrients. Heart failure does not mean that the heart has stopped beating; rather, the heart's pumping chambers have either become too weak or too stiff to fill and circulate blood efficiently.

Types of heart failure
----------------------
Heart failure can affect the left side, the right side, or both sides of the heart:
- Left-sided heart failure: The most common form. It includes heart failure with reduced ejection fraction (HFrEF or systolic failure), where the left ventricle cannot contract forcefully enough, and heart failure with preserved ejection fraction (HFpEF or diastolic failure), where the ventricle cannot relax and fill with blood properly.
- Right-sided heart failure: The right ventricle is too weak to pump deoxygenated blood to the lungs. This most frequently occurs as a result of left-sided heart failure causing fluid backup and pulmonary hypertension.

Causes and Risk Factors
-----------------------
Heart failure typically develops over time secondary to underlying cardiovascular conditions:
- Coronary artery disease and heart attack (myocardial infarction): The most common underlying cause. Narrowed arteries deprive heart muscle of blood, and past heart attacks leave scarred, non-contracting tissue.
- High blood pressure (hypertension): Forces the heart to work harder, causing the ventricular muscle to thicken and eventually stiffen or weaken.
- Cardiomyopathy: Disease of the heart muscle caused by genetic mutations, infections, alcohol misuse, or toxic drug exposures.
- Heart valve disease: Leaking or narrowed valves force the chambers to work overtime.
- Cardiac arrhythmias: Chronic irregular heart rhythms, especially atrial fibrillation.
- Congenital heart defects: Structural heart malformations present from birth.
- Chronic systemic conditions: Type 2 diabetes, obesity, chronic kidney disease, severe lung diseases (such as COPD), severe anemia, and thyroid disease.

Symptoms of heart failure
-------------------------
Common symptoms arise from fluid congestion and reduced organ perfusion:
- Shortness of breath (dyspnea), during exertion, at rest, or when lying flat in bed (orthopnea)
- Persistent coughing or wheezing with white or pink blood-tinged mucus
- Fluid retention (edema) causing swelling in the legs, ankles, feet, or abdomen (ascites)
- Sudden weight gain from fluid accumulation
- Chronic fatigue and overall physical weakness
- Rapid or irregular heartbeat (palpitations)
- Decreased appetite and nausea

Diagnosis and Treatment
-----------------------
Doctors diagnose heart failure using physical exams (checking for leg swelling and crackles in lungs), blood tests (B-type natriuretic peptide or BNP/NT-proBNP), electrocardiograms (ECG), chest X-rays, and echocardiograms (ultrasound to calculate ejection fraction).

Treatment focuses on slowing progression, relieving symptoms, and improving survival:
- Medications: ACE inhibitors, angiotensin receptor-neprilysin inhibitors (ARNIs), beta-blockers, aldosterone receptor antagonists, SGLT2 inhibitors, and diuretics to eliminate excess fluid.
- Implantable devices: Pacemakers, cardiac resynchronization therapy (CRT), and implantable cardioverter-defibrillators (ICDs).
- Lifestyle interventions: Limiting dietary sodium, monitoring daily weight for fluid gain, restricting fluids when indicated, and participating in cardiac rehabilitation.
"""

def main():
    print("Writing curated, clean, readable articles...")
    for art_id, content in ARTICLES.items():
        # Verify no # and no *
        assert '#' not in content, f"Hash found in {art_id}"
        assert '*' not in content, f"Asterisk found in {art_id}"
        filepath = os.path.join(ARTICLES_DIR, f"{art_id}.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        print(f"  Saved {art_id}.txt ({len(content)} chars)")
    print("All 10 articles successfully curated, clean, readable, and verified with 0 '#' and 0 '*'!")

if __name__ == "__main__":
    main()
