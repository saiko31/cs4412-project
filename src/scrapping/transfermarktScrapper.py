"""
Transfermarkt Injury Scraper
CS 4412 - M2: Initial Implementation
Author: Alexander San Agustin-Melendez

Target: Sub-25 players, Big 5 leagues, 5 seasons (2019-2023)
Output: data/raw/injuries_raw.csv
        data/raw/players_raw.csv

USAGE:
    python transfermarktScrapper.py

    TEST MODE: transfermarktScrapper.py --test

NOTES:
    - Rate limiting: 2-5s between requests (avoid IP ban)
    - Saves progress incrementally (resume-safe)
    - Logs all errors to data/logs/scraper.log



This thing took +10 HOURS to run, so I added a test mode that only scrapes La Liga 2022/23. This allows me to quickly iterate on the parsing logic without waiting for the full run.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import logging
import re
import json
import os
from datetime import datetime, date
from pathlib import Path

# ── Directory setup ──────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_RAW = BASE_DIR / "data" / "transfermarkt" / "raw"
DATA_LOGS = BASE_DIR / "data" / "transfermarkt" / "logs"
DATA_RAW.mkdir(parents=True, exist_ok=True)
DATA_LOGS.mkdir(parents=True, exist_ok=True)



# Sleep parameters (in seconds)
SLEEP_MIN = 4.0
SLEEP_MAX = 8.0

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(DATA_LOGS / "scraper.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ── Headers 
HEADERS_POOL = [
    {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.transfermarkt.com/",
    },
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "en-GB,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.transfermarkt.com/",
    },
]

# ── Scope Definition ──────────────────────────────────────────────────────────
# Transfermarkt league IDs
LEAGUES = {
    "Premier League": {"competition_id": "GB1", "country": "England"},
    "La Liga":        {"competition_id": "ES1", "country": "Spain"},
    "Bundesliga":     {"competition_id": "L1",  "country": "Germany"},
    "Serie A":        {"competition_id": "IT1",  "country": "Italy"},
    "Ligue 1":        {"competition_id": "FR1",  "country": "France"},
}

# Last 5 complete seasons
SEASONS = ["2019", "2020", "2021", "2022", "2023"]  # TM uses start year

BASE_URL = "https://www.transfermarkt.com"

# ── Rate limiter ──────────────────────────────────────────────────────────────
def polite_sleep(min_s: float = 4.0, max_s: float = 8.0):
    delay = random.uniform(min_s, max_s)
    time.sleep(delay)

def get_page(url: str, retries: int = 3) -> BeautifulSoup | None:
    """
    Fetch a page with retry logic and rotating headers.
    Returns BeautifulSoup object or None on failure.
    """
    for attempt in range(retries):
        try:
            headers = random.choice(HEADERS_POOL)
            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                return BeautifulSoup(response.content, "html.parser")
            elif response.status_code == 429:
                wait = 30 * (attempt + 1)
                log.warning(f"Rate limited (429). Waiting {wait}s. URL: {url}")
                time.sleep(wait)
            elif response.status_code == 403:
                log.error(f"Forbidden (403). URL: {url}")
                return None
            else:
                log.warning(f"HTTP {response.status_code} on attempt {attempt+1}. URL: {url}")

        except requests.exceptions.RequestException as e:
            log.error(f"Request error on attempt {attempt+1}: {e}")
            time.sleep(5 * (attempt + 1))

    log.error(f"Failed after {retries} retries: {url}")
    return None

# ── Player Discovery ──────────────────────────────────────────────────────────
def get_players_from_league(competition_id: str, season: str) -> list[dict]:
    """
    Scrape player list from a league season page.
    Filters for players under 25 at time of season.
    
    Returns list of dicts: {player_id, player_name, dob, position, club, league, season}
    """
    url = (f"{BASE_URL}/wettbewerb/startseite/wettbewerb/{competition_id}"
           f"/plus/?saison_id={season}")
    
    log.info(f"Fetching league page: {url}")
    soup = get_page(url)
    if not soup:
        return []
    
    # DEBUG: see raw HTML table
    table = soup.find("table", {"class": "items"})
    if not table:
        log.warning(f"No items table found for {competition_id} {season}")
        return []
    
    #DEBUG : see firt raw table row
    rows = table.find_all("tr", {"class": ["odd", "even"]})
    log.info(f"Rows found: {len(rows)}")

    """ if rows:
        print("FIRST HTML ROW")
        print(rows[0].prettify()) """

    players = []
    
    # Find all clubs in the league

    club_links = []
    for row in rows:
        club_link = row.find("a", href=lambda h: h and "/startseite/verein/" in h)
        if club_link:
            club_href = club_link.get("href")
            club_name = club_link.get("title", "Unknown Club")
            # Convert club page to squad page
            
            squad_url = club_href.replace("/startseite/", "/kader/") + f"/saison_id/{season}/plus/1"
            club_links.append({
                "club_name": club_name,
                "squad_url": BASE_URL + squad_url if not squad_url.startswith("http") else squad_url
            })

    log.info(f"Found {len(club_links)} clubs in {competition_id} {season}")

    # Scrape each club's squad
    for club_info in club_links:
        #DEBUG : Print squad url to see if correct
        log.info("Getting players from: " + club_info["squad_url"] + " for club: " + club_info["club_name"])
        polite_sleep(SLEEP_MIN, SLEEP_MAX)
        club_players = get_squad_players(
            club_info["squad_url"],
            club_info["club_name"],
            competition_id,
            season
        )
        players.extend(club_players)
        log.info(f"  {club_info['club_name']}: {len(club_players)} players found")

    return players

def get_squad_players(squad_url: str, club: str, league: str, season: str) -> list[dict]:
    """
    Scrape individual squad page and extract player metadata.
    Filters: age <= 25 at start of season (Aug 1 of season year).
    """
    soup = get_page(squad_url)
    if not soup:
        #DEBUG
        print("Error getting url")
        return []

    players = []
    season_start = date(int(season), 8, 1)  # Season starts ~Aug 1

    # DEBUG: see raw HTML table
    table = soup.find("table", {"class": "items"})
    if not table:
        print("NO TABLE FOUND")
        print(soup.prettify()[:3000])
        return []  
    
    #DEBUG : see firt raw table row
    rows = table.find_all("tr", {"class": ["odd", "even"]})
    print(f"Rows found: {len(rows)}")

    """ if rows:
        print("FIRST HTML ROW")
        print(rows[0].prettify()) """

    if not table:
        log.debug(f"No squad table found at {squad_url}")
        return []
    log.debug(f"Parsing squad table with {len(rows)} rows at {squad_url}")

    for row in rows:
        try:
            # Player name and ID
            """ name_cell = row.find("td", {"class": "hauptlink"})
            if not name_cell:
                continue
            player_link = name_cell.find("a")
            if not player_link:
                continue

            player_name = player_link.get_text(strip=True)
            href = player_link.get("href", "")
            # Extract player ID from URL: /player-name/profil/spieler/12345
            parts = href.split("/")
            player_id = parts[-1] if parts[-1].isdigit() else None
            #DEBUG
            print("player id:" + player_id)
            if not player_id:
                continue """
            



            """ NOTE: This is made even more confusing by the fact that the links are in German. """


            

            player_link = row.find("a", href=lambda h: h and "/profil/spieler/" in h)
            if not player_link:
                continue
            log.debug(f"Found player link: {player_link}")
            player_name = player_link.get_text(strip=True)
            player_id = player_link["href"].split("/profil/spieler/")[1].split("/")[0]

            print(player_name + " - " + player_link["href"] + " - ID: " + player_id)

            # determine birthdate and compute age as of season start

            zentriert_cells = [td for td in row.find_all("td") 
                   if "zentriert" in (td.get("class") or [])]

            #DEBUG: print zentriert cells to see if we can find the DOB
            print(f"Total cells zentriert: {len(zentriert_cells)}")
            for i, cell in enumerate(zentriert_cells):
                print(f"[{i}]: {cell.get_text(strip=True)}")

            dob = None
            age_at_season = None
    
            if len(zentriert_cells) >= 2:
                dob_text = zentriert_cells[1].get_text(strip=True)
                match_dob = re.match(r"(\d{2}/\d{2}/\d{4})", dob_text)
                if match_dob:
                    dob = parse_dob(match_dob.group(1))
                    age_at_season = (season_start - dob).days // 365 if dob else log.debug(f"Could not parse DOB for {player_name}: {dob_text}")

            # Filter: under 25 at season start
            if age_at_season is None or age_at_season >= 25:
                continue

            # Position
            position = None
            pos_cell = row.find("td", {"class": lambda c: c and "zentriert" in c and "rueckennummer" in c})
            if pos_cell:
                # "Goalkeeper", "Centre-Back", etc.
                position = pos_cell.get("title")

            players.append({
                "player_id_tm": player_id,
                "player_name_raw": player_name,
                "dob": dob.isoformat() if dob else None,
                "age_at_season_start": age_at_season,
                "position": position,
                "club": club,
                "league_id": league,
                "season": season,
            })

        except Exception as e:
            log.debug(f"[ERROR] Row parse error: {e}")
            continue

    return players


def parse_dob(text: str):
    formats = [
        "%b %d, %Y",   # Jan 15, 2000
        "%d.%m.%Y",    # 15.01.2000
        "%d/%m/%Y",    # 15/01/2000  
        "%m/%d/%Y",    # 01/15/2000 
        "%Y-%m-%d",    # 2000-01-15  
    ]
    for fmt in formats:
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            continue
    return None


# ── Injury Scraper ────────────────────────────────────────────────────────────
def get_player_injuries(player_id: str, player_name: str) -> list[dict]:
    """
    Scrape full injury history for a specific player.
    URL pattern: /player-name/verletzungen/spieler/{player_id}
    
    Returns list of injury records.
    """
    # TM injury page uses the player's slug — we approximate it
    url = f"{BASE_URL}/player/verletzungen/spieler/{player_id}"
    
    soup = get_page(url)
    if not soup:
        return []

    injuries = []
    table = soup.find("table", {"class": "items"})
    if not table:
        log.debug(f"No injury table for player {player_id} ({player_name})")
        return []

    rows = table.find_all("tr", {"class": ["odd", "even"]})
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 5:
            continue

        try:
            season_cell    = cells[0].get_text(strip=True)  # e.g. "23/24"
            injury_cell    = cells[1].get_text(strip=True)  # e.g. "Muscle injury"
            from_cell      = cells[2].get_text(strip=True)  # e.g. "Jan 15, 2024"
            until_cell     = cells[3].get_text(strip=True)  # e.g. "Feb 10, 2024"
            absence_cell   = cells[4].get_text(strip=True)  # e.g. "26 days"
            
            # Parse absence days
            days_absent = None
            if "day" in absence_cell.lower():
                try:
                    days_absent = int(absence_cell.lower().replace("days", "")
                                                           .replace("day", "")
                                                           .strip())
                except ValueError:
                    pass

            # Parse dates
            injury_date = None
            return_date = None
            for fmt in ["%b %d, %Y", "%d.%m.%Y", "%m/%d/%Y"]:
                try:
                    injury_date = datetime.strptime(from_cell, fmt).date().isoformat()
                    break
                except ValueError:
                    continue
            for fmt in ["%b %d, %Y", "%d.%m.%Y", "%m/%d/%Y"]:
                try:
                    return_date = datetime.strptime(until_cell, fmt).date().isoformat()
                    break
                except ValueError:
                    continue

            injuries.append({
                "player_id_tm": player_id,
                "player_name_raw": player_name,
                "season_tm": season_cell,
                "injury_type_raw": injury_cell,
                "injury_date": injury_date,
                "return_date": return_date,
                "days_absent_raw": absence_cell,
                "days_absent": days_absent,
                "scraped_at": datetime.now().isoformat(),
            })

        except Exception as e:
            log.debug(f"Injury row parse error for {player_id}: {e}")
            continue

    return injuries


# ── Progress Tracking ─────────────────────────────────────────────────────────
def load_progress(filepath: Path) -> set:
    """Load set of already-processed player IDs to allow resume."""
    if filepath.exists():
        df = pd.read_csv(filepath)
        return set(df["player_id_tm"].astype(str).unique())
    return set()


# ── Main Pipeline ─────────────────────────────────────────────────────────────
def run_scraper(
    test_mode: bool = False,
    max_clubs_per_league: int = None
):
    """
    Full scraping pipeline:
    1. Discover sub-25 players across leagues/seasons
    2. Scrape injury history for each unique player
    3. Save incrementally
    
    Args:
        test_mode: If True, scrapes only La Liga 2022/23, 2 clubs max
        max_clubs_per_league: Limit clubs per league (for testing)
    """
    
    # ── PHASE 1: Player Discovery ─────────────────────────────────────────
    players_file = DATA_RAW / "players_raw.csv"
    
    if players_file.exists():
        log.info(f"Loading existing players file: {players_file}")
        players_df = pd.read_csv(players_file)
    else:
        log.info("Starting player discovery phase...")
        all_players = []
        
        leagues_to_scrape = {"La Liga": LEAGUES["La Liga"]} if test_mode else LEAGUES
        seasons_to_scrape = ["2022"] if test_mode else SEASONS

        for league_name, league_info in leagues_to_scrape.items():
            for season in seasons_to_scrape:
                log.info(f"── Scraping {league_name} {season}/{int(season)+1} ──")
                polite_sleep(SLEEP_MIN, SLEEP_MAX)
                
                players = get_players_from_league(
                    league_info["competition_id"], 
                    season
                )
                
                for p in players:
                    p["league_name"] = league_name
                
                all_players.extend(players)
                log.info(f"  Total players so far: {len(all_players)}")

        players_df = pd.DataFrame(all_players)
        players_df.drop_duplicates(subset=["player_id_tm", "season"], inplace=True)
        players_df.to_csv(players_file, index=False)
        log.info(f"Players saved: {len(players_df)} rows → {players_file}")

    # Summary
    unique_players = players_df["player_id_tm"].nunique()
    log.info(f"Unique sub-25 players discovered: {unique_players}")
    print(f"\n{'='*50}")
    print(f"PHASE 1 COMPLETE")
    print(f"Total records: {len(players_df)}")
    print(f"Unique players: {unique_players}")
    print(f"Leagues: {players_df['league_name'].value_counts().to_dict()}")
    print(f"{'='*50}\n")

    # ── PHASE 2: Injury Scraping ──────────────────────────────────────────
    injuries_file = DATA_RAW / "injuries_raw.csv"
    processed_ids = load_progress(injuries_file)
    
    unique_player_ids = players_df["player_id_tm"].astype(str).unique()
    remaining = [pid for pid in unique_player_ids if pid not in processed_ids]
    
    log.info(f"Injuries to scrape: {len(remaining)} players "
             f"({len(processed_ids)} already done)")

    all_injuries = []
    
    for i, player_id in enumerate(remaining):
        player_row = players_df[
            players_df["player_id_tm"].astype(str) == player_id
        ].iloc[0]
        player_name = player_row["player_name_raw"]
        
        polite_sleep(SLEEP_MIN, SLEEP_MAX)
        injuries = get_player_injuries(player_id, player_name)
        
        if injuries:
            all_injuries.extend(injuries)
            log.info(f"[{i+1}/{len(remaining)}] {player_name}: "
                     f"{len(injuries)} injuries")
        else:
            log.info(f"[{i+1}/{len(remaining)}] {player_name}: no injuries")

        # Incremental save every 50 players
        if (i + 1) % 50 == 0:
            if all_injuries:
                temp_df = pd.DataFrame(all_injuries)
                if injuries_file.exists():
                    temp_df.to_csv(injuries_file, mode="a", 
                                   header=False, index=False)
                else:
                    temp_df.to_csv(injuries_file, index=False)
                log.info(f"Checkpoint saved: {len(all_injuries)} new injuries")
                all_injuries = []

    # Final save
    if all_injuries:
        temp_df = pd.DataFrame(all_injuries)
        if injuries_file.exists():
            temp_df.to_csv(injuries_file, mode="a", header=False, index=False)
        else:
            temp_df.to_csv(injuries_file, index=False)

    # Final report
    if injuries_file.exists():
        final_df = pd.read_csv(injuries_file)
        print(f"\n{'='*50}")
        print(f"PHASE 2 COMPLETE")
        print(f"Total injury records: {len(final_df)}")
        print(f"Players with injuries: {final_df['player_id_tm'].nunique()}")
        print(f"Injury types found: {final_df['injury_type_raw'].nunique()}")
        print(f"{'='*50}\n")
        print(final_df["injury_type_raw"].value_counts().head(15))


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Transfermarkt Injury Scraper")
    parser.add_argument(
        "--test", 
        action="store_true",
        help="Test mode: La Liga 2022/23 only, minimal requests"
    )
    args = parser.parse_args()
    
    if args.test:
        log.info("Running in TEST MODE")
    
    run_scraper(test_mode=args.test)