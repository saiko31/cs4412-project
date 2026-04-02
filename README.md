# Injury Pattern Discovery in U-25 Professional Footballers

## Author
**Alexander San Agustin Melendez**

## Overview
This project seeks to apply data mining techniques to discover hidden patterns in injury records of professional soccer players under 25 years old across the Big 5 European Leagues:

- La Liga (Spain)
- Premier League (England)
- Serie A (Italy)
- Ligue 1 (France)
- Bundesliga (Germany)

 The data was taken from the 2019/20 to 2023/24 seasons.

 Using clustering and association rules, the study seeks to characterize injury risk profiles and indentify non-obvious relatinships between plater attributes and injury outcomes.

 ### Discovery Questions
1. Which combination of factors represents a significant elevation in injury occurrence among U-25 players?
2. Are there natural risk profiles that segment U-25 players by injury pattern?

##  Data Sources
* **Transfermarkt (Scraped):** Used for player demographics, market value context, and historical injury records. 

**NOTE:** The original proposal planned to integrate **StatsBomb Open Data** for workload metrics. During M2, it was 
determined that StatsBomb's event-level data requires authentication and is not publicly available for the Big 5 leagues at the required coverage.

The dataset was restructured to rely exclusively on Transfermarkt for injury history, player demographics, and positional data. Workload metrics remain a planned extension for M3 via an alternative data source.

## Dataset (M2)
| Parameter | Value |
|---|---|
| Source | Transfermarkt (web scraping) |
| Scope | Big 5 leagues, seasons 2019/20 — 2023/24 |
| Players scraped | 3,273 unique U-25 players |
| Raw injury records | 22,612 |
| Final dataset (post-preprocessing) | 4,917 records |
| Age range | 15 — 24 at time of injury |
| Injury categories | 7 (normalized from 299 raw types) |

---


## Tech Stack
* **Language:** Python
* **Libraries:** Pandas, NumPy, Scikit-learn, BeautifulSoup/Scrapy (for Transfermarkt)
* **Documentation:** LaTeX (for technical reporting)

---


## Repository Structure
```text
├── data/
│   └── transfermarkt/
│       └── raw/
│           ├── players_raw.csv      # 3,273 unique U-25 players
│           └── injuries_raw.csv     # 22,612 raw injury records
├── notebooks/
│   └── M2 - Alexander San Agustin.ipynb     # Main analysis notebook
├── src/
|   ├── analysis/
|   |   └── tm_test_analysis.pys
│   ├── scrapping/
│   │   └── transfermarktScrapper.py
    |   └── tm_debug.py
│   └── preprocesing/
│       └── tm_preprocessing.py     # INJURY_TYPE_MAP + normalize_injury_type()
├── docs/
|   └── CS_4412_M1__Project_Proposal___Alexander_San_Agustin_Melendez.pdf
│   └── M2_Summary.pdf              # 1-2 page summary
└── README.md
```


## How to Run

### 1. Setup environment
```bash
conda activate cs4412_dm
pip install pandas numpy scikit-learn matplotlib seaborn beautifulsoup4 requests thefuzz
```

### 2. Run the scraper
```bash
# Test mode (La Liga, 1 season)
python src/scrapping/transfermarktScrapper.py --test

# Full run (~10-12 hours)
python src/scrapping/transfermarktScrapper.py
```

### 3. Run the notebook
```bash
jupyter notebook notebooks/M2_EDA_Clustering.ipynb
```

---

## M2 Results Summary
- **4,917 injury records** after preprocessing (scope: 2019-2024, age < 25)
- **4 clusters** identified via K-Means (silhouette = 0.25 at k=4)
- **Key finding:** Ligamentous_Severe injuries (4% of records) produce 
  median absence of 204 days — 10x higher than Muscular injuries (22 days)
- **Cluster 1** isolates 191 ACL/cruciate cases as a distinct high-severity profile

---

## Milestones
| Milestone | Status |
|---|---|
| M1: Proposal | Complete |
| M2: EDA + Initial Mining | Complete |
| M3: Association Rules + Extended Mining | Planned |
| M4: Final Report | Planned |