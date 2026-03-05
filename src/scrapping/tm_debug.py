# DEBUG: pega esto en un archivo debug_tm.py y ejecútalo
import requests
from bs4 import BeautifulSoup
import random

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.transfermarkt.com/",
}

url = "https://www.transfermarkt.com/wettbewerb/startseite/wettbewerb/ES1/plus/?saison_id=2022"

response = requests.get(url, headers=HEADERS, timeout=15)

print(f"Status code: {response.status_code}")
print(f"Content length: {len(response.content)}")
print(f"URL final (after redirects): {response.url}")

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    # Ver todas las tablas disponibles
    tables = soup.find_all("table")
    print(f"\nTablas encontradas: {len(tables)}")
    for i, t in enumerate(tables):
        print(f"  Tabla {i}: class={t.get('class')}, rows={len(t.find_all('tr'))}")
    
    # Primeras 2000 chars del HTML
    print("\n── HTML SNIPPET ──")
    print(soup.prettify()[:2000])
else:
    print(f"\nRespuesta completa:\n{response.text[:1000]}")