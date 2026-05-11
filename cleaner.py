"""
FINAL CLEANER: 3 sources → 1 clean dataset
Fast translation using Google Translate (deep-translator)
"""

import re
import pandas as pd
import os
from datetime import datetime
import time
from deep_translator import GoogleTranslator

# ============================================================
# CONFIG
# ============================================================
home = os.path.expanduser("~")
DOWNLOADS = os.path.join(home, "Downloads")

VACANCIES_FILE = os.path.join(DOWNLOADS, "vacancies.csv")
HABR_FILE = os.path.join(DOWNLOADS, "habr_vacancies_5300.csv")
GLOBAL_FILE = os.path.join(DOWNLOADS, "global_job_market_dataset.csv")

timestamp = datetime.now().strftime('%Y%m%d_%H%M')
OUTPUT_FILE = os.path.join(DOWNLOADS, f"final_cleaned_{timestamp}.csv")

# ============================================================
# FAST TRANSLATOR (Google Translate)
# ============================================================
translator = GoogleTranslator(source='ru', target='en')


def translate_batch(texts):
    """Translate only unique texts, cache results"""
    translated = []
    cache = {}  # Translation cache
    ru_count = 0

    for i, text in enumerate(texts):
        if pd.isna(text) or not isinstance(text, str) or text.strip() == '':
            translated.append(text)
        elif not any('а' <= c.lower() <= 'я' or c in 'ёЁ' for c in str(text)):
            translated.append(text)
        elif text in cache:
            translated.append(cache[text])  # Use cached
        else:
            try:
                result = translator.translate(str(text)[:500])
                cache[text] = result if result else text
                translated.append(cache[text])
                ru_count += 1
                time.sleep(0.03)
            except:
                cache[text] = text
                translated.append(text)

        if (i + 1) % 100 == 0:
            print(
                f"      {i+1}/{len(texts)} ({ru_count} unique translated)...", end='\r')

    print(
        f"      Done: {len(texts)} texts, {ru_count} unique translated".ljust(80))
    return translated


# ============================================================
# IT & DS KEYWORDS
# ============================================================
IT_DS_KEYWORDS = [
    'data scient', 'data sci', 'machine learn', 'ml engineer', 'deep learn',
    'nlp', 'computer vision', 'нейросет', 'машинн', 'искусствен',
    'аналитик данн', 'data analyst', 'data engineer', 'big data', 'ai ',
    'программист', 'разработчик', 'developer', 'software engineer',
    'python', 'java', 'javascript', 'c++', 'c#', 'golang', 'php', 'ruby',
    'scala', 'kotlin', 'swift', 'typescript', 'rust', 'react', 'angular',
    'vue', 'node.js', 'django', 'flask', 'spring', '.net', 'fullstack',
    'backend', 'back-end', 'бэкенд', 'frontend', 'front-end', 'фронтенд',
    'devops', 'sre', 'cloud engineer', 'kubernetes', 'docker', 'aws', 'azure',
    'gcp', 'terraform', 'ci/cd', 'qa engineer', 'тестиров', 'test engineer',
    'sql', 'database', 'dba', 'postgresql', 'mysql', 'mongodb', 'redis',
    'android', 'ios', 'mobile dev', 'мобильн', 'flutter', 'system admin',
    'системный админ', 'network engineer', 'security', 'безопасност',
    'cyber', 'project manager', 'product manager', 'tech lead', 'team lead',
    'scrum master', 'руководитель', 'тимлид', 'cto', 'технический директор',
    'bi analyst', 'business intelligence', 'etl', 'blockchain', 'game dev',
    'embedded', 'technical writer', 'it support', 'helpdesk', '1с', 'sap',
]

NON_IT_KEYWORDS = [
    'бухгалт', 'accountant', 'продав', 'sales', 'водител', 'driver',
    'охран', 'уборщ', 'клининг', 'повар', 'cook', 'кассир', 'склад',
    'грузчик', 'строител', 'сантехн', 'электрик', 'врач', 'медсестр',
    'учител', 'преподава', 'юрист', 'lawyer', 'маркетолог', 'smm',
    'рекрут', 'hr ', 'дизайнер интерьер', 'фотограф', 'журналист',
    'риэлтор', 'офис-менеджер', 'секретар', 'мерчендайзер',
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================


def is_it_ds(title: str) -> bool:
    if pd.isna(title) or not isinstance(title, str):
        return False
    t = title.lower().strip()
    for kw in NON_IT_KEYWORDS:
        if kw in t:
            return False
    for kw in IT_DS_KEYWORDS:
        if kw in t:
            return True
    return False


def extract_numeric(salary_str):
    if pd.isna(salary_str) or str(salary_str).strip() in ['', 'Not specified', 'Negotiable', 'nan', 'None']:
        return None
    try:
        nums = re.findall(
            r'\d+\.?\d*', str(salary_str).replace(',', '').replace(' ', ''))
        if nums:
            value = float(nums[0])
            if value <= 0:
                return None
            if value > 100000:
                value = value / 90
            return round(value, 0)
    except:
        pass
    return None


def clean_salary(val) -> str:
    if pd.isna(val) or str(val).strip() in ['', 'nan', 'None']:
        return 'Negotiable'
    s = str(val).strip()
    if any(w in s.lower() for w in ['договор', 'обсуждает', 'negotiable']):
        return 'Negotiable'
    s = s.replace('Зарплата не указана', 'Negotiable')
    s = s.replace('Not specified', 'Negotiable')
    s = s.replace('₽', 'RUB')
    return s[:100]


def extract_experience(title: str) -> str:
    if pd.isna(title):
        return 'Middle'
    t = str(title).lower()
    if any(w in t for w in ['junior', 'младший', 'стажер', 'intern', 'джуниор', 'entry', 'trainee']):
        return 'Junior'
    if any(w in t for w in ['senior', 'старший', 'ведущий', 'сеньор', 'principal', 'staff']):
        return 'Senior'
    if any(w in t for w in ['lead', 'team lead', 'руководитель', 'тимлид', 'лид', 'head of', 'director', 'cto']):
        return 'Lead'
    if any(w in t for w in ['middle', 'мидл']):
        return 'Middle'
    return 'Middle'


def categorize_role(title: str) -> str:
    if pd.isna(title):
        return 'Other IT'
    t = str(title).lower()
    categories = {
        'Data Science': ['data scient', 'machine learn', 'ml engineer', 'deep learn', 'nlp', 'computer vision', 'нейросет', 'аналитик данн', 'data analyst', 'ai researcher', 'ai engineer', 'машинное обучение'],
        'Data Engineering': ['data engineer', 'etl', 'big data', 'spark', 'hadoop', 'airflow', 'kafka', 'инженер данн'],
        'Backend': ['backend', 'python dev', 'java dev', 'php', 'golang', 'ruby', 'c++ dev', 'c# dev', 'scala', 'kotlin', 'node.js', 'django', 'flask', 'spring', '.net'],
        'Frontend': ['frontend', 'react', 'angular', 'vue', 'javascript', 'typescript', 'версталь', 'web developer'],
        'DevOps & Cloud': ['devops', 'sre', 'cloud engineer', 'kubernetes', 'docker', 'aws', 'azure', 'gcp', 'terraform'],
        'QA & Testing': ['qa engineer', 'тестиров', 'test engineer', 'quality assurance'],
        'Mobile': ['android', 'ios', 'mobile dev', 'мобильн', 'flutter', 'swift'],
        'Database': ['sql', 'database', 'dba', 'postgresql', 'mysql', 'mongodb', 'redis', 'oracle', 'баз данн'],
        'System Admin': ['system admin', 'системный админ', 'network engineer', 'linux', 'it support', 'helpdesk'],
        'Security': ['security', 'безопасност', 'cyber', 'пентест'],
        'Management': ['project manager', 'product manager', 'tech lead', 'team lead', 'scrum master', 'руководитель', 'тимлид', 'cto', 'технический директор'],
        'BI & Analytics': ['bi analyst', 'business intelligence', 'power bi', 'tableau'],
    }
    for cat, kws in categories.items():
        for kw in kws:
            if kw in t:
                return cat
    return 'Other IT'


# ============================================================
# MAIN
# ============================================================
print("=" * 60)
print("FINAL CLEANER (Fast Google Translate)")
print("=" * 60)

# 1. HH.ru
print("\n[1/3] HH.ru...")
if os.path.exists(VACANCIES_FILE):
    df_hh = pd.read_csv(VACANCIES_FILE)
    if 'professional_roles' in df_hh.columns:
        df_hh = df_hh[df_hh['professional_roles'].apply(is_it_ds)].copy()
    df_hh['source'] = 'HH.ru'
    df_hh['title'] = df_hh.get('professional_roles', '')
    df_hh['company'] = 'HH.ru employer'
    df_hh['salary'] = df_hh.get('salary', 'Not specified').apply(clean_salary)
    df_hh['skills'] = ''
    df_hh['location'] = df_hh.get('AO', '')
    df_hh['date'] = '2024-05-01'

    print(f"      Translating {len(df_hh)} titles...")
    df_hh['title'] = translate_batch(df_hh['title'].tolist())

    df_hh = df_hh[['source', 'title', 'company',
                   'salary', 'skills', 'location', 'date']]
    print(f"      Final: {len(df_hh):,} rows")
else:
    df_hh = pd.DataFrame()

# 2. Habr
print("\n[2/3] Habr Career...")
if os.path.exists(HABR_FILE):
    df_habr = pd.read_csv(HABR_FILE)
    df_habr['source'] = 'Habr Career'
    df_habr['location'] = ''
    df_habr['salary'] = df_habr['salary'].apply(clean_salary)

    print(f"      Translating {len(df_habr)} titles & companies...")
    df_habr['title'] = translate_batch(df_habr['title'].tolist())
    df_habr['company'] = translate_batch(
        df_habr['company'].fillna('Not specified').tolist())

    if 'date' in df_habr.columns:
        df_habr['date'] = pd.to_datetime(
            df_habr['date'], errors='coerce').dt.strftime('%Y-%m-%d')

    df_habr = df_habr[['source', 'title', 'company',
                       'salary', 'skills', 'location', 'date']]
    print(f"      Final: {len(df_habr):,} rows")
else:
    df_habr = pd.DataFrame()

# 3. Global_Job
print("\n[3/3] Global Job...")
if os.path.exists(GLOBAL_FILE):
    df_global = pd.read_csv(GLOBAL_FILE)
    if 'title' in df_global.columns:
        df_global = df_global[df_global['title'].apply(is_it_ds)].copy()
    df_global['source'] = 'Global_Job'
    df_global['title'] = df_global.get('title', '')

    # Fixed: handle company_size with ranges like '51-200'
    def format_company_size(x):
        if pd.isna(x) or str(x).strip() == '':
            return 'Not specified'
        x = str(x).strip()
        if '-' in x:
            return f"Company ({x} emp.)"
        try:
            return f"Company ({int(float(x))} emp.)"
        except:
            return f"Company ({x} emp.)"

    df_global['company'] = df_global.get(
        'company_size', '').apply(format_company_size)
    df_global['salary'] = df_global.get(
        'starting_salary', 'Not specified').apply(clean_salary)
    df_global['skills'] = df_global.get('skills', '').fillna('')
    df_global['location'] = df_global.get(
        'country', '') + ', ' + df_global.get('city', '').fillna('')
    df_global['date'] = df_global.get('posted_date', '')

    df_global = df_global[['source', 'title', 'company',
                           'salary', 'skills', 'location', 'date']]
    print(f"      Final: {len(df_global):,} rows")
else:
    df_global = pd.DataFrame()

# MERGE
print("\nMerging...")
dfs = [df_hh, df_habr, df_global]
df = pd.concat([d for d in dfs if not d.empty], ignore_index=True)
df = df.dropna(subset=['title'])
df = df[df['title'].str.strip() != '']
before = len(df)
df = df.drop_duplicates(subset=['title', 'company', 'date'], keep='first')
print(f"Combined: {len(df):,} rows (removed {before - len(df):,} duplicates)")

# ENRICH
print("\nEnriching...")
df['salary_num'] = df['salary'].apply(extract_numeric)
print(f"Salary parsed: {df['salary_num'].notna().sum():,} / {len(df):,}")
df['experience_level'] = df['title'].apply(extract_experience)
df['category'] = df['title'].apply(categorize_role)
before = len(df)
df = df[df['category'] != 'Other IT']
print(f"Removed 'Other IT': {before - len(df):,} rows")

# SAMPLE
target = 5300
if len(df) > target * 2:
    df_small = df[df['source'] != 'Global_Job']
    df_global_part = df[df['source'] == 'Global_Job']
    sample_size = target - len(df_small)
    if sample_size > 0 and len(df_global_part) > sample_size:
        df_global_sample = df_global_part.sample(
            n=sample_size, random_state=42)
        df = pd.concat([df_small, df_global_sample], ignore_index=True)
    print(f"Sampled to: {len(df):,} rows")

# SAVE
final_cols = ['source', 'title', 'company', 'salary', 'salary_num',
              'skills', 'location', 'date', 'experience_level', 'category']
df = df[[c for c in final_cols if c in df.columns]]
df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')

print(f"\n{'=' * 60}")
print(f"✅ DONE!")
print(f"{'=' * 60}")
print(f"File: {OUTPUT_FILE}")
print(f"Rows: {len(df):,}")
print(f"Sources: {dict(df['source'].value_counts())}")
print(f"Categories: {dict(df['category'].value_counts().head(5))}")
