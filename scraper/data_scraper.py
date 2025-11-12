import time
import csv
import datetime
import os
import re
import sqlite3
import unicodedata
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ----------------------------------------------------------
# CONFIG
# ----------------------------------------------------------
ARTISTS = {
    "Burna Boy": "3wcj11K77LjEY1PkEazffa",
    "Davido": "0Y3agQaa6g2r0YmHPOO9rh",
    "Wizkid": "3tVQdUvClmAT7URs9V3rsp",
    "Rema": "46pWGuE3dSwY3bMMXGBvVS",
    "Ayra Starr": "3ZpEKRjHaHANcpk10u6Ntq",
    "Asake": "3a1tBryiczPAZpgoZN9Rzg",
    "Fireboy DML": "75VKfyoBlkmrJFDqo1o2VY",
    "Tems": "687cZJR45JO7jhk1LHIbgq",
    "Olamide": "4ovtyvs7j1jSmwhkBGHqSr",
    "CKay": "048LktY5zMnakWq7PTtFrz",
    "Mr Eazi": "4TAoP0f9OuWZUesao43xUW",
    "Omah Lay": "5yOvAmpIR7hVxiS6Ls5DPO",
}
PLATFORM = "Spotify"
OUTPUT_FILE = "spotify_kworb_artist_tracks.csv"

# ----------------------------------------------------------
# SELENIUM SETUP
# ----------------------------------------------------------
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

firefox_options = webdriver.FirefoxOptions()

firefox_options.add_argument("-headless")
driver = webdriver.Firefox(options=firefox_options)
# driver = webdriver.Chrome(options=chrome_options)

# ----------------------------------------------------------
# CSV INIT
# ----------------------------------------------------------
if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["artist", "track", "platform", "country", "streams", "month"])


# ----------------------------------------------------------
# DATABASE SETUP
# ----------------------------------------------------------
DB_FILE = "spotify_kworb_artist_tracks.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS artist_tracks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artist TEXT,
    track TEXT,
    platform TEXT,
    country TEXT,
    streams INTEGER,
    month TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(artist, track, country, month)
)
""")


conn.commit()


# ----------------------------------------------------------
# SCRAPE LOGIC
# ----------------------------------------------------------
for artist_name, artist_id in ARTISTS.items():
    print(f"\n🎵 Working on artist: {artist_name}")
    artist_url = f"https://kworb.net/spotify/artist/{artist_id}.html"
    driver.get(artist_url)

    while True:
        try:
            track_table = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            rows = track_table.find_elements(By.TAG_NAME, "tr")[1:]  # skip header
            break
        except Exception as e:
            print(f" Error loading artist page for {artist_name}: {e}")
            time.sleep(3)

    for i in range(len(rows)):
        try:
            # ⚠️ RELOAD THE TABLE EACH TIME to avoid stale references
            track_table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            rows = track_table.find_elements(By.TAG_NAME, "tr")[1:]
            row = rows[i]

            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 2:
                continue
            title_cell = cells[1]
            link = title_cell.find_element(By.TAG_NAME, "a").get_attribute("href")
            track_name = title_cell.text.strip()
            print(f"  🎶 {track_name} -> {link}")

            # Visit track page
            driver.get(link)

            # Click "Streams" tab
            try:
                streams_tab = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "streams"))
                )
                streams_tab.click()
                time.sleep(2)
            except Exception as e:
                print(f"     Couldn't click streams tab for {track_name}: {e}")
                driver.back()
                continue

            # Wait for table to load
            try:
                table = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )
            except:
                print(f"     No streams table found for {track_name}")
                driver.back()
                continue

            headers = [h.text.strip() for h in table.find_elements(By.TAG_NAME, "th")]
            rows_in_table = table.find_elements(By.TAG_NAME, "tr")

            total_row = None
            for tr in rows_in_table:
                cols = [c.text.strip() for c in tr.find_elements(By.TAG_NAME, "td")]
                if cols and cols[0] == "Total":
                    total_row = cols
                    break

            if not total_row:
                print(f"     No total row found for {track_name}")
                driver.back()
                continue

            countries = headers[1:]   # skip "Date"
            totals = total_row[1:]    # skip "Total"
            today = datetime.datetime.now().strftime("%Y-%m-%d")

            # with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
            #     writer = csv.writer(f)
            #     for country, streams in zip(countries, totals):
            #         writer.writerow([
            #             artist_name,
            #             track_name,
            #             PLATFORM,
            #             country,
            #             streams,
            #             today
            #         ])

            def clean_text(text):
                """Clean and normalize text for CSV output."""
                if not text:
                    return ""
                # Remove unwanted symbols (like *, †, etc.)
                text = re.sub(r"[*†‡•º°¤§¶…«»–—]", "", text)
                # Normalize unicode accents
                text = unicodedata.normalize("NFKD", text)
                # Replace multiple spaces or newlines
                text = re.sub(r"\s+", " ", text)
                return text.strip()

            def clean_number(num):
                """Clean numeric fields (streams)."""
                return re.sub(r"[^\d]", "", num) if num else "0"

            # ...

            # with open(OUTPUT_FILE, "a", newline="", encoding="utf-8-sig") as f:
            #     writer = csv.writer(f)
            #     for country, streams in zip(countries, totals):
            #         writer.writerow([
            #             clean_text(artist_name),
            #             clean_text(track_name),
            #             PLATFORM,
            #             clean_text(country),
            #             clean_number(streams),
            #             today                                                                                                                                                                                                                                                                                                                                                                                 
            #         ])

            for country, streams in zip(countries, totals):
                cursor.execute("""
                    INSERT OR REPLACE INTO artist_tracks (artist, track, platform, country, streams, month)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    clean_text(artist_name),
                    clean_text(track_name),
                    PLATFORM,
                    clean_text(country),
                    int(clean_number(streams) or 0),
                    today
                ))                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              

            conn.commit()                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               


            print(f"    Saved totals for {track_name}")                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
            driver.back()

        except Exception as e:
            print(f"    Error processing track #{i}: {e}")
            try:
                driver.get(artist_url)
            except:
                pass
            continue

driver.quit()
conn.close()
print("\n✅ Scraping complete!")