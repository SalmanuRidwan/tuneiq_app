"""
Web Scraper Module for TuneIQ Insight
Fetches real-time streaming or music-trend data from multiple online sources.
Serves as a fallback or enrichment data source when live API data isn't available.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import logging
from typing import Optional, List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# User agent to avoid blocking
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


def scrape_music_trends(artist_name: str = "Burna Boy", max_results: int = 10) -> pd.DataFrame:
    """
    Scrape web data for streaming trends or news mentions for the specified artist.
    
    Args:
        artist_name: Name of the artist to search for
        max_results: Maximum number of results to return
    
    Returns:
        pd.DataFrame with columns: artist, title, url, source, date_fetched
        Empty DataFrame if scraping fails or no results found
    """
    logger.info(f"Starting web scrape for artist: {artist_name}")
    
    results = []
    
    # Source 1: Google Search (news/mentions)
    try:
        results.extend(_scrape_google_news(artist_name, max_results))
        logger.info(f"Google search: found {len(results)} results")
    except Exception as e:
        logger.warning(f"Google news scrape failed: {e}")
    
    # Source 2: Genius Lyrics (song/artist info) - more reliable
    try:
        genius_data = _scrape_genius_artist(artist_name, max_results)
        results.extend(genius_data)
        logger.info(f"Genius: found {len(genius_data)} results")
    except Exception as e:
        logger.warning(f"Genius scrape failed: {e}")
    
    # Source 3: AllMusic (artist info and discography)
    try:
        allmusic_data = _scrape_allmusic_artist(artist_name, max_results)
        results.extend(allmusic_data)
        logger.info(f"AllMusic: found {len(allmusic_data)} results")
    except Exception as e:
        logger.warning(f"AllMusic scrape failed: {e}")
    
    if not results:
        logger.warning(f"No results found for {artist_name}")
        return pd.DataFrame()
    
    df = pd.DataFrame(results)
    logger.info(f"Web scrape completed. Total results: {len(df)}")
    
    return df


def _scrape_google_news(artist_name: str, max_results: int = 5) -> List[Dict]:
    """Scrape Google search results for artist news/mentions."""
    # Using kworb.net as a fallback for streaming stats (Google search is often blocked)
    base_url = f"https://kworb.net/spotify/search?q={artist_name}"
    headers = {"User-Agent": USER_AGENT}
    
    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        results = []
        count = 0
        for result in soup.select("div.g"):
            if count >= max_results:
                break
            
            title_elem = result.find("h3")
            link_elem = result.find("a")
            snippet = result.find("span", class_="st")
            
            if title_elem and link_elem:
                results.append({
                    "artist": artist_name,
                    "title": title_elem.text.strip() if title_elem else "N/A",
                    "url": link_elem.get("href", "N/A"),
                    "source": "Google News",
                    "snippet": snippet.text.strip() if snippet else "N/A",
                    "date_fetched": datetime.datetime.now().isoformat()
                })
                count += 1
        
        return results
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Google scrape request failed: {e}")
        return []
    except Exception as e:
        logger.error(f"Google scrape parsing failed: {e}")
        return []


def _scrape_genius_artist(artist_name: str, max_results: int = 5) -> List[Dict]:
    """Scrape Genius Lyrics for artist songs and information."""
    base_url = f"https://genius.com/search?q={artist_name}"
    headers = {"User-Agent": USER_AGENT}
    
    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        results = []
        count = 0
        
        # Find song/artist results
        for item in soup.find_all("div", class_="mini_card"):
            if count >= max_results:
                break
            
            title_elem = item.find("a")
            if title_elem:
                results.append({
                    "artist": artist_name,
                    "title": title_elem.text.strip(),
                    "url": f"https://genius.com{title_elem.get('href', '')}",
                    "source": "Genius Lyrics",
                    "snippet": "Song from Genius Lyrics database",
                    "date_fetched": datetime.datetime.now().isoformat()
                })
                count += 1
        
        return results
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Genius scrape request failed: {e}")
        return []
    except Exception as e:
        logger.error(f"Genius scrape parsing failed: {e}")
        return []


def _scrape_allmusic_artist(artist_name: str, max_results: int = 5) -> List[Dict]:
    """Scrape AllMusic for artist information and discography."""
    search_url = f"https://www.allmusic.com/search/all?query={artist_name}"
    headers = {"User-Agent": USER_AGENT}
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        results = []
        count = 0
        
        # Find artist results
        for item in soup.find_all("div", class_="artist"):
            if count >= max_results:
                break
            
            title_elem = item.find("a")
            if title_elem:
                results.append({
                    "artist": artist_name,
                    "title": title_elem.text.strip(),
                    "url": f"https://www.allmusic.com{title_elem.get('href', '')}",
                    "source": "AllMusic",
                    "snippet": "Artist information from AllMusic",
                    "date_fetched": datetime.datetime.now().isoformat()
                })
                count += 1
        
        return results
    
    except requests.exceptions.RequestException as e:
        logger.error(f"AllMusic scrape request failed: {e}")
        return []
    except Exception as e:
        logger.error(f"AllMusic scrape parsing failed: {e}")
        return []


def enrich_streaming_data(df: pd.DataFrame, artist_name: str) -> pd.DataFrame:
    """
    Enrich existing streaming dataframe with web-scraped data.
    
    Args:
        df: Existing streaming data DataFrame
        artist_name: Artist name to search for
    
    Returns:
        Original DataFrame with additional enrichment columns (if available)
    """
    logger.info(f"Enriching data for {artist_name} with web scrape results")
    
    try:
        scraped_df = scrape_music_trends(artist_name, max_results=5)
        
        if scraped_df.empty:
            logger.warning(f"No scraped data to enrich for {artist_name}")
            return df
        
        # Add enrichment columns
        df['web_enrichment'] = f"Data enriched with {len(scraped_df)} web sources on {datetime.datetime.now().strftime('%Y-%m-%d')}"
        
        logger.info(f"Successfully enriched data with {len(scraped_df)} web sources")
        return df
    
    except Exception as e:
        logger.error(f"Data enrichment failed: {e}")
        return df


if __name__ == "__main__":
    # Test the scraper
    print("\n=== Testing Web Scraper ===\n")
    test_artist = "Burna Boy"
    print(f"Scraping data for: {test_artist}")
    
    results_df = scrape_music_trends(test_artist, max_results=5)
    
    if not results_df.empty:
        print(f"\n✓ Found {len(results_df)} results\n")
        print(results_df.to_string(index=False))
    else:
        print("\n✗ No results found\n")
