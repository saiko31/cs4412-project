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

    # Ligamentous
    "cruciate": "Ligamentous_Severe",
    "acl": "Ligamentous_Severe",
    "knee ligament": "Ligamentous_Severe",
    "meniscus": "Ligamentous_Severe",

    "ankle sprain": "Ligamentous_Mild",
    "ankle injury": "Ligamentous_Mild",
    "ankle problems": "Ligamentous_Mild",
    "injury to the ankle": "Ligamentous_Mild",
    "knee injury": "Ligamentous_Mild",
    "knee problems": "Ligamentous_Mild",
    "shoulder injury": "Ligamentous_Mild",
    "foot injury": "Ligamentous_Mild",
    "ligament": "Ligamentous_Mild",

    # Bone
    "fracture": "Bone",
    "broken": "Bone",
    "stress fracture": "Bone",
    "bone injury": "Bone",

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

    # Other — explicito
    "knock": "Other",
    "fitness": "Other",
    "minor knock": "Other",
    "unknown": "Other",
}


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