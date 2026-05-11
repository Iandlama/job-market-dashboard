# 📊 IT & Data Science Job Market Dashboard

[![GitHub Pages](https://img.shields.io/badge/Live-Dashboard-blue)](https://ТВОЙ-USERNAME.github.io/job-market-dashboard/)

Interactive dashboard analyzing **5,000+ job postings** in Data Science and IT from Russian and global job markets.

## 🚀 Live Demo

👉 **[Open Dashboard](https://iandlama.github.io/job-market-dashboard/)**


## 📈 Features

- **Salary Distribution** — Histogram with 5th-95th percentile
- **Top Categories** — Horizontal bar chart
- **Experience Levels** — Junior to Lead breakdown
- **Salary by Experience** — Box plot analysis
- **Top Skills** — 15 most in-demand skills
- **Searchable Table** — Browse 5,000+ jobs with pagination
- **Filters** — Category & Experience level


## 🛠️ Tech Stack

- **Python** — Scraping & cleaning
- **Pandas** — Data processing
- **Plotly.js** — Interactive charts
- **GitHub Pages** — Hosting

## 📂 Project Structure

```
├── index.html          # Dashboard (GitHub Pages)
├── vis.py              # Generate dashboard from CSV
├── cleaner.py          # Merge & clean datasets
├── scaper.py           # Scrape Habr Career
├── final_cleaned.csv   # Cleaned dataset (5,000+ rows)
└── requirements.txt    # Python dependencies
```

## 🔄 Data Pipeline

### 1. Scraping (`scaper.py`)
- Scraped vacancies 
- Used `cloudscraper` to bypass Cloudflare protection
- Searched by 32 IT/DS keywords (Python, Data Scientist, DevOps, etc.)
- Extracted: title, company, salary, skills, date, link


### 2. Cleaning & Merging (`cleaner.py`)
- Applied IT/DS keyword filter to remove non-tech roles
- Translated Russian titles to English via `deep-translator` (Google Translate API)
- Normalized salaries: RUB → USD conversion
- Extracted experience level from job titles (Junior/Middle/Senior/Lead)
- Categorized jobs into 12 domains (Data Science, Backend, DevOps, etc.)
- Removed duplicates by title + company + date
- Sampled to **5,300 clean records**
- Output: `final_cleaned.csv`

### 3. Visualization (`vis.py`)
- Built interactive HTML dashboard with Plotly.js
- Created 5 charts: histogram, bar charts, box plot
- Added searchable table with pagination (20 rows/page)
- Implemented filters by category and experience level
- Output: `index.html` (hosted on GitHub Pages)

### Pipeline Flow
```
Habr Career (scraping)
       ↓
   habr_vacancies.csv
       ↓
   ┌── cleaner.py ──┐
   │  Merge 3 sources │
   │  Clean & translate│
   │  Deduplicate      │
   │  Enrich & sample  │
   └──────────────────┘
       ↓
   final_cleaned.csv
       ↓
   vis.py (dashboard)
       ↓
   index.html → GitHub Pages 🚀
```

## 🔧 How to Run Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Scrape data (optional)
python scaper.py

# 3. Clean & merge data
python cleaner.py

# 4. Generate dashboard
python vis.py
```

## 📊 Key Findings

- **Data Science** is the most in-demand category (27.7%)
- **Middle-level** positions dominate the market
- **Python, SQL, Docker** are top required skills
- Median salary: **$85,000/year** (global average)

## 👤 Author

- Made by [@ТВОЙ-USERNAME](https://github.com/ТВОЙ-USERNAME)
- Educational project for Data Science course

---

⭐ Star this repo if you find it useful!
```

Замени `ТВОЙ-USERNAME` на свой GitHub username, сохрани и отправь в репозиторий:

```bash
git add README.md
git commit -m "Add README"
git push
```
