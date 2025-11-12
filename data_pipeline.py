"""
Data pipeline for TuneIQ Insight - handles both sample and live data sources.
Supports fallback to sample data when API keys aren't configured.
Includes web scraping as an alternative data enrichment source.
"""

import os
import pandas as pd
from typing import Optional, Dict
from tuneiq_app.spotify_fetch import get_spotify_data
from tuneiq_app.youtube_fetch_oauth import get_youtube_analytics
from tuneiq_app.apple_music_fetch import get_apple_music_data
from tuneiq_app.web_scraper import scrape_music_trends, enrich_streaming_data

def load_sample_data() -> pd.DataFrame:
    """Load Burna Boy sample streaming data."""
    sample_path = os.path.join(os.path.dirname(__file__), 'sample_data/streaming_sample.csv')
    return pd.read_csv(sample_path)

def fetch_spotify_data(client_id: Optional[str] = None, 
                      client_secret: Optional[str] = None,
                      artist_name: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    Fetch Spotify streaming data if credentials provided, else return None.
    Uses client credentials flow (no user auth required).
    """
    if not (client_id and client_secret):
        return None
    
    try:
        return get_spotify_data(client_id, client_secret, artist_name=artist_name)
    except Exception as e:
        print(f"Spotify API Error: {e}")
        return None

def fetch_youtube_geo_data(credentials_json: Optional[Dict] = None,
                          artist_name: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    Fetch YouTube Analytics geographic data if OAuth credentials provided.
    Requires channel owner authentication.
    """
    if not credentials_json:
        return None
    
    try:
        # Pass artist_name for labeling if supported by the YouTube helper
        return get_youtube_analytics(credentials_json, artist_name=artist_name)
    except Exception as e:
        print(f"YouTube API Error: {e}")
        return None

def fetch_all(spotify_creds: Optional[Dict] = None,
              youtube_creds: Optional[Dict] = None,
              apple_music_creds: Optional[Dict] = None,
              artist_name: Optional[str] = None) -> pd.DataFrame:
    """
    Orchestration function to merge sample and live data when available.
    Falls back to sample data if no API credentials provided.
    """
    # Always load sample data as fallback
    df = load_sample_data()
    
    # Attempt to fetch live data if credentials provided
    if spotify_creds:
        spotify_df = fetch_spotify_data(
            spotify_creds.get('client_id'),
            spotify_creds.get('client_secret'),
            artist_name=artist_name
        )
        if spotify_df is not None:
            # Replace sample Spotify data with live data
            df = df[df['platform'] != 'Spotify'].copy()
            df = pd.concat([df, spotify_df])
    
    if youtube_creds:
        youtube_df = fetch_youtube_geo_data(youtube_creds, artist_name=artist_name)
        if youtube_df is not None:
            # Replace sample YouTube data with live data
            df = df[df['platform'] != 'YouTube'].copy()
            df = pd.concat([df, youtube_df])

    # Apple Music (optional/stub)
    if apple_music_creds:
        try:
            apple_df = get_apple_music_data(apple_music_creds, artist_name=artist_name)
            if apple_df is not None:
                df = df[df['platform'] != 'Apple Music'].copy()
                df = pd.concat([df, apple_df])
        except Exception as e:
            print(f"Apple Music API Error: {e}")
    
    return df.reset_index(drop=True)


def fetch_live_data(source: str = "web", artist_name: str = "Burna Boy") -> pd.DataFrame:
    """
    Fetch live data from specified source (Spotify, YouTube, or web scraper).
    
    Args:
        source: Data source type ('spotify', 'youtube', 'web')
        artist_name: Name of the artist to fetch data for
    
    Returns:
        pd.DataFrame with streaming data from specified source, or empty DataFrame on failure
    """
    if source.lower() == "spotify":
        print(f"Fetching Spotify data for {artist_name}...")
        # Requires credentials - return empty if none available
        return pd.DataFrame()
    
    elif source.lower() == "youtube":
        print(f"Fetching YouTube data for {artist_name}...")
        # Requires credentials - return empty if none available
        return pd.DataFrame()
    
    elif source.lower() == "web":
        print(f"Scraping live web data for {artist_name}...")
        try:
            scraped_df = scrape_music_trends(artist_name, max_results=15)
            if not scraped_df.empty:
                print(f"✓ Web scrape successful: {len(scraped_df)} results found")
                return scraped_df
            else:
                print(f"✗ No results found via web scraping for {artist_name}")
                return pd.DataFrame()
        except Exception as e:
            print(f"✗ Web scraping failed: {e}")
            return pd.DataFrame()
    
    else:
        raise ValueError(f"Invalid data source '{source}'. Use 'spotify', 'youtube', or 'web'.")


def enrich_data_with_web(df: pd.DataFrame, artist_name: str) -> pd.DataFrame:
    """
    Enrich existing streaming data with web-scraped insights.
    
    Args:
        df: Existing streaming DataFrame
        artist_name: Artist name to enrich for
    
    Returns:
        DataFrame enriched with web scrape metadata
    """
    print(f"Enriching data with web sources for {artist_name}...")
    try:
        enriched_df = enrich_streaming_data(df, artist_name)
        print(f"✓ Data enrichment completed")
        return enriched_df
    except Exception as e:
        print(f"✗ Data enrichment failed: {e}")
        return df