# src/preprocessing.py

INJURY_TYPE_MAP = {
    # Muscular
    "muscle injury": "Muscular",
    "muscular injury": "Muscular",
    "muscular problems": "Muscular",
    "muscle fatigue": "Muscular",
    "torn muscle fiber": "Muscular",
    "muscle strain": "Muscular",
    "thigh problems": "Muscular",
    "thigh injury": "Muscular",
    "calf injury": "Muscular",
    "calf problems": "Muscular",
    "calf strain": "Muscular",
    "hamstring": "Muscular",
    "adductor": "Muscular",
    "groin": "Muscular",
    "dead leg": "Muscular",
    "pulled muscle": "Muscular",
    "back problems": "Muscular",
    "back injury": "Muscular",
    "torn muscle bundle": "Muscular",
    "strain": "Muscular",
    "lumbago": "Muscular",
    "hip problems": "Muscular",
    "hip injury": "Muscular",
    "pubalgia": "Muscular",

    # Ligamentous
    "cruciate": "Ligamentous_Severe",
    "acl": "Ligamentous_Severe",
    "knee ligament": "Ligamentous_Severe",
    "meniscus": "Ligamentous_Severe",


    # Ligamentous_Mild
    "sprain": "Ligamentous_Mild",
    "leg injury": "Ligamentous_Mild",
    "foot bruise": "Ligamentous_Mild",
    "ankle sprain": "Ligamentous_Mild",
    "ankle injury": "Ligamentous_Mild",
    "ankle problems": "Ligamentous_Mild",
    "injury to the ankle": "Ligamentous_Mild",
    "knee injury": "Ligamentous_Mild",
    "knee problems": "Ligamentous_Mild",
    "shoulder injury": "Ligamentous_Mild",
    "foot injury": "Ligamentous_Mild",
    "ligament": "Ligamentous_Mild",

    # Trauma 
    "bruise": "Trauma",
    "head injury": "Trauma",
    "concussion": "Trauma",

    # Bone
    "fracture": "Bone",
    "broken": "Bone",
    "stress fracture": "Bone",
    "bone injury": "Bone",
    "knee surgery": "Bone",
    "surgery": "Bone",
    "shin injury": "Bone",
    "toe injury": "Bone",

    # Tendon
    "tendon": "Tendon",
    "achilles": "Tendon",
    "patellar": "Tendon",

    # Illness
    "illness": "Illness",
    "ill": "Illness",
    "covid": "Illness",
    "corona": "Illness",
    "virus": "Illness",
    "infection": "Illness",
    "flu": "Illness",
    "quarantine": "Illness",
    "fever": "Illness",
    "cold": "Illness",
    "inflammation": "Illness",

    # Other — explicito
    "knock": "Other",
    "fitness": "Other",
    "minor knock": "Other",
    "unknown": "Other",
}


import pandas as pd
import numpy as np


def normalize_injury_type(raw: str) -> str:
    """
    Normalize injury_type_raw to canonical category.
    Search for partial match (substring) to cover variants.
    Return ‘Other’ if no match is found.
    """
    if not raw or not isinstance(raw, str):
        return "Other"
    
    raw_lower = raw.lower().strip()
    
    # Búsqueda por substring - cubre variantes parciales
    for key, category in INJURY_TYPE_MAP.items():
        if key in raw_lower:
            return category
    
    return "Other"


def get_clean_df (players_csv_path, injuries_csv_path):

    
    df_players = pd.read_csv(players_csv_path, parse_dates=['dob'])
    df_injuries = pd.read_csv(injuries_csv_path, parse_dates=['injury_date'])

    df_players = df_players.drop_duplicates(subset=['player_id_tm'], keep='first')
    df_injuries = df_injuries.drop_duplicates()

    df_raw = pd.merge(df_injuries, df_players, how='left', on='player_id_tm')

    df_scope = df_raw.copy()
    df_scope['age_at_injury'] = np.floor((df_scope['injury_date'] - df_scope['dob']).dt.days / 365.25).astype('Int64')
    df_scope = df_scope[df_scope['age_at_injury'].between(14, 24)]

    df_scope = df_scope[df_scope['injury_date'] >= '2019-08-01']


    df_preclean = df_scope.copy()
    df_preclean['injury_type'] = df_preclean['injury_type_raw'].apply(normalize_injury_type)

    IRREDUCIBLE = ['unknown injury', 'fitness', 'knock', 'minor knock', 'rest']
    df_clean = df_preclean[~df_preclean['injury_type_raw'].str.lower().isin(IRREDUCIBLE)].copy()

    df_clean['days_absent'] = df_clean.groupby('injury_type')['days_absent'].transform(
        lambda x: x.fillna(x.median())
    )

    print(f"Pre-clean records: {len(df_preclean)}")
    print(f"Cleaned records: {len(df_clean)}")
    assert len(df_clean) == 4401, f"Pipeline failure: Expected 4401 records, but got {len(df_clean)}."
    assert df_clean['days_absent'].isna().sum() == 0, "Pipeline failure: Nulls remain in days_absent."

    return df_clean
