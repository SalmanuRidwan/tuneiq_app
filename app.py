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
    /* Root neon theme variables */
    :root{
        --bg-1: #05030a;
        --bg-2: #0b1020;
        --neon-1: #00FFC2;
        --neon-2: #00A3FF;
        --accent: #9B59FF;
        --gold: #FFD700;
        --silver: #C0C0C0;
        --glass: rgba(255,255,255,0.04);
        --muted: #98ffe0;
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
        filter: drop-shadow(0 0 10px rgba(0,255,194,0.3));
    }
    
    .logo-text {
        display: flex;
        flex-direction: column;
    }
    
    .logo-title {
        font-size: 2.5rem !important;
        font-weight: 800;
        margin: 0 !important;
        background: linear-gradient(90deg, var(--gold), var(--silver));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        text-shadow: 0 0 20px rgba(255,215,0,0.2);
    }
    
    .logo-tagline {
        font-size: 1.1rem;
        color: var(--muted);
        margin-top: 5px;
        font-weight: 400;
    }

    /* Animated gradient background */
    html, body, .stApp {
        height: 100%;
        background: radial-gradient(circle at 10% 10%, rgba(0,163,255,0.06), transparent 10%),
                                radial-gradient(circle at 90% 90%, rgba(155,89,255,0.03), transparent 10%),
                                linear-gradient(180deg, var(--bg-1), var(--bg-2));
        color: var(--muted) !important;
        font-family: 'Inter', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
    }

    /* Animated gradient title */
    h1 {
        font-size: 2.2rem !important;
        margin: 0 !important;
        font-weight: 800;
        background: linear-gradient(90deg, var(--neon-1), var(--neon-2), var(--accent));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        animation: hue 6s linear infinite;
        text-align: right !important;
    }

    @keyframes hue{ 0%{filter: hue-rotate(0deg);}50%{filter: hue-rotate(40deg);}100%{filter: hue-rotate(0deg);} }

    /* Glass KPI cards */
    .stMetric, .stMetric > div {
        background: linear-gradient(135deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)) !important;
        border: 1px solid rgba(0,255,194,0.12) !important;
        box-shadow: 0 8px 30px rgba(0,0,0,0.6) inset, 0 8px 24px rgba(0,255,194,0.04);
        border-radius: 12px !important;
        padding: 10px !important;
        color: var(--muted) !important;
    }

    /* Bright neon values for metric numbers */
    .stMetric .value, .stMetric .stMetricValue {
        color: var(--neon-1) !important;
        font-weight: 800 !important;
        text-shadow: 0 6px 18px rgba(0,255,194,0.12);
    }

    /* Make buttons look like neon pills */
    .stButton>button {
        background: linear-gradient(90deg, rgba(0,255,194,0.12), rgba(0,163,255,0.12));
        color: var(--neon-1) !important;
        border: 1px solid rgba(0,255,194,0.18) !important;
        padding: 10px 14px !important;
        border-radius: 999px !important;
        box-shadow: 0 8px 30px rgba(0,163,255,0.06);
        transition: transform 0.12s ease, box-shadow 0.12s ease;
    }
    .stButton>button:hover{ transform: translateY(-2px); box-shadow: 0 16px 46px rgba(0,163,255,0.12); }

    /* Sidebar styling */
    .css-1d391kg .css-1lcbmhc { background: linear-gradient(180deg, rgba(11,16,32,0.6), rgba(8,10,20,0.6)); }
    .sidebar .stMarkdown, .sidebar .stTextInput { color: var(--muted) !important; }

    /* Glass panels for main content blocks */
    .element-container, .block-container .stExpander {
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        border: 1px solid rgba(155,89,255,0.04);
        border-radius: 10px;
        padding: 12px;
    }

    /* Tables */
    .stTable td, .stTable th { color: var(--muted) !important; }

    /* Footer */
    footer { opacity: 0.8; color: #7FFFD4 !important; }

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
                artist_name=st.session_state.get('artist_name')
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
            f"{alert_count} Regions",
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
        border: 1px solid rgba(255,215,0,0.18) !important;
        border-radius: 12px !important;
        padding: 15px 20px !important;
        color: var(--gold) !important;
        background: linear-gradient(135deg, 
            rgba(0,255,194,0.08), 
            rgba(0,163,255,0.08)
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
            rgba(255,215,0,0.1),
            transparent
        );
        transform: rotate(45deg);
        transition: all 0.3s ease;
    }

    /* Button hover effect */
    div[data-testid="stHorizontalBlock"] > div button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(255,215,0,0.15) !important;
        background: linear-gradient(135deg, 
            rgba(0,255,194,0.12), 
            rgba(0,163,255,0.12)
        ) !important;
    }
    
    div[data-testid="stHorizontalBlock"] > div button:hover::after {
        transform: rotate(45deg) translate(150%, 150%);
    }

    /* Selected button state */
    div[data-testid="stHorizontalBlock"] > div button.selected {
        background: linear-gradient(135deg, 
            rgba(0,255,194,0.2), 
            rgba(0,163,255,0.2)
        ) !important;
        box-shadow: 
            0 8px 25px rgba(0,255,194,0.2),
            0 0 0 1px rgba(0,255,194,0.4) !important;
        transform: translateY(-2px);
    }

    /* Header section container */
    .header-section {
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        background: linear-gradient(135deg,
            rgba(0,255,194,0.05),
            rgba(0,163,255,0.05)
        );
        border: 1px solid rgba(0,255,194,0.1);
        backdrop-filter: blur(10px);
    }

    /* Section title */
    .section-title {
        color: var(--neon-1);
        font-weight: 600;
        font-size: 1.2em;
        margin-bottom: 15px;
        text-shadow: 0 0 10px rgba(0,255,194,0.3);
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
  color:#00FFC2 !important;
  display:inline-block !important;
  vertical-align:middle !important;
}}
.logo-tagline {{ margin-top:4px !important; font-size:1.1em !important; color:#ccc !important; }}
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
            help="Set time period and region filters",
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
                
            st.markdown('</div>', unsafe_allow_html=True)
    
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

            # Artist selection (applies to live fetch)
            artist_input = st.selectbox(
                "Select Artist",
                options=NIGERIAN_ARTISTS,
                index=NIGERIAN_ARTISTS.index('Burna Boy') if 'Burna Boy' in NIGERIAN_ARTISTS else 0,
                help="Choose a Nigerian artist to analyze"
            )
            if artist_input:
                st.session_state['artist_name'] = artist_input

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
                selected_artist = st.session_state.get('artist_name')
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
    artist_name_display = st.session_state.get('artist_name', 'Burna Boy')  # Default to Burna Boy if not set
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
                selected_months = st.multiselect(
                    "Time Period",
                    months,
                    default=st.session_state.selected_months,
                    key="header_months"
                )
                st.session_state.selected_months = selected_months
            with filter_cols[1]:
                header_country = st.selectbox(
                    "Region",
                    country_options,
                    key="header_country"
                )
                
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Sidebar mirror of filters (synced with header)
    # st.sidebar.header("Filters & Drilldown")
    selected_platforms = header_platforms  # Use header selection
    selected_months = header_months  # Use header selection
    drill_country = header_country  # Use header selection
    
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
    
    # Economic Impact Details
    with st.expander("Economic Impact Analysis"):
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