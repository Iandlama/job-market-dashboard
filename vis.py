"""
ADVANCED INTERACTIVE DASHBOARD - FINAL VERSION
Cleaned table, USD conversion, no extra columns
"""

import webbrowser
import pandas as pd
import os
import re
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================
home = os.path.expanduser("~")
DOWNLOADS = os.path.join(home, "Downloads")

files = [f for f in os.listdir(DOWNLOADS) if f.startswith("final_cleaned_")]
if not files:
    print("ERROR: No final_cleaned_*.csv found in Downloads")
    print("Run cleaner first!")
    exit()

DATA_FILE = os.path.join(DOWNLOADS, sorted(files)[-1])
OUTPUT_FILE = os.path.join(
    DOWNLOADS, f"dashboard_{datetime.now():%Y%m%d_%H%M}.html")

# ============================================================
# LOAD DATA
# ============================================================
print(f"Loading: {DATA_FILE}")
df = pd.read_csv(DATA_FILE)

# ============================================================
# EXTRACT NUMERIC SALARY & CONVERT RUB TO USD
# ============================================================


def extract_numeric(salary_str):
    if pd.isna(salary_str) or str(salary_str).strip() in ['', 'Not specified', 'Negotiable', 'nan']:
        return None
    try:
        nums = re.findall(
            r'[\d]+[.\d]*', str(salary_str).replace(',', '').replace(' ', ''))
        if nums:
            value = float(nums[0])
            if value > 100000:
                value = value / 90
            return round(value, 0)
    except:
        pass
    return None


df['salary_num'] = df['salary'].apply(extract_numeric)

# ============================================================
# CLEAN SALARY TEXT (fix merged strings)
# ============================================================


def clean_salary_text(salary_str):
    if pd.isna(salary_str):
        return 'Negotiable'
    s = str(salary_str)
    s = s.replace('Not specifiedMarket avg:', 'Not specified | Market avg:')
    s = s.replace('Not specified', 'Negotiable')
    s = s.replace('₽', 'RUB')
    return s


df['salary'] = df['salary'].apply(clean_salary_text)
# Create employment_type if missing
if 'employment_type' not in df.columns:
    def detect_employment(title):
        t = str(title).lower()
        if any(w in t for w in ['part-time', 'part time', 'parttime', 'неполный']):
            return 'Part-time'
        if any(w in t for w in ['contract', 'contractor', 'контракт', 'времен']):
            return 'Contract'
        if any(w in t for w in ['intern', 'internship', 'стажер', 'стажировк']):
            return 'Internship'
        return 'Full-time'
    df['employment_type'] = df['title'].apply(detect_employment)

# ============================================================
# CLEAN SKILLS
# ============================================================
if 'skills' in df.columns:
    df['skills_clean'] = df['skills'].fillna('').apply(
        lambda x: ', '.join([s.strip() for s in re.split(
            r'[,;\s]+', str(x)) if len(s.strip()) > 2])
    )
else:
    df['skills_clean'] = '—'

# ============================================================
# STATS
# ============================================================
total = len(df)
companies = df['company'].nunique() if 'company' in df.columns else 0
locations = df['location'].nunique() if 'location' in df.columns else 0
median_sal = df['salary_num'].median()
avg_sal = df['salary_num'].mean()
categories_n = df['category'].nunique() if 'category' in df.columns else 0

# ============================================================
# PREPARE DATA FOR JAVASCRIPT
# ============================================================
js_data = df[['title', 'salary', 'employment_type', 'skills_clean',
              'category', 'experience_level', 'salary_num']].to_json(orient='records')

# ============================================================
# HTML TEMPLATE
# ============================================================
html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IT & Data Science Job Market Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #f0f2f5; color: #1a1a2e; }}
        .hero {{ background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; padding: 50px 40px; text-align: center; }}
        .hero h1 {{ font-size: 2.6em; margin-bottom: 8px; font-weight: 700; }}
        .kpi-row {{ display: flex; justify-content: center; gap: 20px; padding: 30px; background: white; flex-wrap: wrap; }}
        .kpi-card {{ text-align: center; padding: 20px 35px; border-radius: 12px; background: white; min-width: 140px; box-shadow: 0 2px 12px rgba(0,0,0,0.04); }}
        .kpi-value {{ font-size: 2.2em; font-weight: 700; color: #302b63; }}
        .kpi-label {{ font-size: 0.8em; color: #8892b0; text-transform: uppercase; letter-spacing: 1.5px; }}
        .filters {{ display: flex; justify-content: center; gap: 20px; padding: 18px; background: white; margin: 0 20px 20px; border-radius: 12px; flex-wrap: wrap; }}
        .filter-group {{ display: flex; align-items: center; gap: 8px; }}
        .filter-group label {{ font-weight: 600; font-size: 0.9em; color: #302b63; }}
        .filter-group select {{ padding: 9px 20px; border: 1.5px solid #ddd; border-radius: 8px; font-size: 0.9em; background: white; cursor: pointer; }}
        .section {{ max-width: 1200px; margin: 25px auto; background: white; border-radius: 14px; box-shadow: 0 2px 15px rgba(0,0,0,0.04); overflow: hidden; }}
        .section-title {{ font-size: 1.25em; font-weight: 600; padding: 22px 25px 8px; color: #302b63; border-left: 4px solid #302b63; margin: 8px 0 0 18px; }}
        .chart-container {{ padding: 10px 15px; }}
        .insight {{ padding: 14px 25px 22px; background: #fafbfc; border-top: 1px solid #eef0f4; font-size: 0.92em; color: #555; }}
        .insight strong {{ color: #302b63; }}
        .highlight {{ background: #eeedf8; padding: 2px 7px; border-radius: 4px; font-weight: 600; color: #302b63; }}
        .table-section {{ max-width: 1200px; margin: 25px auto; }}
        .table-container {{ background: white; border-radius: 14px; box-shadow: 0 2px 15px rgba(0,0,0,0.04); padding: 22px; }}
        .search-box {{ margin-bottom: 15px; display: flex; gap: 10px; align-items: center; }}
        .search-box input {{ padding: 10px 18px; border: 1.5px solid #ddd; border-radius: 8px; width: 320px; font-size: 0.9em; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 0.88em; }}
        th {{ background: #302b63; color: white; padding: 13px 12px; text-align: left; cursor: pointer; font-weight: 500; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #f0f0f0; }}
        tr:hover {{ background: #f8f7ff; }}
        .salary-badge {{ background: #e8f5e9; color: #2e7d32; padding: 4px 10px; border-radius: 6px; font-size: 0.85em; font-weight: 500; white-space: nowrap; }}
        .type-badge {{ padding: 4px 10px; border-radius: 6px; font-size: 0.8em; font-weight: 600; }}
        .type-Full-time {{ background: #e3f2fd; color: #1565c0; }}
        .type-Part-time {{ background: #fff3e0; color: #e65100; }}
        .type-Contract {{ background: #fce4ec; color: #c62828; }}
        .pagination {{ display: flex; justify-content: center; align-items: center; gap: 12px; padding: 18px; }}
        .pagination button {{ padding: 9px 20px; border: 1.5px solid #302b63; background: white; color: #302b63; border-radius: 8px; cursor: pointer; font-size: 0.9em; }}
        .pagination button:hover {{ background: #302b63; color: white; }}
        .pagination button:disabled {{ opacity: 0.3; cursor: not-allowed; }}
        .pagination .page-info {{ font-weight: 600; color: #302b63; }}
        .footer {{ text-align: center; padding: 30px; color: #8892b0; font-size: 0.85em; }}
    </style>
</head>
<body>

<div class="hero">
    <h1>📊 IT & Data Science Job Market</h1>
    <p>Interactive analysis of {total:,} job postings across {categories_n} categories</p>
</div>

<div class="kpi-row">
    <div class="kpi-card"><div class="kpi-value">{total:,}</div><div class="kpi-label">Total Jobs</div></div>
    <div class="kpi-card"><div class="kpi-value">{companies:,}</div><div class="kpi-label">Companies</div></div>
    <div class="kpi-card"><div class="kpi-value">{locations:,}</div><div class="kpi-label">Locations</div></div>
    <div class="kpi-card"><div class="kpi-value">${median_sal:,.0f}</div><div class="kpi-label">Median Salary</div></div>
    <div class="kpi-card"><div class="kpi-value">${avg_sal:,.0f}</div><div class="kpi-label">Avg Salary</div></div>
</div>

<div class="filters">
    <div class="filter-group">
        <label>🎯 Category:</label>
        <select id="filterCategory" onchange="applyFilters()">
            <option value="All">All Categories</option>
            {''.join(f'<option value="{c}">{c}</option>' for c in sorted(df['category'].dropna().unique()))}
        </select>
    </div>
    <div class="filter-group">
        <label>👤 Experience:</label>
        <select id="filterExp" onchange="applyFilters()">
            <option value="All">All Levels</option>
            {''.join(f'<option value="{e}">{e}</option>' for e in sorted(df['experience_level'].dropna().unique()))}
        </select>
    </div>
</div>

<div id="chartsContainer"></div>

<div class="table-section">
    <div class="table-container">
        <div style="font-size:1.25em;font-weight:600;color:#302b63;padding-bottom:12px;border-left:4px solid #302b63;padding-left:15px;margin-bottom:10px;">📋 Browse All Jobs</div>
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="🔍 Search by title or skills..." onkeyup="filterTable()">
            <span id="resultCount"></span>
        </div>
        <div style="overflow-x:auto;max-height:600px;overflow-y:auto;">
            <table id="jobsTable">
                <thead><tr><th onclick="sortTable(0)">📌 Title</th><th onclick="sortTable(1)">💰 Salary</th><th>📋 Type</th><th>🛠️ Skills</th></tr></thead>
                <tbody id="tableBody"></tbody>
            </table>
        </div>
        <div class="pagination" id="pagination"></div>
    </div>
</div>

<div class="footer">
    <p>📊 Data from HH.ru, Habr Career & Global Job Market | {datetime.now():%B %d, %Y}</p>
</div>

<script>
const allData = {js_data};
let filteredData = allData.slice();
let currentPage = 1;
const rowsPerPage = 20;

function formatSalary(sal) {{
    if (!sal || sal === "Not specified" || sal === "Negotiable") return "Negotiable";
    var cleaned = sal.replace("Not specifiedMarket avg:", "Not specified | Market avg:");
    var n = parseFloat(sal.replace(/[^0-9.]/g, ""));
    if (n > 100000) return "$" + Math.round(n / 90).toLocaleString();
    if (n > 0) return "$" + Math.round(n).toLocaleString();
    return cleaned;
}}

function createCharts(data) {{
    const container = document.getElementById("chartsContainer");
    container.innerHTML = "";
    if (data.length === 0) {{ container.innerHTML = '<div class="section"><div style="text-align:center;padding:50px;color:#8892b0;">No data matches filters.</div></div>'; return; }}
    const n = data.length;
    document.getElementById("resultCount").textContent = n.toLocaleString() + " jobs";

        // CHART 1: Salary Histogram
    const sRaw = data
        .map(function(d) {{
            var val = parseFloat(d.salary_num);
            if (isNaN(val) || val <= 0) return null;
            if (val < 100) return null;
            return val;
        }})
        .filter(function(val) {{ return val !== null; }});

    if (sRaw.length > 5) {{
        const srt = sRaw.slice().sort((a, b) => a - b);
        const p5 = srt[Math.floor(srt.length * 0.05)];
        const p95 = srt[Math.floor(srt.length * 0.95)];
        
        const sFilt = sRaw.filter(s => s >= p5 && s <= p95);
        
        const avgS = Math.round(sFilt.reduce((a, b) => a + b, 0) / sFilt.length);
        const medS = srt[Math.floor(srt.length / 2)];

        const d1 = document.createElement("div"); 
        d1.className = "section";
        d1.innerHTML = '<div class="section-title">📊 Salary Distribution</div>' +
            '<div class="chart-container"><div id="chart1"></div></div>' +
            '<div class="insight"><strong>💡</strong> <span class="highlight">' + sFilt.length.toLocaleString() + 
            '</span> salaries (5th-95th %ile). <strong>Mean:</strong> $' + avgS.toLocaleString() + 
            ' | <strong>Median:</strong> $' + medS.toLocaleString() + 
            '. Range: <strong>$' + Math.round(p5).toLocaleString() + ' – $' + Math.round(p95).toLocaleString() + '</strong>.</div>';
        
        container.appendChild(d1);

        Plotly.newPlot("chart1", [{{
            x: sFilt,
            type: "histogram",
            nbinsx: 35,
            marker: {{color: "#302b63", line: {{color: "white", width: 1.5}}}},
            hovertemplate: "<b>$%{{x:,.0f}}</b><br>Jobs: %{{y}}<extra></extra>"
        }}], {{
            height: 380,
            margin: {{l: 50, r: 25, t: 15, b: 50}},
            bargap: 0.08,
            xaxis: {{
                title: "Annual Salary ($)", 
                tickformat: "$,.0f",
                rangemode: "tozero"
            }},
            yaxis: {{title: "Number of Jobs"}}
        }}, {{responsive: true, displaylogo: false}});
    }}

    // CHART 2: Categories
    const cats = {{}}; data.forEach(d => {{ const c=d.category||"Other"; cats[c]=(cats[c]||0)+1; }});
    const catS = Object.entries(cats).sort((a,b)=>b[1]-a[1]).slice(0,12);
    const top3 = catS.slice(0,3).reduce((s,x)=>s+x[1],0);
    const d2 = document.createElement("div"); d2.className = "section";
    d2.innerHTML = '<div class="section-title">📈 Top Categories</div><div class="chart-container"><div id="chart2"></div></div><div class="insight"><strong>🔍</strong> <span class="highlight">'+catS[0][0]+'</span> leads: '+catS[0][1].toLocaleString()+' ('+(catS[0][1]/n*100).toFixed(1)+'%). Top 3 = <strong>'+(top3/n*100).toFixed(1)+'%</strong>.</div>';
    container.appendChild(d2);
    Plotly.newPlot("chart2", [{{x:catS.map(d=>d[1]),y:catS.map(d=>d[0]),type:"bar",orientation:"h",marker:{{color:catS.map(d=>d[1]),colorscale:[[0,"#8f94fb"],[1,"#302b63"]],showscale:false}},text:catS.map(d=>d[1].toLocaleString()),textposition:"outside",hovertemplate:"<b>%{{y}}</b><br>%{{x:,}}<extra></extra>"}}], {{height:400,margin:{{l:190,r:80,t:10,b:20}},xaxis:{{showticklabels:false}},yaxis:{{autorange:"reversed"}}}}, {{responsive:true,displaylogo:false}});

    // CHART 3: Experience
    const expO = ["Junior","Middle","Senior","Lead"];
    const expC = ["#8f94fb","#302b63","#ff7f0e","#2ca02c"];
    const expCnt = expO.map(e => data.filter(d => d.experience_level===e).length);
    const d3 = document.createElement("div"); d3.className = "section";
    d3.innerHTML = '<div class="section-title">👥 Experience Levels</div><div class="chart-container"><div id="chart3"></div></div><div class="insight"><strong>📊</strong> <span class="highlight">Middle:</span> '+expCnt[1].toLocaleString()+' ('+(expCnt[1]/n*100).toFixed(1)+'%) | Junior: '+(expCnt[0]/n*100).toFixed(1)+'% | Senior: '+(expCnt[2]/n*100).toFixed(1)+'% | Lead: '+(expCnt[3]/n*100).toFixed(1)+'%.</div>';
    container.appendChild(d3);
    Plotly.newPlot("chart3", [{{x:expO,y:expCnt,type:"bar",marker:{{color:expC}},text:expCnt.map(x=>x.toLocaleString()),textposition:"outside",hovertemplate:"<b>%{{x}}</b><br>%{{y:,}}<extra></extra>"}}], {{height:360,margin:{{l:40,r:40,t:10,b:50}},yaxis:{{showticklabels:false}}}}, {{responsive:true,displaylogo:false}});

    // CHART 4: Salary Box Plot
    const boxD = expO.map((exp,i) => {{ const v = data.filter(d=>d.experience_level===exp&&d.salary_num).map(d=>d.salary_num); return v.length<3?null:{{y:v,type:"box",name:exp,marker:{{color:expC[i]}},boxmean:"sd"}}; }}).filter(Boolean);
    if (boxD.length) {{
        const d4 = document.createElement("div"); d4.className = "section";
        d4.innerHTML = '<div class="section-title">💰 Salary by Experience</div><div class="chart-container"><div id="chart4"></div></div><div class="insight"><strong>📈</strong> Salary grows <strong>2-3x</strong> from Junior to Lead.</div>';
        container.appendChild(d4);
        Plotly.newPlot("chart4",boxD,{{height:380,margin:{{l:80,r:20,t:10,b:40}},yaxis:{{title:"Salary ($)",tickformat:"$,.0f"}},showlegend:false}},{{responsive:true,displaylogo:false}});
    }}

    // CHART 5: Skills
    const allSk = []; data.forEach(d=>{{ if(d.skills_clean)d.skills_clean.split(",").forEach(s=>{{ const sk=s.trim().toLowerCase(); if(sk.length>2&&["not","specified","the","and","nan"].indexOf(sk)===-1)allSk.push(sk); }}); }});
    if (allSk.length>10) {{
        const skCnt = {{}}; allSk.forEach(s=>skCnt[s]=(skCnt[s]||0)+1);
        const skS = Object.entries(skCnt).sort((a,b)=>b[1]-a[1]).slice(0,15);
        const d5 = document.createElement("div"); d5.className = "section";
        d5.innerHTML = '<div class="section-title">🛠️ Top Skills</div><div class="chart-container"><div id="chart5"></div></div><div class="insight"><strong>🔑</strong> <span class="highlight">'+skS[0][0]+'</span> ('+skS[0][1].toLocaleString()+'), <span class="highlight">'+skS[1][0]+'</span> ('+skS[1][1].toLocaleString()+'), <span class="highlight">'+skS[2][0]+'</span> ('+skS[2][1].toLocaleString()+').</div>';
        container.appendChild(d5);
        Plotly.newPlot("chart5", [{{x:skS.map(d=>d[1]),y:skS.map(d=>d[0]),type:"bar",orientation:"h",marker:{{color:skS.map(d=>d[1]),colorscale:[[0,"#ff9a9e"],[1,"#d62728"]],showscale:false}},text:skS.map(d=>d[1].toLocaleString()),textposition:"outside"}}], {{height:400,margin:{{l:150,r:80,t:10,b:20}},xaxis:{{showticklabels:false}},yaxis:{{autorange:"reversed"}}}}, {{responsive:true,displaylogo:false}});
    }}
}}

// TABLE
function renderTable(data,page) {{
    const s=(page-1)*rowsPerPage, e=s+rowsPerPage;
    document.getElementById("tableBody").innerHTML = data.slice(s,e).map(d => '<tr><td><strong>'+(d.title||"")+'</strong></td><td><span class="salary-badge">'+formatSalary(d.salary)+'</span></td><td><span class="type-badge type-'+(d.employment_type||"Full-time")+'">'+(d.employment_type||"Full-time")+'</span></td><td style="max-width:250px;font-size:0.83em;">'+(d.skills_clean||"—")+'</td></tr>').join("");
    const tp=Math.ceil(data.length/rowsPerPage);
    document.getElementById("pagination").innerHTML = '<button onclick="changePage('+(page-1)+')" '+(page===1?"disabled":"")+'>←</button> <span class="page-info">'+page+' / '+tp.toLocaleString()+'</span> <button onclick="changePage('+(page+1)+')" '+(page===tp?"disabled":"")+'>→</button> <span style="color:#8892b0;">('+data.length.toLocaleString()+' jobs)</span>';
}}
function changePage(p) {{ const tp=Math.ceil(filteredData.length/rowsPerPage); if(p<1||p>tp)return; currentPage=p; renderTable(filteredData,p); }}
function sortTable(col) {{ const k=["title","salary_num","employment_type","skills_clean"][col]; filteredData.sort((a,b)=>{{ const va=a[k]||"",vb=b[k]||""; return typeof va==="number"?vb-va:String(va).localeCompare(String(vb)); }}); currentPage=1; renderTable(filteredData,1); }}
function filterTable() {{ const q=document.getElementById("searchInput").value.toLowerCase(); applyFiltersTo(q?allData.filter(d=>(d.title||"").toLowerCase().indexOf(q)!==-1||(d.skills_clean||"").toLowerCase().indexOf(q)!==-1):allData.slice()); }}
function applyFilters() {{ let d=allData.slice(); const cat=document.getElementById("filterCategory").value,exp=document.getElementById("filterExp").value; if(cat!=="All")d=d.filter(x=>x.category===cat); if(exp!=="All")d=d.filter(x=>x.experience_level===exp); applyFiltersTo(d); }}
function applyFiltersTo(data) {{ filteredData=data; currentPage=1; createCharts(filteredData); renderTable(filteredData,1); }}

createCharts(allData); renderTable(allData,1);
</script>

</body>
</html>'''

# ============================================================
# WRITE FILE
# ============================================================
with open("index.html", 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✅ Dashboard saved: index.html")
print(f"   📊 {total:,} job postings")
print(f"   📈 5 interactive charts + searchable table")
print(f"   🎛️ Filters: Category, Experience")
