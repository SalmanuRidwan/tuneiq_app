"""
TuneIQ Solution - Making Nigeria's music economy visible.
Streamlit dashboard for music streaming analytics and economic impact analysis.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from typing import Dict, Optional
import json
import sys
import os
import importlib

# Ensure package imports work when running the script from inside the package folder
# (e.g., `cd tuneiq_app && streamlit run app.py`). We add the parent directory to sys.path
# so `import tuneiq_app.*` resolves to the package on disk.
if __package__ is None or __package__ == "":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
# Dynamically import internal modules to avoid static analysis errors for absolute package imports
# Try package-style imports first, then fall back to top-level module imports.
fetch_all = None
estimate_royalties = None
detect_underpayment = None
economic_impact_proxy = None
COUNTRIES = None
NIGERIAN_ARTISTS = None

try:
    # Prefer package-style imports (works when the package is installed or when executed as a module)
    dp = importlib.import_module("tuneiq_app.data_pipeline")
    fetch_all = getattr(dp, "fetch_all")
    models = importlib.import_module("tuneiq_app.models")
    estimate_royalties = getattr(models, "estimate_royalties")
    detect_underpayment = getattr(models, "detect_underpayment")
    economic_impact_proxy = getattr(models, "economic_impact_proxy")
    countries_mod = importlib.import_module("tuneiq_app.countries")
    COUNTRIES = getattr(countries_mod, "COUNTRIES")
    na_mod = importlib.import_module("tuneiq_app.nigerian_artists")
    NIGERIAN_ARTISTS = getattr(na_mod, "NIGERIAN_ARTISTS")
except Exception:
    # Fallback when running app.py directly (e.g., `streamlit run app.py` from within the package folder)
    try:
        dp = importlib.import_module("data_pipeline")
        fetch_all = getattr(dp, "fetch_all")
        models = importlib.import_module("models")
        estimate_royalties = getattr(models, "estimate_royalties")
        detect_underpayment = getattr(models, "detect_underpayment")
        economic_impact_proxy = getattr(models, "economic_impact_proxy")
        countries_mod = importlib.import_module("countries")
        COUNTRIES = getattr(countries_mod, "COUNTRIES")
        na_mod = importlib.import_module("nigerian_artists")
        NIGERIAN_ARTISTS = getattr(na_mod, "NIGERIAN_ARTISTS")
    except Exception as e:
        raise ImportError(
            "Could not import internal modules. Run from the project root or install the package "
            "(pip install -e .) so 'tuneiq_app' package imports resolve."
        ) from e

# Page config
st.set_page_config(
    page_title="TuneIQ Solution",
    page_icon="assets/logo.png",
    layout="wide"
)

# Custom CSS for dark neon theme
st.markdown("""
<style>
    /* Root theme variables - Updated Palette */
    :root{
        --bg-1: #F4F7F5;
        --bg-2: #F4F7F5;
        --neon-1: #0EA5A4; /* teal */
        --neon-2: #7C3AED; /* violet accent */
        --accent: #1F213A; /* deep indigo */
        --gold: #F59E0B; /* warm accent */
        --silver: #94A3B8;
        --glass: rgba(14,165,164,0.08);
        --muted: #475569;
    }
    
    /* Logo styles */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 20px 0;
        margin-bottom: 30px;
    }
    
    .logo-image {
        width: 80px;
        height: 80px;
        filter: drop-shadow(0 0 10px rgba(6,141,157,0.3));
    }
    
    .logo-text {
        display: flex;
        flex-direction: column;
    }
    
    .logo-title {
        font-size: 2.5rem !important;
        font-weight: 800;
        margin: 0 !important;
        background: linear-gradient(90deg, #068D9D, #3C3744);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        text-shadow: 0 0 20px rgba(6,141,157,0.2);
    }
    
    .logo-tagline {
        font-size: 1.1rem;
        color: #3C3744;
        margin-top: 5px;
        font-weight: 400;
    }

    /* Animated gradient background */
    html, body, .stApp {
        height: 100%;
        background: radial-gradient(circle at 10% 10%, rgba(6,141,157,0.06), transparent 10%),
                                radial-gradient(circle at 90% 90%, rgba(60,55,68,0.03), transparent 10%),
                                linear-gradient(180deg, #F4F7F5, #F4F7F5);
        color: #3C3744 !important;
        font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
    }

    /* Animated gradient title */
    h1 {
        font-size: 2.2rem !important;
        margin: 0 !important;
        font-weight: 800;
        background: linear-gradient(90deg, #068D9D, #3C3744, #068D9D);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        animation: hue 6s linear infinite;
        text-align: right !important;
    }

    @keyframes hue{ 0%{filter: hue-rotate(0deg);}50%{filter: hue-rotate(40deg);}100%{filter: hue-rotate(0deg);} }

    /* Glass KPI cards */
    .stMetric, .stMetric > div {
        background: linear-gradient(135deg, rgba(6,141,157,0.04), rgba(60,55,68,0.02)) !important;
        border: 1px solid rgba(6,141,157,0.2) !important;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1) inset, 0 8px 24px rgba(6,141,157,0.06);
        border-radius: 12px !important;
        padding: 10px !important;
        color: #3C3744 !important;
    }

    /* Bright neon values for metric numbers */
    .stMetric .value, .stMetric .stMetricValue {
        color: #068D9D !important;
        font-weight: 800 !important;
        text-shadow: 0 6px 18px rgba(6,141,157,0.12);
    }

    /* Make buttons look like neon pills */
    .stButton>button {
        background: linear-gradient(90deg, rgba(6,141,157,0.12), rgba(60,55,68,0.12));
        color: #068D9D !important;
        border: 1px solid rgba(6,141,157,0.25) !important;
        padding: 10px 14px !important;
        border-radius: 999px !important;
        box-shadow: 0 8px 30px rgba(6,141,157,0.08);
        transition: transform 0.12s ease, box-shadow 0.12s ease;
    }
    .stButton>button:hover{ transform: translateY(-2px); box-shadow: 0 16px 46px rgba(6,141,157,0.15); }

    /* Sidebar styling */
    .css-1d391kg .css-1lcbmhc { background: linear-gradient(180deg, rgba(6,141,157,0.08), rgba(60,55,68,0.06)); }
    .sidebar .stMarkdown, .sidebar .stTextInput { color: #3C3744 !important; }

    /* Glass panels for main content blocks */
    .element-container, .block-container .stExpander {
        background: linear-gradient(180deg, rgba(6,141,157,0.04), rgba(60,55,68,0.02));
        border: 1px solid rgba(6,141,157,0.15);
        border-radius: 10px;
        padding: 12px;
    }

    /* Tables */
    .stTable td, .stTable th { color: #3C3744 !important; }

    /* Footer */
    footer { opacity: 0.8; color: #068D9D !important; }
    
    /* Web Scraper Section Styling */
    .web-scraper-container {
        background: linear-gradient(135deg, rgba(6,141,157,0.08), rgba(60,55,68,0.06));
        border: 1px solid rgba(6,141,157,0.25);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        backdrop-filter: blur(10px);
    }
    
    .web-scraper-title {
        font-size: 1.3em;
        font-weight: 600;
        color: #068D9D;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .web-data-card {
        background: linear-gradient(135deg, rgba(6,141,157,0.05), rgba(60,55,68,0.03));
        border: 1px solid rgba(6,141,157,0.15);
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        transition: all 0.3s ease;
    }
    
    .web-data-card:hover {
        border-color: rgba(6,141,157,0.35);
        box-shadow: 0 4px 12px rgba(6,141,157,0.1);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 6px;
        color: #3C3744 !important;
    }
    
    .stTabs [aria-selected="true"] {
        border-bottom: 2px solid #068D9D;
    }

</style>
""", unsafe_allow_html=True)

def load_data(use_live: bool = False) -> pd.DataFrame:
    """Load data based on mode selection.

    If live data has been fetched previously and stored in session_state['latest_df'],
    return that. Otherwise fetch sample or live on-demand.
    """
    # If a prior live fetch succeeded, use it
    if use_live and st.session_state.get('latest_df') is not None:
        return st.session_state['latest_df']

    # If live mode is requested, and platform creds are available for selected platforms,
    # pass only those credentials to fetch_all. Otherwise fall back to sample data.
    if use_live:
        platforms_to_fetch = st.session_state.get('platforms_to_fetch', [])
        has_creds = (
            ("Spotify" in platforms_to_fetch and st.session_state.get('spotify_creds')) or
            ("YouTube" in platforms_to_fetch and st.session_state.get('youtube_creds')) or
            ("Apple Music" in platforms_to_fetch and st.session_state.get('apple_music_creds'))
        )
        if has_creds:
            return fetch_all(
                spotify_creds=st.session_state.get('spotify_creds') if "Spotify" in platforms_to_fetch else None,
                youtube_creds=st.session_state.get('youtube_creds') if "YouTube" in platforms_to_fetch else None,
                apple_music_creds=st.session_state.get('apple_music_creds') if "Apple Music" in platforms_to_fetch else None,
                artist_name=st.session_state.get('filter_artist') or st.session_state.get('artist_name')
            )

    # Default: sample data
    return fetch_all()

def format_ngn(amount: float) -> str:
    """Format amount in Nigerian Naira."""
    return f"₦{amount:,.2f}"

def render_kpi_cards(df: pd.DataFrame, impact_metrics: Dict):
    """Render KPI metric cards in the dashboard."""
    cols = st.columns(4)
    
    # Total Streams
    with cols[0]:
        st.metric(
            "Total Streams",
            f"{df['streams'].sum():,}",
            "Across All Platforms"
        )
    
    # Revenue
    with cols[1]:
        st.metric(
            "Est. Revenue",
            format_ngn(impact_metrics['direct_revenue_ngn']),
            f"+ {format_ngn(impact_metrics['indirect_revenue_ngn'])} indirect"
        )
    
    # Global Reach
    with cols[2]:
        country_count = len(df['country'].unique())
        st.metric(
            "Global Reach",
            f"{country_count} Countries",
            "Cultural Export"
        )
    
    # Underpayment Alerts
    with cols[3]:
        underpaid = detect_underpayment(df)
        alert_count = len(underpaid)
        st.metric(
            "Underpayment Alerts",
            f"{alert_count} Countries",
            "Requiring Investigation"
        )

def render_charts(df: pd.DataFrame, selected_platforms=None):
    """Render main dashboard visualizations."""
    # Filter data based on selected platforms
    if selected_platforms:
        df = df[df['platform'].isin(selected_platforms)]
    
    # If no data after filtering, show message and return
    if df.empty:
        st.warning("No data available for the selected platforms. Please select at least one platform.")
        return
        
    # Compute per-country impact and identify top-10 countries by impact
    # Ensure expected_revenue_ngn exists (estimate_royalties called earlier in main)
    country_impact = df.groupby('country').agg({
        'streams': 'sum',
        'expected_revenue_ngn': 'sum',
        'actual_revenue_ngn': 'sum'
    }).reset_index()
    country_impact['revenue_gap'] = country_impact['expected_revenue_ngn'] - country_impact['actual_revenue_ngn']
    # Define impact_value as expected revenue (proxy for economic impact)
    country_impact['impact_value_ngn'] = country_impact['expected_revenue_ngn']
    # Top 10 high impact countries
    top10 = country_impact.sort_values('impact_value_ngn', ascending=False).head(10).copy()

    # Global Streaming Distribution (choropleth colored by streams, with top-10 highlighted)
    st.subheader("Global Streaming Distribution")
    geo_data = country_impact.copy()
    # Add a flag to indicate top10
    geo_data['is_top10'] = geo_data['country'].isin(top10['country']).astype(int)

    fig_map = px.choropleth(
        geo_data,
        locations='country',
        locationmode='country names',
        color='streams',
        color_continuous_scale='Viridis',
        template="plotly_dark",
        title='Global Streams (top-10 impact countries highlighted)'
    )

    # Overlay top-10 markers to highlight them
    try:
        fig_scatter = px.scatter_geo(
            top10,
            locations='country',
            locationmode='country names',
            size='impact_value_ngn',
            hover_name='country',
            projection='natural earth'
        )
        # Add scatter traces to choropleth
        for trace in fig_scatter.data:
            fig_map.add_trace(trace)
    except Exception:
        # Fallback: ignore overlay if scatter fails due to location lookups
        pass

    st.plotly_chart(fig_map, use_container_width=True)

    # Streaming Trends and Revenue Analysis in equal columns
    col1, col2 = st.columns(2)

    with col1:
        # Streams by Platform
        st.subheader("Streaming Trends")
        platform_data = df.groupby('platform')['streams'].sum().reset_index()
        
        # Add platform icons
        platform_icons = {
            'Spotify': '🎵',
            'YouTube': '▶️',
            'Apple Music': '🍎'
        }
        platform_data['platform_label'] = platform_data['platform'].apply(
            lambda x: f"{platform_icons.get(x, '')} {x}"
        )
        
        fig_platform = px.bar(
            platform_data,
            x='platform_label',
            y='streams',
            color='platform',
            template="plotly_dark",
            labels={'platform_label': 'Platform', 'streams': 'Total Streams'}
        )
        
        # Enhanced styling
        fig_platform.update_traces(
            marker_line_color='rgba(255,215,0,0.3)',
            marker_line_width=1,
            opacity=0.8
        )
        
        # Update layout
        fig_platform.update_layout(
            title={
                'text': f"Streaming Distribution Across {len(platform_data)} Platform(s)",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            showlegend=False
        )
        
        st.plotly_chart(fig_platform, use_container_width=True)
        
        # Add platform stats
        with st.expander("Platform Statistics"):
            stats_df = platform_data.copy()
            total_streams = stats_df['streams'].sum()
            stats_df['percentage'] = (stats_df['streams'] / total_streams * 100).round(2)
            stats_df['streams'] = stats_df['streams'].map(lambda x: f"{int(x):,}")
            stats_df['percentage'] = stats_df['percentage'].map(lambda x: f"{x}%")
            st.dataframe(
                stats_df[['platform', 'streams', 'percentage']],
                column_config={
                    "platform": "Platform",
                    "streams": "Total Streams",
                    "percentage": "Market Share"
                },
                hide_index=True
            )

    with col2:
        # Revenue Gap Analysis - show top-10 high impact countries by default
        st.subheader("Revenue Gap Analysis (Top 10 Impact Countries)")
        show_revenue_details = st.checkbox("Show full country list", value=False)

        if show_revenue_details:
            display_df = country_impact.sort_values('revenue_gap', ascending=False)
        else:
            display_df = top10.copy()

        display_df = display_df.assign(
            streams=display_df['streams'].map('{:,.0f}'.format),
            expected_revenue_ngn=display_df['expected_revenue_ngn'].map(lambda x: f"₦{x:,.0f}"),
            actual_revenue_ngn=display_df['actual_revenue_ngn'].map(lambda x: f"₦{x:,.0f}"),
            revenue_gap=display_df['revenue_gap'].map(lambda x: f"₦{x:,.0f}")
        )

        st.dataframe(display_df[['country', 'streams', 'expected_revenue_ngn', 'actual_revenue_ngn', 'revenue_gap']])

def main():
    """Main dashboard layout and logic."""
    # Initialize use_live flag
    use_live = False
    
    # Custom CSS for header styling
    st.markdown("""
    <style>
    /* Header button styles */
    div[data-testid="stHorizontalBlock"] > div button {
        width: 100%;
        border: 1px solid rgba(6,141,157,0.25) !important;
        border-radius: 12px !important;
        padding: 15px 20px !important;
        color: #068D9D !important;
        background: linear-gradient(135deg, 
            rgba(6,141,157,0.08), 
            rgba(60,55,68,0.06)
        ) !important;
        transition: all 0.3s ease !important;
        position: relative;
        overflow: hidden;
    }
    
    /* Button shine effect */
    div[data-testid="stHorizontalBlock"] > div button::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            45deg,
            transparent,
            rgba(6,141,157,0.1),
            transparent
        );
        transform: rotate(45deg);
        transition: all 0.3s ease;
    }

    /* Button hover effect */
    div[data-testid="stHorizontalBlock"] > div button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(6,141,157,0.15) !important;
        background: linear-gradient(135deg, 
            rgba(6,141,157,0.12), 
            rgba(60,55,68,0.1)
        ) !important;
    }
    
    div[data-testid="stHorizontalBlock"] > div button:hover::after {
        transform: rotate(45deg) translate(150%, 150%);
    }

    /* Selected button state */
    div[data-testid="stHorizontalBlock"] > div button.selected {
        background: linear-gradient(135deg, 
            rgba(6,141,157,0.2), 
            rgba(60,55,68,0.1)
        ) !important;
        box-shadow: 
            0 8px 25px rgba(6,141,157,0.2),
            0 0 0 1px rgba(6,141,157,0.4) !important;
        transform: translateY(-2px);
    }

    /* Header section container */
    .header-section {
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        background: linear-gradient(135deg,
            rgba(6,141,157,0.05),
            rgba(60,55,68,0.03)
        );
        border: 1px solid rgba(6,141,157,0.15);
        backdrop-filter: blur(10px);
    }

    /* Section title */
    .section-title {
        color: #068D9D;
        font-weight: 600;
        font-size: 1.2em;
        margin-bottom: 15px;
        text-shadow: 0 0 10px rgba(6,141,157,0.2);
    }

    /* Icon styling in buttons */
    div[data-testid="stHorizontalBlock"] button svg {
        margin-right: 8px;
        vertical-align: middle;
    }
    </style>
    """, unsafe_allow_html=True)
    def get_base64_image(image_path):
        import base64
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    # Convert logo to Base64
    image_base64 = get_base64_image("./assets/logo.png")

    # Main header with logo and title
    # st.markdown(f"""
    # <div class="logo-container" style="display:flex; align-items:left; gap:20px; margin-bottom:20px;">
    #     <img src="data:image/png;base64,{image_base64}" 
    #         alt="TuneIQ Logo" 
    #         style="width:100px; height:100px; object-fit:contain;">
    #     <div class="logo-text">
    #         <h1 class="logo-title" style="margin-left: 0px; align-items: left; color:#00FFC2;">TuneIQ Solution</h1>
    #         <div class="logo-tagline" style="font-size:1.5em; color:#ccc;">Making Nigeria's music economy visible through data-driven analytics.</div>
    #     </div>
    # </div>
    # """, unsafe_allow_html=True)
    st.markdown(f"""
<style>
/* higher specificity + important to override theme styles */
.logo-container {{ display:flex !important; align-items:center !important; gap:12px !important; }}
.logo-container img {{ width:90px !important; height:90px !important; object-fit:contain !important; margin:0 !important; }}
.logo-text {{ display:flex !important; flex-direction:column !important; justify-content:center !important; }}
.logo-title {{
  margin:0 !important;
  padding:0 !important;
  font-size:2.0em !important;
  line-height:1 !important;
  color:#black !important;
  display:inline-block !important;
  vertical-align:middle !important;
}}
.logo-tagline {{ margin-top:4px !important; font-size:1.1em !important; color:#88888 !important; }}
</style>

<div class="logo-container">
    <img src="data:image/png;base64,{image_base64}" alt="TuneIQ Logo">
    <div class="logo-text">
        <h1 class="logo-title">TuneIQ Solution</h1>
        <div class="logo-tagline">Making Nigeria's music economy visible through data-driven analytics.</div>
    </div>
</div>
""", unsafe_allow_html=True)


    
    # Initialize session state for section visibility
    if 'show_live_data' not in st.session_state:
        st.session_state.show_live_data = False
    if 'show_filters' not in st.session_state:
        st.session_state.show_filters = False
    if 'active_section' not in st.session_state:
        st.session_state.active_section = None
    if 'platforms_to_fetch' not in st.session_state:
        st.session_state.platforms_to_fetch = ["Spotify"]  # Default platform
    if 'selected_platforms' not in st.session_state:
        st.session_state.selected_platforms = ["Spotify"]  # Default platform
    if 'web_scraped_data' not in st.session_state:
        st.session_state.web_scraped_data = pd.DataFrame()  # Empty DataFrame for web scrape results
    if 'web_scraped_artist' not in st.session_state:
        st.session_state.web_scraped_artist = None  # Track which artist was scraped
    if 'filter_artist' not in st.session_state:
        # Default artist selection for Filters & Analysis (keeps prior behavior if Burna Boy exists)
        st.session_state.filter_artist = NIGERIAN_ARTISTS[0] if len(NIGERIAN_ARTISTS) > 0 else None

    # Header buttons in a single row with selection state
    header_cols = st.columns(2)
    
    # Initialize button states in session state if not present
    if 'active_section' not in st.session_state:
        st.session_state.active_section = None
    
    with header_cols[0]:
        btn_style = "selected" if st.session_state.show_live_data else ""
        if st.button(
            "📊 Data Configuration",
            key="live_data_btn",
            help="Configure data source and select platforms",
            use_container_width=True
        ):
            st.session_state.show_live_data = not st.session_state.show_live_data
            st.session_state.active_section = "data_source" if not st.session_state.show_live_data else None
    
    with header_cols[1]:
        btn_style = "selected" if st.session_state.show_filters else ""
        if st.button(
            "🔍 Filters & Analysis",
            key="filters_btn",
            help="Set time period and country filters",
            use_container_width=True
        ):
            st.session_state.show_filters = not st.session_state.show_filters
            st.session_state.show_live_data = False
            st.session_state.active_section = "filters" if st.session_state.show_filters else None
            
    # Add visual separator after header
    st.markdown("<hr style='margin: 25px 0; border: none; border-top: 1px solid rgba(0,255,194,0.1);'>", 
                unsafe_allow_html=True)

    # Data Configuration Section
    if st.session_state.show_live_data:
        with st.container():
            st.markdown('<div class="header-section">', unsafe_allow_html=True)
            st.markdown('<p class="section-title">Data Configuration</p>', unsafe_allow_html=True)
            
            # Data Source Selection
            use_live = st.checkbox("Enable Live Data", value=False, help="Check to enable live API mode")
            
            # Platform Selection (moved from separate section)
            platforms_to_fetch = st.multiselect(
                "Select Platforms to Analyze",
                ["Spotify", "YouTube", "Apple Music"],
                default=["Spotify"],
                help="Choose which platforms to analyze"
            )
            st.session_state['platforms_to_fetch'] = platforms_to_fetch
            st.session_state['selected_platforms'] = platforms_to_fetch  # Store for filtering visualizations

            if use_live:
                st.info("Configure API credentials below")
            
            # Web Scraper Quick Access
            st.markdown("---")
            st.markdown('<p class="section-title">🌐 Web Data Source</p>', unsafe_allow_html=True)
            
            web_scraper_col1, web_scraper_col2 = st.columns([2, 1])
            with web_scraper_col1:
                # Artist selection has been moved to Filters & Analysis.
                current_filter_artist = st.session_state.get('filter_artist', NIGERIAN_ARTISTS[0] if NIGERIAN_ARTISTS else 'Unknown')
                st.markdown(f"**Artist (Filters & Analysis):** {current_filter_artist}")
            with web_scraper_col2:
                fetch_web_data = st.button("🔍 Scrape Web Data", use_container_width=True, key="web_scrape_btn")
            
            if fetch_web_data:
                # Use the artist selected in Filters & Analysis
                artist_for_scrape = st.session_state.get('filter_artist', NIGERIAN_ARTISTS[0] if NIGERIAN_ARTISTS else None)
                with st.spinner(f"🔄 Scraping web data for {artist_for_scrape}..."):
                    try:
                        from data_pipeline import fetch_live_data
                        web_df = fetch_live_data(source="web", artist_name=artist_for_scrape)

                        if not web_df.empty:
                            st.session_state['web_scraped_data'] = web_df
                            st.session_state['web_scraped_artist'] = artist_for_scrape
                            st.success(f"✓ Successfully scraped {len(web_df)} results for {artist_for_scrape}")

                            # Show preview of scraped data
                            with st.expander(f"📋 Preview Web Data ({len(web_df)} results)", expanded=True):
                                # Create a formatted display of web scrape results
                                display_cols = ["artist", "title", "source", "url", "date_fetched"]
                                available_cols = [col for col in display_cols if col in web_df.columns]
                                st.dataframe(web_df[available_cols], use_container_width=True)
                        else:
                            st.warning(f"⚠️ No results found for {artist_for_scrape}. Try a different artist in Filters & Analysis or check your internet connection.")
                    except Exception as e:
                        st.error(f"✗ Web scraping failed: {str(e)}")
                
            st.markdown('</div>', unsafe_allow_html=True)
            # Mirror header selections into local variables used below
            header_months = st.session_state.get('selected_months')
            header_country = st.session_state.get('header_country')

    
    # Live data configuration in expandable section
    if use_live:
        with st.expander("Configure API Credentials"):
            # Platform selection
            platforms_to_fetch = st.multiselect(
                "Select Platforms to Fetch Data From",
                ["Spotify", "YouTube", "Apple Music"],
                default=["Spotify"],
                help="Choose which platforms to fetch data from"
            )
            st.session_state['platforms_to_fetch'] = platforms_to_fetch

            # Artist selection moved to Filters & Analysis (stored in session_state['filter_artist'])

            # Platform-specific credentials
            if "Spotify" in platforms_to_fetch:
                st.subheader("Spotify Credentials")
                spotify_id = st.text_input("Spotify Client ID", type="password")
                spotify_secret = st.text_input("Spotify Client Secret", type="password")
                if spotify_id and spotify_secret:
                    st.session_state['spotify_creds'] = {
                        'client_id': spotify_id,
                        'client_secret': spotify_secret
                    }

            if "YouTube" in platforms_to_fetch:
                st.subheader("YouTube Credentials")
                youtube_json = st.text_area(
                    "YouTube OAuth Credentials (JSON)",
                    height=100
                )
                if youtube_json:
                    try:
                        st.session_state['youtube_creds'] = json.loads(youtube_json)
                    except json.JSONDecodeError:
                        st.error("Invalid YouTube credentials JSON")

            if "Apple Music" in platforms_to_fetch:
                st.subheader("Apple Music Credentials")
                st.markdown("You can either paste a pre-generated Developer Token, or supply key material to generate one.")
                apple_developer_token = st.text_area(
                    "Apple Music Developer Token (optional)",
                    height=80,
                    help="If you have a pre-generated developer token, paste it here (recommended for testing)."
                )
                apple_key_id = st.text_input("Apple Key ID", type="password")
                apple_team_id = st.text_input("Apple Team ID", type="password")
                apple_private_key = st.text_area(
                    "Apple Music Private Key (PEM)",
                    height=120,
                    help="Paste your Apple Music private key (PEM) here if you want the app to generate a token."
                )
                # Prefer explicit developer token if provided, else keep key material
                if apple_developer_token:
                    st.session_state['apple_music_creds'] = {
                        'developer_token': apple_developer_token.strip()
                    }
                elif apple_key_id and apple_team_id and apple_private_key:
                    st.session_state['apple_music_creds'] = {
                        'key_id': apple_key_id,
                        'team_id': apple_team_id,
                        'private_key': apple_private_key
                    }

            # Fetch button
            fetch_button = st.button("Fetch Live Data")
            if fetch_button:
                st.session_state['fetching'] = True
                # Use the filter artist selected in Filters & Analysis when fetching live data
                selected_artist = st.session_state.get('filter_artist') or st.session_state.get('artist_name')
                with st.spinner(f"Fetching live data for {selected_artist} from APIs (falls back to sample where necessary)..."):
                    try:
                        fetched = fetch_all(
                            spotify_creds=st.session_state.get('spotify_creds'),
                            youtube_creds=st.session_state.get('youtube_creds'),
                            apple_music_creds=st.session_state.get('apple_music_creds'),
                            artist_name=selected_artist
                        )
                        if fetched is None or fetched.empty:
                            st.warning(f"No data found for {selected_artist}; continuing with sample data.")
                        else:
                            st.session_state['latest_df'] = fetched
                            st.session_state['current_artist'] = selected_artist
                            st.success(f"Live data fetched for {selected_artist} and applied to the dashboard")
                    except Exception as e:
                        st.error(f"Error fetching live data: {e}")
                st.session_state['fetching'] = False
    
    # Initialize filter values as None
    header_platforms = None
    header_months = None
    header_country = None
    
    # Load and process data
    df = load_data(use_live)

    # Ensure artist_image field exists consistently (merge info from any platform)
    if 'artist_image' not in df.columns:
        df['artist_image'] = None
    else:
        # forward-fill a single artist image if present on some rows
        imgs = df['artist_image'].dropna().unique()
        if len(imgs) > 0:
            df['artist_image'] = df['artist_image'].fillna(imgs[0])
        else:
            df['artist_image'] = None

    df = estimate_royalties(df)
    impact_metrics = economic_impact_proxy(df)

    # Source badge
    if st.session_state.get('latest_df') is not None:
        st.markdown("**Data source:** 🔴 Live (fetched)")
    else:
        st.markdown("**Data source:** 🟢 Sample")

    # Artist badge (show thumbnail + resolved name)
    # Display artist from Filters & Analysis (preferred), otherwise fall back to current fetched artist or legacy artist_name
    artist_name_display = st.session_state.get('filter_artist') or st.session_state.get('current_artist') or st.session_state.get('artist_name') or 'Burna Boy'
    artist_image_display = None
    if 'artist_image' in df.columns and not df['artist_image'].isnull().all():
        artist_image_display = df['artist_image'].dropna().unique()[0]

    badge_col1, badge_col2 = st.columns([1, 4])
    with badge_col1:
        if artist_image_display:
            st.image(artist_image_display, width=100, caption=artist_name_display)
        else:
            st.markdown(f"**Artist:** {artist_name_display}")
    with badge_col2:
        st.markdown(f"### {artist_name_display}")
    
    # Clean data for filtering
    df['platform'] = df['platform'].fillna('Spotify').astype(str)
    df['platform'] = df['platform'].replace('Unknown', 'Spotify')
    df = df[df['month'].notna()]  # Remove rows with Unknown months
    df['month'] = df['month'].astype(str)
    
    # Get unique values and sort
    platforms = sorted(df['platform'].unique().tolist(), key=str)
    months = sorted(df['month'].unique().tolist(), key=str)
    
    # Initialize filter selections if not in session state
    if 'selected_platforms' not in st.session_state:
        st.session_state.selected_platforms = platforms
    if 'selected_months' not in st.session_state:
        st.session_state.selected_months = months
    
    # Prepare country options
    country_options = list(COUNTRIES)
    for c in sorted(df['country'].dropna().unique().tolist()):
        if c and c not in country_options:
            country_options.append(c)
    country_options = sorted(country_options)
    country_options.insert(0, 'All')
    
    # Filters Section (replaces header filters)
    if st.session_state.show_filters:
        with st.container():
            st.markdown('<div class="header-section">', unsafe_allow_html=True)
            st.markdown('<p class="section-title">Filters & Analysis</p>', unsafe_allow_html=True)
            
            filter_cols = st.columns(2)
            with filter_cols[0]:
                # Present human-friendly month labels (e.g., Jan 2025) while storing the underlying month codes
                def _format_month_label(m: str) -> str:
                    try:
                        if '-' in m:
                            parts = m.split('-')
                            year = int(parts[0]); month = int(parts[1])
                            return pd.to_datetime(f"{year}-{month:02d}-01").strftime('%b %Y')
                        return m
                    except Exception:
                        return m

                month_display_map = {m: _format_month_label(m) for m in months}
                month_display_list = [month_display_map[m] for m in months]

                # Defaults: convert stored selected_months (which are codes) to display labels
                default_display = [month_display_map.get(m, m) for m in st.session_state.get('selected_months', months)]

                selected_display = st.multiselect(
                    "Time Period",
                    month_display_list,
                    default=default_display
                )

                # Convert back to the underlying month codes and store
                selected_months = [orig for orig, label in month_display_map.items() if label in selected_display]
                if not selected_months:
                    # fallback to all months when user clears selection
                    selected_months = months
                st.session_state.selected_months = selected_months
            with filter_cols[1]:
                # Artist selector moved into Filters & Analysis (authoritative artist for the dashboard)
                st.selectbox(
                    "Select Artist",
                    options=NIGERIAN_ARTISTS,
                    index=NIGERIAN_ARTISTS.index('Burna Boy') if 'Burna Boy' in NIGERIAN_ARTISTS else 0,
                    key="filter_artist",
                    help="Choose a Nigerian artist to analyze"
                )

                header_country = st.selectbox(
                    "Country",
                    country_options,
                    key="header_country"
                )
                
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Sidebar mirror of filters (synced with header)
    # st.sidebar.header("Filters & Drilldown")
    selected_platforms = header_platforms  # Use header selection
    selected_months = header_months  # Use header selection
    drill_country = header_country  # Use header selection

    # If header-based selections are not present (filters hidden), fall back to session_state selections
    if not selected_months or not isinstance(selected_months, list):
        selected_months = st.session_state.get('selected_months', months)
    if not drill_country:
        drill_country = st.session_state.get('header_country')
    
    # Show current selections in sidebar for reference
    # st.sidebar.markdown("### Current Filters")
    
    # Ensure we have lists before joining
    platforms_display = selected_platforms if isinstance(selected_platforms, list) else []
    months_display = selected_months if isinstance(selected_months, list) else []
    
    # st.sidebar.markdown(f"**Platforms:** {', '.join(map(str, platforms_display))}")
    # st.sidebar.markdown(f"**Months:** {', '.join(map(str, months_display))}")
    # st.sidebar.markdown(f"**Country:** {drill_country if drill_country else 'All'}")

    # Ensure platform and month are strings before filtering
    df['platform'] = df['platform'].fillna('Unknown').astype(str)
    df['month'] = df['month'].fillna('Unknown').astype(str)
    
    # Ensure we have valid lists for filtering
    valid_platforms = selected_platforms if isinstance(selected_platforms, list) else df['platform'].unique().tolist()
    valid_months = selected_months if isinstance(selected_months, list) else df['month'].unique().tolist()
    
    # Apply filters
    filtered_df = df[
        (df['platform'].isin(valid_platforms)) & 
        (df['month'].isin(valid_months))
    ]
    
    if drill_country and drill_country != 'All':
        filtered_df = filtered_df[filtered_df['country'] == drill_country]

    # Get currently selected platforms
    selected_platforms = st.session_state.get('platforms_to_fetch', ["Spotify"])
    
    # Render dashboard components with filtered data
    render_kpi_cards(filtered_df, impact_metrics)
    render_charts(filtered_df, selected_platforms)

    # Country-level detail panel when drilled down
    if drill_country != 'All':
        st.subheader(f"Details for {drill_country}")
        country_agg = filtered_df.groupby('platform').agg({'streams': 'sum', 'expected_revenue_ngn': 'sum', 'actual_revenue_ngn': 'sum'}).reset_index()
        fig_country = px.bar(country_agg, x='platform', y='streams', title=f"Streams in {drill_country} by Platform", template='plotly_dark')
        st.plotly_chart(fig_country, use_container_width=True)
        st.dataframe(country_agg.assign(
            expected_revenue_ngn=country_agg['expected_revenue_ngn'].map(lambda x: f"₦{x:,.0f}"),
            actual_revenue_ngn=country_agg['actual_revenue_ngn'].map(lambda x: f"₦{x:,.0f}")
        ))
    
    # Web Scraping Data Display
    if 'web_scraped_data' in st.session_state and not st.session_state['web_scraped_data'].empty:
        web_artist = st.session_state.get('web_scraped_artist', 'Unknown Artist')
        web_df = st.session_state['web_scraped_data']
        
        st.markdown("---")
        st.subheader(f"🌐 Web Research Data for {web_artist}")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📰 All Sources", "🔗 By Source", "📊 Source Statistics"])
        
        with tab1:
            # Display all scraped data in a nice format
            st.write(f"**Total sources found:** {len(web_df)}")
            
            # Create columns for better display
            cols_to_display = ['artist', 'title', 'source', 'url', 'date_fetched']
            cols_available = [col for col in cols_to_display if col in web_df.columns]
            
            # Format and display
            display_df = web_df[cols_available].copy()
            
            # Add clickable links if URL column exists
            if 'url' in display_df.columns:
                display_df['url'] = display_df['url'].apply(
                    lambda x: f"[🔗 Link]({x})" if pd.notna(x) and x != 'N/A' else 'N/A'
                )
            
            st.dataframe(
                display_df,
                use_container_width=True,
                column_config={
                    "artist": "Artist",
                    "title": "Title/Content",
                    "source": st.column_config.TextColumn("Source", width="medium"),
                    "url": st.column_config.LinkColumn("URL"),
                    "date_fetched": "Date Fetched"
                } if 'url' in display_df.columns else None,
                hide_index=True
            )
        
        with tab2:
            # Group by source and show statistics
            source_breakdown = web_df['source'].value_counts().reset_index()
            source_breakdown.columns = ['Source', 'Count']
            
            # Create two columns for breakdown
            col_left, col_right = st.columns([1, 2])
            
            with col_left:
                st.metric("Total Sources", len(web_df['source'].unique()))
                st.dataframe(source_breakdown, hide_index=True, use_container_width=True)
            
            with col_right:
                # Pie chart of source distribution
                fig_sources = px.pie(
                    source_breakdown,
                    names='Source',
                    values='Count',
                    title='Data Distribution by Source',
                    template='plotly_dark'
                )
                st.plotly_chart(fig_sources, use_container_width=True)
        
        with tab3:
            # Source statistics and metadata
            st.write("**Source Statistics**")
            
            stats_data = []
            for source in web_df['source'].unique():
                source_data = web_df[web_df['source'] == source]
                stats_data.append({
                    'Source': source,
                    'Count': len(source_data),
                    'First Fetched': source_data['date_fetched'].min(),
                    'Last Fetched': source_data['date_fetched'].max()
                })
            
            stats_df = pd.DataFrame(stats_data)
            st.dataframe(stats_df, hide_index=True, use_container_width=True)
            
            # Export option
            if st.button("📥 Export Web Data as CSV", key="export_web_data"):
                csv = web_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"web_scrape_{web_artist}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    # Economic Impact Details
    with st.expander("📊 Economic Impact Analysis"):
        impact_df = pd.DataFrame([{
            'Metric': 'Direct Streaming Revenue',
            'Value': format_ngn(impact_metrics['direct_revenue_ngn'])
        }, {
            'Metric': 'Indirect Revenue (Est.)',
            'Value': format_ngn(impact_metrics['indirect_revenue_ngn'])
        }, {
            'Metric': 'Cultural Export Value',
            'Value': format_ngn(impact_metrics['cultural_export_value_ngn'])
        }, {
            'Metric': 'Total Economic Impact',
            'Value': format_ngn(impact_metrics['total_economic_impact_ngn'])
        }])
        st.table(impact_df)

if __name__ == "__main__":
    main()