# 📊 IT & Data Science Job Market Dashboard

[![GitHub Pages](https://img.shields.io/badge/Live-Dashboard-blue)](https://ТВОЙ-USERNAME.github.io/job-market-dashboard/)

Interactive dashboard analyzing **5,000+ job postings** in Data Science and IT from Russian and global job markets.

## 🚀 Live Demo

👉 **[Open Dashboard](https://ТВОЙ-USERNAME.github.io/job-market-dashboard/)**


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
