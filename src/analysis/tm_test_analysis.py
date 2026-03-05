"""
This code is to check if the data collected from transfermarktScrapper.py 
in its TEST MODE collects the right data, before performing the actual scrapping
"""

"""
At the end, I also used it to verify the integrity of the collected data, checking for nulls, unique values, 
and sample rows to ensure the data looks correct and is ready for preprocessing and analysis. 
"""

import pandas as pd

players = pd.read_csv('data/transfermarkt/raw/players_raw.csv')
injuries = pd.read_csv('data/transfermarkt/raw/injuries_raw.csv')


# PLAYERS
print("=== PLAYERS ===")
print(f"Total rows: {len(players)}")
print(f"Unique player IDs: {players['player_id_tm'].nunique()}")
print(f"\nNulls per column:\n{players.isnull().sum()}")
print(f"\n Found ages:\n{players['age_at_season_start'].value_counts().sort_index()}")
print(f"\nSample:\n{players[['player_name_raw','dob','age_at_season_start','position','club']].head(10)}")

# INJURIES
print("\n=== INJURIES ===")
print(f"Total rows: {len(injuries)}")
print(f"Unique players con lesiones: {injuries['player_id_tm'].nunique()}")
print(f"\nNulls per column:\n{injuries.isnull().sum()}")
print(f"\nInjury types (top 10):\n{injuries['injury_type_raw'].value_counts().head(10)}")
print(f"\nSample:\n{injuries.head(10)}")