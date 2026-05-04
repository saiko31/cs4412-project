# Injury Pattern Discovery in U-25 Professional Footballers
## Author
**Alexander San Agustin Melendez** | CS 4412 — Data Mining | Kennesaw State University

---

## Overview
This project applies Knowledge Discovery in Databases (KDD) methodology to uncover
hidden patterns in injury records of professional footballers under 25 years old
across the Big 5 European leagues (2019/20–2023/24). Using clustering and association
rule mining, the study characterizes injury risk profiles and identifies non-obvious
relationships between player attributes and injury outcomes.

### Leagues Covered
- La Liga (Spain)
- Premier League (England)
- Serie A (Italy)
- Ligue 1 (France)
- Bundesliga (Germany)

### Discovery Questions
1. Which combination of factors represents a significant elevation in injury occurrence
   among U-25 players?
2. Are there natural risk profiles that segment U-25 players by injury pattern?

---

## Data Source

**Transfermarkt (web scraping):** Player demographics and historical injury records.

> **Note:** The original proposal planned to integrate StatsBomb Open Data for
> event-level workload metrics. During M2, it was determined that StatsBomb's
> event data requires authentication and is not publicly available for the Big 5
> leagues at the required coverage. FBref was evaluated as an alternative but
> returned HTTP 403 errors for automated access. The dataset was restructured to
> rely exclusively on Transfermarkt. Player position is used as a proxy for
> physical workload.

---

## Dataset

| Parameter | Value |
|---|---|
| Source | Transfermarkt (web scraping) |
| Scope | Big 5 leagues, seasons 2019/20 — 2023/24 |
| Unique U-25 players | 3,273 |
| Raw injury records | 22,612 |
| Final dataset (M3 pipeline) | 4,401 records |
| Age range at injury | 15 — 24 |
| Injury categories (normalized) | 8 (from 299 raw types) |

> **Raw data files are excluded from the repository (.gitignore).**
> Run the scraper to regenerate them (see How to Run).

---

## Key Findings

**Severity asymmetry:**
Ligamentous_Severe injuries (ACL, cruciate) represent 4.8% of records but produce
a median absence of 204 days — 10× higher than Muscular injuries (22 days).

**Developmental risk windows (Apriori, Lift > 1.2):**
- Goalkeepers → categorically distinct injuries (Lift: 2.286)
- Players under 18 → elevated bone injury risk (Lift: 1.415)
- Attackers aged 19–21 → elevated ACL/cruciate risk (Lift: 1.401)
- Midfielders aged 19–21 → elevated bone stress risk (Lift: 1.331)

**Cluster isolation (K-Means, k=4):**
One clinically distinct cluster of 197 players defined by Ligamentous_Severe
injuries with median absence of 208 days was isolated from 4,401 records.

---

## Tech Stack

- **Language:** Python 3.10
- **Environment:** Miniforge (conda) on Fedora Linux
- **Libraries:** Pandas, NumPy, Scikit-learn, Matplotlib, Seaborn,
  BeautifulSoup, Requests, TheFuzz, mlxtend
- **Tools:** Jupyter Notebook, VS Code

---

## Repository Structure

```text
├── data/
│   └── transfermarkt/
│       └── raw/
│           ├── players_raw.csv       # 3,273 unique U-25 players
│           └── injuries_raw.csv      # 22,612 raw injury records
├── notebooks/
│   ├── M2 - Alexander San Agustin.ipynb   # EDA + K-Means
│   └── M3 - Alexander San Agustin.ipynb   # Apriori + Decision Tree
├── src/
│   ├── scrapping/
│   │   ├── transfermarktScrapper.py
│   │   └── tm_debug.py
│   ├── preprocesing/
│   │   └── tm_preprocessing.py      # INJURY_TYPE_MAP + normalize_injury_type()
│   └── analysis/
│       └── tm_test_analysis.py
├── outputs/                          # Generated visualizations
├── docs/
│   ├── CS_4412_M1__Project_Proposal___Alexander_San_Agustin_Melendez.pdf
│   ├── M2_Summary.pdf
│   ├── M3_Summary___Alexander_San_Agustin_Melendez.pdf
│   └── M4_Final_Report_Alexander_San_Agustin.pdf
└── README.md
```

---

## How to Run

### 1. Setup environment
```bash
conda env create -f enviroment.yml
conda activate cs4412_dm
```

### 2. Run the scraper
```bash
# Test mode — La Liga, 1 season (~30 min)
python src/scrapping/transfermarktScrapper.py --test

# Full run — Big 5 leagues, 5 seasons (~10-12 hours)
python src/scrapping/transfermarktScrapper.py
```

### 3. Run the notebooks
```bash
# M2: EDA + K-Means clustering
jupyter notebook notebooks/M2\ -\ Alexander\ San\ Agustin.ipynb

# M3: Apriori + Decision Tree
jupyter notebook notebooks/M3\ -\ Alexander\ San\ Agustin.ipynb
```

Run all cells in order: **Kernel > Restart & Run All**

---

## Milestones

| Milestone | Key Deliverable | Status |
|---|---|---|
| M1: Proposal | Discovery questions, toolstack, data source identification | ✅ Complete |
| M2: EDA + Initial Mining | K-Means clustering, preprocessing pipeline | ✅ Complete |
| M3: Complete Implementation | Apriori association rules, Decision Tree validation | ✅ Complete |
| M4: Final Report | Critical assessment, portfolio-ready documentation | ✅ Complete |
