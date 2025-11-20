"""
TuneIQ Solution - Making Nigeria's music economy visible.
Streamlit dashboard for music streaming analytics and economic impact analysis.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Optional
import json
import base64
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
display_economic_impact_section = None

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
    ei_mod = importlib.import_module("tuneiq_app.economic_impact")
    display_economic_impact_section = getattr(ei_mod, "display_economic_impact_section")
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
        ei_mod = importlib.import_module("economic_impact")
        display_economic_impact_section = getattr(ei_mod, "display_economic_impact_section")
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
    /* ============================================
   TUNEIQ MODERN UI - ENHANCED CSS
   ============================================ */

/* ============================================
   1. ROOT VARIABLES & THEME
   ============================================ */
:root {
    /* Colors */
    --primary: #0EA5A4;
    --primary-light: #10bfbd;
    --primary-dark: #0c8483;
    --secondary: #7C3AED;
    --accent: #F59E0B;
    --bg-primary: #F4F7F5;
    --bg-secondary: #FFFFFF;
    --text-primary: #1F213A;
    --text-secondary: #64748B;
    --text-muted: #94A3B8;
    --border: rgba(14, 165, 164, 0.15);
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    --shadow-glow: 0 0 20px rgba(14, 165, 164, 0.15);
    
    /* Spacing Scale */
    --space-1: 0.25rem;
    --space-2: 0.5rem;
    --space-3: 0.75rem;
    --space-4: 1rem;
    --space-5: 1.25rem;
    --space-6: 1.5rem;
    --space-8: 2rem;
    --space-10: 2.5rem;
    --space-12: 3rem;
    --space-16: 4rem;
    
    /* Border Radius */
    --radius-sm: 0.375rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
    --radius-xl: 1rem;
    --radius-2xl: 1.5rem;
    --radius-full: 9999px;
    
    /* Typography */
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-weight-normal: 400;
    --font-weight-medium: 500;
    --font-weight-semibold: 600;
    --font-weight-bold: 700;
    --font-weight-extrabold: 800;
    
    /* Transitions */
    --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* ============================================
   2. BASE STYLES & LAYOUT
   ============================================ */
html, body, .stApp {
    font-family: var(--font-sans);
    background: linear-gradient(135deg, #F4F7F5 0%, #E8F3F1 100%);
    color: var(--text-primary);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Main container with better padding */
.main .block-container {
    padding-top: var(--space-8) !important;
    padding-bottom: var(--space-16) !important;
    max-width: 1400px !important;
}

/* ============================================
   3. TYPOGRAPHY HIERARCHY'
   ============================================ */
h1, h2, h3, h4, h5, h6 {
    font-weight: var(--font-weight-bold);
    letter-spacing: -0.02em;
    line-height: 1.2;
}

h1 {
    font-size: 2.5rem !important;
    font-weight: var(--font-weight-extrabold) !important;
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: var(--space-6) !important;
}

h2 {
    font-size: 1.875rem !important;
    color: var(--text-primary);
    margin-bottom: var(--space-4) !important;
}

h3 {
    font-size: 1.5rem !important;
    color: var(--text-primary);
    margin-bottom: var(--space-3) !important;
}

/* ============================================
   4. LOGO & HEADER SECTION
   ============================================ */
.logo-container {
    display: flex !important;
    align-items: center !important;
    gap: var(--space-4) !important;
    padding: var(--space-6) 0 !important;
    margin-bottom: var(--space-8) !important;
    position: relative;
}

.logo-container::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, 
        transparent 0%, 
        var(--border) 20%, 
        var(--border) 80%, 
        transparent 100%
    );
}

.logo-container img {
    width: 80px !important;
    height: 80px !important;
    object-fit: contain !important;
    filter: drop-shadow(0 4px 12px rgba(14, 165, 164, 0.2));
    transition: transform var(--transition-base);
}

.logo-container:hover img {
    transform: scale(1.05);
}

.logo-title {
    font-size: 2.25rem !important;
    font-weight: var(--font-weight-extrabold) !important;
    background: linear-gradient(135deg, var(--primary) 0%, var(--text-primary) 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent !important;
    margin: 0 !important;
    line-height: 1 !important;
}

.logo-tagline {
    font-size: 0.95rem !important;
    color: var(--text-secondary) !important;
    font-weight: var(--font-weight-medium);
    margin-top: var(--space-2) !important;
}

/* ============================================
   5. MODERN CARD SYSTEM
   ============================================ */
.modern-card {
    background: var(--bg-secondary);
    border-radius: var(--radius-xl);
    padding: var(--space-6);
    box-shadow: var(--shadow-md);
    border: 1px solid var(--border);
    transition: all var(--transition-base);
    position: relative;
    overflow: hidden;
}

.modern-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--primary), var(--secondary));
    opacity: 0;
    transition: opacity var(--transition-base);
}

.modern-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-xl), var(--shadow-glow);
}

.modern-card:hover::before {
    opacity: 1;
}

/* ============================================
   6. ENHANCED METRIC CARDS
   ============================================ */
.stMetric {
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.95) 0%, 
        rgba(255, 255, 255, 0.85) 100%
    ) !important;
    backdrop-filter: blur(20px);
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-xl) !important;
    padding: var(--space-6) !important;
    box-shadow: var(--shadow-md) !important;
    transition: all var(--transition-base) !important;
    position: relative;
    overflow: hidden;
}

/* Metric card accent bar */
.stMetric::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, var(--primary), var(--accent));
}

.stMetric:hover {
    transform: translateY(-4px) scale(1.02);
    box-shadow: var(--shadow-xl), var(--shadow-glow) !important;
    border-color: var(--primary) !important;
}

/* Metric label styling */
.stMetric label {
    font-size: 0.875rem !important;
    font-weight: var(--font-weight-semibold) !important;
    color: var(--text-secondary) !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: var(--space-2) !important;
}

/* Metric value styling */
.stMetric [data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: var(--font-weight-extrabold) !important;
    color: var(--primary) !important;
    line-height: 1.2 !important;
    text-shadow: 0 2px 8px rgba(14, 165, 164, 0.2);
}

/* Metric delta styling */
.stMetric [data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
    font-weight: var(--font-weight-medium) !important;
    color: var(--text-muted) !important;
    margin-top: var(--space-2) !important;
}

/* ============================================
   7. BUTTON SYSTEM
   ============================================ */
.stButton > button {
    background: linear-gradient(135deg, 
        rgba(14, 165, 164, 0.1) 0%, 
        rgba(14, 165, 164, 0.05) 100%
    ) !important;
    color: var(--primary) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    padding: var(--space-3) var(--space-6) !important;
    font-weight: var(--font-weight-semibold) !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.01em;
    transition: all var(--transition-base) !important;
    box-shadow: var(--shadow-sm) !important;
    position: relative;
    overflow: hidden;
}

/* Button shine effect */
.stButton > button::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.5);
    transform: translate(-50%, -50%);
    transition: width var(--transition-slow), height var(--transition-slow);
}

.stButton > button:hover::after {
    width: 300px;
    height: 300px;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg) !important;
    border-color: var(--primary) !important;
    background: linear-gradient(135deg, 
        rgba(14, 165, 164, 0.15) 0%, 
        rgba(14, 165, 164, 0.1) 100%
    ) !important;
}

.stButton > button:active {
    transform: translateY(0);
}

/* Primary button variant */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
    color: white !important;
    border: none !important;
}

.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, var(--primary-light), var(--primary)) !important;
    box-shadow: 0 8px 24px rgba(14, 165, 164, 0.4) !important;
}

/* ============================================
   8. SECTION CONTAINERS
   ============================================ */
.header-section {
    background: linear-gradient(135deg, 
        rgba(255, 255, 255, 0.9) 0%, 
        rgba(255, 255, 255, 0.7) 100%
    );
    backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: var(--radius-2xl);
    padding: var(--space-8);
    margin: var(--space-6) 0;
    box-shadow: var(--shadow-md);
    position: relative;
}

.section-title {
    font-size: 1.25rem !important;
    font-weight: var(--font-weight-bold) !important;
    color: var(--primary) !important;
    margin-bottom: var(--space-4) !important;
    display: flex;
    align-items: center;
    gap: var(--space-2);
}

.section-title::before {
    content: '';
    width: 4px;
    height: 24px;
    background: linear-gradient(180deg, var(--primary), var(--secondary));
    border-radius: var(--radius-full);
}

/* ============================================
   9. DATA VISUALIZATION ENHANCEMENTS
   ============================================ */
/* Chart container */
.stPlotlyChart {
    background: var(--bg-secondary);
    border-radius: var(--radius-xl);
    padding: var(--space-4);
    box-shadow: var(--shadow-md);
    border: 1px solid var(--border);
    margin: var(--space-4) 0;
}

/* Dataframe styling */
.stDataFrame {
    border-radius: var(--radius-lg) !important;
    overflow: hidden;
    box-shadow: var(--shadow-md);
    border: 1px solid var(--border) !important;
}

.stDataFrame table {
    font-size: 0.9rem;
}

.stDataFrame thead tr th {
    background: linear-gradient(135deg, 
        rgba(14, 165, 164, 0.1) 0%, 
        rgba(14, 165, 164, 0.05) 100%
    ) !important;
    color: var(--text-primary) !important;
    font-weight: var(--font-weight-semibold) !important;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
    padding: var(--space-4) !important;
    border-bottom: 2px solid var(--border) !important;
}

.stDataFrame tbody tr {
    transition: background-color var(--transition-fast);
}

.stDataFrame tbody tr:hover {
    background: rgba(14, 165, 164, 0.03) !important;
}

.stDataFrame tbody tr td {
    padding: var(--space-3) var(--space-4) !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05) !important;
}

/* ============================================
   10. EXPANDER STYLING
   ============================================ */
.stExpander {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: var(--shadow-sm) !important;
    margin: var(--space-4) 0 !important;
    overflow: hidden;
}

.stExpander summary {
    padding: var(--space-4) !important;
    font-weight: var(--font-weight-semibold) !important;
    color: var(--text-primary) !important;
    background: linear-gradient(135deg, 
        rgba(14, 165, 164, 0.05) 0%, 
        transparent 100%
    );
    transition: all var(--transition-base);
}

.stExpander summary:hover {
    background: linear-gradient(135deg, 
        rgba(14, 165, 164, 0.1) 0%, 
        rgba(14, 165, 164, 0.05) 100%
    );
}

.stExpander[open] summary {
    border-bottom: 1px solid var(--border);
}

/* ============================================
   11. INPUT FIELDS
   ============================================ */
.stTextInput > div > div > input,
.stSelectbox > div > div > select,
.stMultiSelect > div > div > div {
    border-radius: var(--radius-md) !important;
    border: 1.5px solid var(--border) !important;
    padding: var(--space-3) !important;
    font-size: 0.95rem !important;
    transition: all var(--transition-base) !important;
    background: var(--bg-secondary) !important;
}

.stTextInput > div > div > input:focus,
.stSelectbox > div > div > select:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px rgba(14, 165, 164, 0.1) !important;
    outline: none !important;
}

/* ============================================
   12. TAB STYLING
   ============================================ */
.stTabs [data-baseweb="tab-list"] {
    gap: var(--space-2);
    border-bottom: 2px solid var(--border);
    padding-bottom: 0;
}

.stTabs [data-baseweb="tab"] {
    padding: var(--space-3) var(--space-6) !important;
    border-radius: var(--radius-md) var(--radius-md) 0 0 !important;
    color: var(--text-secondary) !important;
    font-weight: var(--font-weight-medium) !important;
    transition: all var(--transition-base) !important;
    border: none !important;
    background: transparent !important;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(14, 165, 164, 0.05) !important;
    color: var(--primary) !important;
}

.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--primary) !important;
    font-weight: var(--font-weight-bold) !important;
    background: linear-gradient(135deg, 
        rgba(14, 165, 164, 0.1) 0%, 
        rgba(14, 165, 164, 0.05) 100%
    ) !important;
    border-bottom: 3px solid var(--primary) !important;
}

/* ============================================
   13. BADGES & PILLS
   ============================================ */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    padding: var(--space-2) var(--space-4);
    border-radius: var(--radius-full);
    font-size: 0.75rem;
    font-weight: var(--font-weight-semibold);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.status-badge.live {
    background: rgba(239, 68, 68, 0.1);
    color: #DC2626;
}

.status-badge.sample {
    background: rgba(34, 197, 94, 0.1);
    color: #16A34A;
}

/* ============================================
   14. LOADING STATES
   ============================================ */
.stSpinner > div {
    border-color: var(--primary) !important;
    border-right-color: transparent !important;
}

/* ============================================
   15. SCROLLBAR STYLING
   ============================================ */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: rgba(14, 165, 164, 0.05);
    border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb {
    background: rgba(14, 165, 164, 0.3);
    border-radius: var(--radius-full);
    transition: background var(--transition-base);
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(14, 165, 164, 0.5);
}

/* ============================================
   16. RESPONSIVE ADJUSTMENTS
   ============================================ */
@media (max-width: 768px) {
    .main .block-container {
        padding-left: var(--space-4) !important;
        padding-right: var(--space-4) !important;
    }
    
    h1 {
        font-size: 2rem !important;
    }
    
    .logo-title {
        font-size: 1.75rem !important;
    }
    
    .header-section {
        padding: var(--space-6);
    }
}

/* ============================================
   17. ANIMATIONS
   ============================================ */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideIn {
    from {
        transform: translateX(-20px);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.8;
    }
}

/* Apply animations */
.stMetric {
    animation: fadeIn var(--transition-slow) ease-out;
}

.modern-card {
    animation: slideIn var(--transition-slow) ease-out;
}

/* ============================================
   18. UTILITY CLASSES
   ============================================ */
.glass-effect {
    background: rgba(255, 255, 255, 0.8) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
}

.gradient-border {
    position: relative;
    border: 2px solid transparent;
    background-clip: padding-box;
}

.gradient-border::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    padding: 2px;
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
}

.shadow-glow-primary {
    box-shadow: 0 0 30px rgba(14, 165, 164, 0.3) !important;
}

/* ============================================
   MODERN CARD STYLING FOR DASHBOARD
   ============================================ */
.main-card {
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    padding: 20px;
    margin-bottom: 25px;
    border: 1px solid rgba(14, 165, 164, 0.1);
}

.kpi-card {
    background: white;
    border-radius: 16px;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
    padding: 20px;
    text-align: center;
    border: 1px solid rgba(14, 165, 164, 0.1);
    transition: all 0.3s ease;
}

.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(14, 165, 164, 0.15);
}

.kpi-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: #0EA5A4;
    margin: 10px 0;
}

.kpi-label {
    font-size: 0.9rem;
    color: #64748B;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.kpi-change {
    font-size: 0.85rem;
    margin-top: 8px;
    font-weight: 600;
}

/* Sidebar styling */
.sidebar-nav {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 20px 0;
}

.sidebar-nav button {
    width: 100%;
    padding: 12px 16px;
    border-radius: 10px;
    border: 1px solid rgba(14, 165, 164, 0.2);
    background: white;
    color: #068D9D;
    font-weight: 500;
    transition: all 0.3s ease;
    cursor: pointer;
}

.sidebar-nav button:hover {
    background: rgba(14, 165, 164, 0.08);
    box-shadow: 0 2px 8px rgba(14, 165, 164, 0.1);
}

.section-header {
    font-size: 1.3rem;
    font-weight: 700;
    color: #1F213A;
    margin: 30px 0 15px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* ============================================
   CIRCULAR PROGRESS RINGS
   ============================================ */
.progress-ring-container {
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    width: 140px;
    height: 140px;
    margin: 0 auto;
}

.progress-ring {
    width: 140px;
    height: 140px;
}

.progress-ring-circle {
    transition: stroke-dashoffset 0.35s;
    transform: rotate(-90deg);
    transform-origin: 50% 50%;
}

.progress-ring-background {
    fill: none;
    stroke: #E5E7EB;
    stroke-width: 8;
}

.progress-ring-progress {
    fill: none;
    stroke-width: 8;
    stroke-linecap: round;
}

.progress-ring-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    font-weight: 700;
    font-size: 1.8rem;
    color: #0EA5A4;
}

.progress-ring-label {
    position: absolute;
    bottom: -30px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 0.85rem;
    color: #64748B;
    white-space: nowrap;
}

/* ============================================
   ENHANCED CARD STYLING WITH HOVER & GRADIENTS
   ============================================ */
.metric-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    border: 1px solid rgba(14, 165, 164, 0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #0EA5A4, #10bfbd);
}

.metric-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.chart-card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(14, 165, 164, 0.1);
    margin-bottom: 20px;
    transition: all 0.3s ease;
}

.chart-card:hover {
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

/* ============================================
   STAT DISPLAY
   ============================================ */
.stat-label {
    font-size: 0.9rem;
    color: #64748B;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}

.stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: #0EA5A4;
    margin: 12px 0;
}

.stat-change {
    font-size: 0.85rem;
    color: #10b981;
    font-weight: 600;
}

/* ============================================
   ANIMATION EFFECTS
   ============================================ */
@keyframes slideInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

.animate-in {
    animation: slideInUp 0.6s ease-out;
}

</style>
""", unsafe_allow_html=True)


def render_table_toolbar(title: str, df: Optional[pd.DataFrame] = None, file_name: str = "data.csv") -> None:
    """Render a very small toolbar (icon-only) with JSON/CSV downloads and fullscreen view.

    Fullscreen uses an expander at the top of the page to maximize available space.
    """
    import hashlib

    # Use a deterministic id based on title+file_name so session-state keys
    # persist across Streamlit reruns (avoids a new random id each render)
    uid = hashlib.md5(f"{title}_{file_name}".encode()).hexdigest()[:8]

    # Title + buttons layout
    col_title, col_buttons = st.columns([2, 1])

    with col_title:
        st.markdown(f"<h4 style='margin: 0; padding: 4px 0; color: #0f172a; font-size:0.95rem;'>{title}</h4>", unsafe_allow_html=True)

    with col_buttons:
        # Wrap toolbar in a scoped div so CSS is targeted and doesn't affect other buttons
        st.markdown(f"<div class='tiny-toolbar-{uid}'>", unsafe_allow_html=True)

        # Tiny toolbar CSS (scoped)
        st.markdown(f"""
        <style>
        .tiny-toolbar-{uid} .stButton>button {{
            min-width: 18px !important;
            height: 18px !important;
            padding: 0 2px !important;
            border-radius: 4px !important;
            font-size: 10px !important;
            line-height: 0.8 !important;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }}
        </style>
        """, unsafe_allow_html=True)

        btn_cols = st.columns([1, 1, 1], gap='small')

        # JSON download
        with btn_cols[0]:
            if df is not None:
                json_str = df.to_json(orient='records', indent=2)
                st.download_button(label="💾", data=json_str, file_name=file_name.replace('.csv', '.json'), mime="application/json", key=f"json_{uid}", help="Download JSON")
            else:
                st.button("💾", key=f"save_disabled_{uid}", disabled=True)

        # CSV download
        with btn_cols[1]:
            if df is not None:
                csv_str = df.to_csv(index=False)
                st.download_button(label="⬇️", data=csv_str, file_name=file_name, mime="text/csv", key=f"csv_{uid}", help="Download CSV")
            else:
                st.button("⬇️", key=f"csv_disabled_{uid}", disabled=True)

        # Fullscreen toggle (sets session state)
        with btn_cols[2]:
            clicked_full = st.button("⛶", key=f"fullscreen_{uid}", help="Expand to fullscreen")
            if clicked_full and df is not None:
                st.session_state[f"toolbar_fullscreen_{uid}"] = True

        st.markdown("</div>", unsafe_allow_html=True)

    # If fullscreen flag set, render a large expander-based fullscreen view
    fs_key = f"toolbar_fullscreen_{uid}"
    if st.session_state.get(fs_key):
        # Use an expander that's expanded by default to create a large viewing area
        with st.expander(f"⛶ Fullscreen — {title}", expanded=True):
            col_close, col_spacer = st.columns([1, 9])
            with col_close:
                if st.button("✕ Close", key=f"close_fullscreen_{uid}"):
                    st.session_state[fs_key] = False
                    st.rerun()
            
            st.divider()
            
            # Render the dataframe in fullscreen (use large height)
            if df is not None:
                st.dataframe(df, width='stretch', height=600, key=f"fullscreen_df_{uid}")


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
    """Render enhanced KPI metric cards with modern design."""
    # Add enhanced CSS for KPI cards
    kpi_css = """
    <style>
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 24px;
        margin: 30px 0 40px 0;
        padding: 0;
        width: 100%;
    }
    
    .kpi-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-left: 6px solid;
        border-radius: 20px;
        padding: 32px 28px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06), 0 0 1px rgba(0, 0, 0, 0.05);
        transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
        position: relative;
        overflow: hidden;
        border-top: 1px solid rgba(255, 255, 255, 0.8);
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 100px;
        height: 100px;
        background: radial-gradient(circle, rgba(14, 165, 164, 0.05) 0%, transparent 70%);
        border-radius: 50%;
        transform: translate(30%, -30%);
    }
    
    .kpi-card:hover {
        transform: translateY(-12px) translateZ(0);
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.12), 0 0 1px rgba(0, 0, 0, 0.05);
    }
    
    .kpi-card.streams { border-left-color: #0EA5A4; }
    .kpi-card.streams:hover { border-left-color: #10bfbd; }
    
    .kpi-card.revenue { border-left-color: #10b981; }
    .kpi-card.revenue:hover { border-left-color: #059669; }
    
    .kpi-card.reach { border-left-color: #F59E0B; }
    .kpi-card.reach:hover { border-left-color: #d97706; }
    
    .kpi-card.alerts { border-left-color: #EF4444; }
    .kpi-card.alerts:hover { border-left-color: #dc2626; }
    
    .kpi-icon {
        font-size: 2.8rem;
        margin-bottom: 16px;
        opacity: 0.95;
        display: block;
        transition: transform 0.3s ease;
    }
    
    .kpi-card:hover .kpi-icon {
        transform: scale(1.1);
    }
    
    .kpi-label {
        font-size: 0.8rem;
        color: #64748B;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 14px;
    }
    
    .kpi-value {
        font-size: 2.4rem;
        font-weight: 800;
        color: #1F213A;
        margin-bottom: 10px;
        line-height: 1.2;
    }
    
    .kpi-sublabel {
        font-size: 0.85rem;
        color: #94A3B8;
        font-weight: 500;
        line-height: 1.4;
    }
    
    .kpi-trend {
        font-size: 0.8rem;
        margin-top: 16px;
        padding-top: 14px;
        border-top: 1px solid rgba(14, 165, 164, 0.15);
        color: #10b981;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .kpi-card:hover .kpi-trend {
        color: #059669;
    }
    </style>
    """
    
    st.markdown(kpi_css, unsafe_allow_html=True)
    
    # Calculate metrics
    total_streams = df['streams'].sum()
    direct_revenue = impact_metrics['direct_revenue_ngn']
    indirect_revenue = impact_metrics['indirect_revenue_ngn']
    country_count = len(df['country'].unique())
    underpaid = detect_underpayment(df)
    alert_count = len(underpaid)
    
    # Format currency
    def fmt_currency(val):
        if val >= 1_000_000:
            return f"₦{val/1_000_000:.1f}M"
        elif val >= 1_000:
            return f"₦{val/1_000:.0f}K"
        return f"₦{val:.0f}"
    
    # Create KPI cards HTML with proper rendering
    kpi_html = f"""<div class="kpi-container"><div class="kpi-card streams"><div class="kpi-icon">🎵</div><div class="kpi-label">Total Streams</div><div class="kpi-value">{total_streams:,}</div><div class="kpi-sublabel">Across All Platforms</div><div class="kpi-trend">↗️ All-time total</div></div><div class="kpi-card revenue"><div class="kpi-icon">💰</div><div class="kpi-label">Est. Revenue</div><div class="kpi-value">{fmt_currency(direct_revenue)}</div><div class="kpi-sublabel">Direct Revenue</div><div class="kpi-trend">+ {fmt_currency(indirect_revenue)} indirect</div></div><div class="kpi-card reach"><div class="kpi-icon">🌍</div><div class="kpi-label">Global Reach</div><div class="kpi-value">{country_count}</div><div class="kpi-sublabel">Countries & Territories</div><div class="kpi-trend">📈 Cultural Export</div></div><div class="kpi-card alerts"><div class="kpi-icon">⚠️</div><div class="kpi-label">Alerts</div><div class="kpi-value">{alert_count}</div><div class="kpi-sublabel">Underpayment Cases</div><div class="kpi-trend">🔍 Needs Investigation</div></div></div>"""
    
    st.markdown(kpi_html, unsafe_allow_html=True)

# def render_charts(df: pd.DataFrame, selected_platforms=None):
#     """Render main dashboard visualizations."""
#     # Filter data based on selected platforms
#     if selected_platforms:
#         df = df[df['platform'].isin(selected_platforms)]
    
#     # If no data after filtering, show message and return
#     if df.empty:
#         st.warning("No data available for the selected platforms. Please select at least one platform.")
#         return
    
#     # Add enhanced chart styling
#     chart_css = """
#     <style>
#     .chart-section {
#         margin: 40px 0 20px 0;
#     }
    
#     .chart-title {
#         font-size: 1.25rem;
#         font-weight: 700;
#         color: #1F213A;
#         margin-bottom: 20px;
#         padding-bottom: 12px;
#         border-bottom: 3px solid #0EA5A4;
#         display: inline-block;
#     }
    
#     .chart-wrapper {
#         background: white;
#         border-radius: 16px;
#         padding: 20px;
#         margin: 20px 0;
#         box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
#         border: 1px solid rgba(14, 165, 164, 0.1);
#         transition: all 0.3s ease;
#     }
    
#     .chart-wrapper:hover {
#         box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
#     }
#     </style>
#     """
#     st.markdown(chart_css, unsafe_allow_html=True)
        
#     # Compute per-country impact and identify top-10 countries by impact
#     # Ensure expected_revenue_ngn exists (estimate_royalties called earlier in main)
#     country_impact = df.groupby('country').agg({
#         'streams': 'sum',
#         'expected_revenue_ngn': 'sum',
#         'actual_revenue_ngn': 'sum'
#     }).reset_index()
#     country_impact['revenue_gap'] = country_impact['expected_revenue_ngn'] - country_impact['actual_revenue_ngn']
#     # Define impact_value as expected revenue (proxy for economic impact)
#     country_impact['impact_value_ngn'] = country_impact['expected_revenue_ngn']
#     # Top 10 high impact countries
#     top10 = country_impact.sort_values('impact_value_ngn', ascending=False).head(10).copy()

#     # Global Streaming Distribution (choropleth colored by streams, with top-10 highlighted)
#     st.markdown('<div class="chart-section"><div class="chart-title">🌍 Global Streaming Distribution</div></div>', unsafe_allow_html=True)
#     st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
    
#     geo_data = country_impact.copy()
#     # Add a flag to indicate top10
#     geo_data['is_top10'] = geo_data['country'].isin(top10['country']).astype(int)

#     fig_map = px.choropleth(
#         geo_data,
#         locations='country',
#         locationmode='country names',
#         color='streams',
#         color_continuous_scale='Viridis',
#         template="plotly_white",
#         title=None,
#         hover_name='country',
#         hover_data={'streams': ':,'}
#     )
    
#     fig_map.update_layout(
#         height=500,
#         margin=dict(l=0, r=0, t=0, b=0),
#         font=dict(family="Inter, sans-serif", size=12),
#         geo=dict(
#             showland=True,
#             landcolor='#f0f0f0',
#             coastlinecolor='#e0e0e0',
#             oceancolor='#e8f4f8'
#         ),
#         coloraxis_colorbar=dict(title="Streams", thickness=15)
#     )

#     # Overlay top-10 markers to highlight them
#     try:
#         fig_scatter = px.scatter_geo(
#             top10,
#             locations='country',
#             locationmode='country names',
#             size='impact_value_ngn',
#             hover_name='country',
#             projection='natural earth'
#         )
#         # Add scatter traces to choropleth
#         for trace in fig_scatter.data:
#             fig_map.add_trace(trace)
#     except Exception:
#         # Fallback: ignore overlay if scatter fails due to location lookups
#         pass

#     st.plotly_chart(fig_map, use_container_width=True)
#     st.markdown('</div>', unsafe_allow_html=True)

#     # Streaming Trends and Revenue Analysis in equal columns
#     col1, col2 = st.columns(2)

#     with col1:
#         # Streams by Platform
#         st.markdown('<div class="chart-section"><div class="chart-title">📈 Streaming Trends</div></div>', unsafe_allow_html=True)
#         st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
#         platform_data = df.groupby('platform')['streams'].sum().reset_index()
        
#         # Add platform icons
#         platform_icons = {
#             'Spotify': '🎵',
#             'YouTube': '▶️',
#             'Apple Music': '🍎'
#         }
#         platform_data['platform_label'] = platform_data['platform'].apply(
#             lambda x: f"{platform_icons.get(x, '')} {x}"
#         )
        
#         fig_platform = px.bar(
#             platform_data,
#             x='platform_label',
#             y='streams',
#             color='platform',
#             template="plotly_white",
#             labels={'platform_label': 'Platform', 'streams': 'Total Streams'}
#         )
        
#         # Enhanced styling
#         fig_platform.update_traces(
#             marker_line_color='rgba(14, 165, 164, 0.3)',
#             marker_line_width=2,
#             opacity=0.85
#         )
        
#         # Update layout
#         fig_platform.update_layout(
#             showlegend=False,
#             height=400,
#             margin=dict(l=0, r=0, t=20, b=0),
#             font=dict(family="Inter, sans-serif", size=12),
#             xaxis_tickangle=-45,
#             hovermode='x unified'
#         )
        
#         st.plotly_chart(fig_platform, use_container_width=True)
        
#         # Add platform stats with export (modebar-style header)
#         with st.expander("Platform Statistics"):
#             stats_df = platform_data.copy()
#             total_streams = stats_df['streams'].sum()
#             stats_df['percentage'] = (stats_df['streams'] / total_streams * 100).round(2)

#             # Keep numeric values for export
#             stats_export = stats_df.copy()

#             # Format for display
#             stats_display = stats_df.copy()
#             stats_display['streams'] = stats_display['streams'].map(lambda x: f"{int(x):,}")
#             stats_display['percentage'] = stats_display['percentage'].map(lambda x: f"{x}%")

#             # Render toolbar above the table (camera, zoom area, zoom in/out, fullscreen, download)
#             render_table_toolbar(
#                 "📊 Platform Statistics",
#                 df=stats_export[['platform', 'streams', 'percentage']],
#                 file_name="platform_statistics.csv"
#             )

#             st.dataframe(
#                 stats_display[['platform', 'streams', 'percentage']],
#                 column_config={
#                     "platform": "Platform",
#                     "streams": "Total Streams",
#                     "percentage": "Market Share"
#                 },
#                 hide_index=True,
#                 use_container_width=True
#             )
#         st.markdown('</div>', unsafe_allow_html=True)

#     with col2:
#         # Revenue Gap Analysis - show top-10 high impact countries by default
#         st.markdown('<div class="chart-section"><div class="chart-title">💹 Revenue Gap Analysis</div></div>', unsafe_allow_html=True)
#         st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
        
#         show_revenue_details = st.checkbox("Show full country list", value=False)

#         if show_revenue_details:
#             display_df = country_impact.sort_values('revenue_gap', ascending=False)
#         else:
#             display_df = top10.copy()

#         # Keep original values for export
#         export_df = display_df.copy()
        
#         display_df = display_df.assign(
#             streams=display_df['streams'].map('{:,.0f}'.format),
#             expected_revenue_ngn=display_df['expected_revenue_ngn'].map(lambda x: f"₦{x:,.0f}"),
#             actual_revenue_ngn=display_df['actual_revenue_ngn'].map(lambda x: f"₦{x:,.0f}"),
#             revenue_gap=display_df['revenue_gap'].map(lambda x: f"₦{x:,.0f}")
#         )

#         # Toolbar above the table (replaces previous inline controls)
#         render_table_toolbar(
#             "💹 Revenue Gap Analysis",
#             df=export_df[['country', 'streams', 'expected_revenue_ngn', 'actual_revenue_ngn', 'revenue_gap']],
#             file_name="revenue_gap_analysis.csv"
#         )

#         st.dataframe(
#             display_df[['country', 'streams', 'expected_revenue_ngn', 'actual_revenue_ngn', 'revenue_gap']],
#             use_container_width=True,
#             hide_index=True,
#             column_config={
#                 'country': st.column_config.TextColumn('Country', width='small'),
#                 'streams': st.column_config.TextColumn('Streams', width='medium'),
#                 'expected_revenue_ngn': st.column_config.TextColumn('Expected Revenue', width='medium'),
#                 'actual_revenue_ngn': st.column_config.TextColumn('Actual Revenue', width='medium'),
#                 'revenue_gap': st.column_config.TextColumn('Gap', width='medium')
#             }
#         )
#         st.markdown('</div>', unsafe_allow_html=True)

#         render_revenue_gap_visualization(country_impact, top10)

def render_charts(df: pd.DataFrame, selected_platforms=None):
    """Render main dashboard visualizations."""
    # Filter data based on selected platforms
    if selected_platforms:
        df = df[df['platform'].isin(selected_platforms)]
    
    # If no data after filtering, show message and return
    if df.empty:
        st.warning("No data available for the selected platforms. Please select at least one platform.")
        return
    
    # Add enhanced chart styling
    chart_css = """
    <style>
    .chart-section {
        margin: 40px 0 20px 0;
    }
    
    .chart-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1F213A;
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 3px solid #0EA5A4;
        display: inline-block;
    }
    
    .chart-wrapper {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(14, 165, 164, 0.1);
        transition: all 0.3s ease;
    }
    
    .chart-wrapper:hover {
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
    }
    
    .mini-card {
        background: linear-gradient(135deg, rgba(14, 165, 164, 0.05), rgba(124, 58, 237, 0.02));
        border-radius: 12px;
        padding: 16px;
        border: 1px solid rgba(14, 165, 164, 0.15);
        height: 100%;
    }
    </style>
    """
    st.markdown(chart_css, unsafe_allow_html=True)
        
    # Compute per-country impact and identify top-10 countries by impact
    country_impact = df.groupby('country').agg({
        'streams': 'sum',
        'expected_revenue_ngn': 'sum',
        'actual_revenue_ngn': 'sum'
    }).reset_index()
    country_impact['revenue_gap'] = country_impact['expected_revenue_ngn'] - country_impact['actual_revenue_ngn']
    country_impact['impact_value_ngn'] = country_impact['expected_revenue_ngn']
    top10 = country_impact.sort_values('impact_value_ngn', ascending=False).head(10).copy()

    # Global Streaming Distribution (choropleth)
    st.markdown('<div class="chart-section"><div class="chart-title">🌍 Global Streaming Distribution</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
    
    geo_data = country_impact.copy()
    geo_data['is_top10'] = geo_data['country'].isin(top10['country']).astype(int)

    fig_map = px.choropleth(
        geo_data,
        locations='country',
        locationmode='country names',
        color='streams',
        color_continuous_scale='Viridis',
        template="plotly_white",
        title=None,
        hover_name='country',
        hover_data={'streams': ':,'}
    )
    
    fig_map.update_layout(
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        font=dict(family="Inter, sans-serif", size=12),
        geo=dict(
            showland=True,
            landcolor='#f0f0f0',
            coastlinecolor='#e0e0e0',
            oceancolor='#e8f4f8'
        ),
        coloraxis_colorbar=dict(title="Streams", thickness=15)
    )

    try:
        fig_scatter = px.scatter_geo(
            top10,
            locations='country',
            locationmode='country names',
            size='impact_value_ngn',
            hover_name='country',
            projection='natural earth'
        )
        for trace in fig_scatter.data:
            fig_map.add_trace(trace)
    except Exception:
        pass

    st.plotly_chart(fig_map, width='stretch')
    st.markdown('</div>', unsafe_allow_html=True)

    # ===== NEW LAYOUT: Streaming Trends 2 Column Grid =====
    st.markdown('<div class="chart-section"><div class="chart-title">📈 Streaming Trends</div></div>', unsafe_allow_html=True)
    
    streaming_col1, streaming_col2 = st.columns(2)
    
    with streaming_col1:
        st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
        st.markdown("#### Platform Distribution")
        
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
            template="plotly_white",
            labels={'platform_label': 'Platform', 'streams': 'Total Streams'},
            color_discrete_sequence=['#0EA5A4', '#F59E0B', '#7C3AED']
        )
        
        # Enhanced styling
        fig_platform.update_traces(
            marker_line_color='rgba(14, 165, 164, 0.3)',
            marker_line_width=2,
            opacity=0.85
        )
        
        # Update layout
        fig_platform.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=0, r=0, t=20, b=60),
            font=dict(family='Inter, sans-serif', size=11),
            xaxis_tickangle=-45,
            hovermode='x unified',
            plot_bgcolor='rgba(244, 247, 245, 0.5)',
            xaxis=dict(gridcolor='rgba(14, 165, 164, 0.1)'),
            yaxis=dict(gridcolor='rgba(14, 165, 164, 0.1)')
        )
        
        st.plotly_chart(fig_platform, width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)
    
    with streaming_col2:
        st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
        st.markdown("#### Platform Statistics")
        
        stats_df = platform_data.copy()
        total_streams = stats_df['streams'].sum()
        stats_df['percentage'] = (stats_df['streams'] / total_streams * 100).round(2)

        # Keep numeric values for export
        stats_export = stats_df.copy()

        # Format for display
        stats_display = stats_df.copy()
        stats_display['streams_formatted'] = stats_display['streams'].map(lambda x: f"{int(x):,}")
        stats_display['percentage_formatted'] = stats_display['percentage'].map(lambda x: f"{x}%")

        # Render toolbar above the table
        render_table_toolbar(
            "📊 Platform Statistics",
            df=stats_export[['platform', 'streams', 'percentage']],
            file_name="platform_statistics.csv"
        )

        st.dataframe(
            stats_display[['platform', 'streams_formatted', 'percentage_formatted']],
            column_config={
                "platform": st.column_config.TextColumn("Platform", width="medium"),
                "streams_formatted": st.column_config.TextColumn("Total Streams", width="medium"),
                "percentage_formatted": st.column_config.TextColumn("Market Share", width="small")
            },
            hide_index=True,
            width='stretch',
            height=350
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # ===== NEW LAYOUT: Revenue Gap Analysis Grid =====
    st.markdown('<div class="chart-section"><div class="chart-title">💰 Revenue Gap Analysis</div></div>', unsafe_allow_html=True)
    
    # Prepare visualization data
    viz_data = top10.copy()
    
    # Row 1: Detailed Table (Left) and Expected vs Actual Chart (Right)
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
        st.markdown("#### 📋 Revenue Gap Details")
        
        show_all = st.checkbox("Show all countries", value=False, key="show_all_revenue")
        
        display_data = country_impact if show_all else viz_data
        display_data = display_data.sort_values('revenue_gap', ascending=False).copy()
        
        # Keep original for export
        export_df = display_data.copy()
        
        # Format for display
        display_data['Gap %'] = ((display_data['revenue_gap'] / display_data['expected_revenue_ngn']) * 100).round(1)
        
        display_formatted = display_data.assign(
            expected_revenue_ngn=display_data['expected_revenue_ngn'].map(
                lambda x: f"₦{x/1e6:.1f}M" if x >= 1e6 else f"₦{x/1e3:.0f}K"
            ),
            actual_revenue_ngn=display_data['actual_revenue_ngn'].map(
                lambda x: f"₦{x/1e6:.1f}M" if x >= 1e6 else f"₦{x/1e3:.0f}K"
            ),
            revenue_gap=display_data['revenue_gap'].map(
                lambda x: f"₦{x/1e6:.1f}M" if x >= 1e6 else f"₦{x/1e3:.0f}K"
            ),
        )
        
        # Toolbar
        render_table_toolbar(
            "Revenue Gap Details",
            df=export_df[['country', 'expected_revenue_ngn', 'actual_revenue_ngn', 'revenue_gap']],
            file_name="revenue_gap_details.csv"
        )
        
        st.dataframe(
            display_formatted[['country', 'expected_revenue_ngn', 'actual_revenue_ngn', 'revenue_gap', 'Gap %']],
            column_config={
                "country": st.column_config.TextColumn("Country", width="small"),
                "expected_revenue_ngn": "Expected",
                "actual_revenue_ngn": "Actual",
                "revenue_gap": "Gap",
                "Gap %": st.column_config.NumberColumn("Gap %", format="%.1f%%")
            },
            hide_index=True,
            width='stretch',
            height=350
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with row1_col2:
        st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
        st.markdown("#### Expected vs Actual Revenue")
        
        # Create grouped bar chart
        fig_revenue = go.Figure()
        
        # Add Expected Revenue bars
        fig_revenue.add_trace(go.Bar(
            name='Expected Revenue',
            x=viz_data['country'],
            y=viz_data['expected_revenue_ngn'],
            marker=dict(
                color='#0EA5A4',
                line=dict(color='#0c8483', width=1)
            ),
            text=viz_data['expected_revenue_ngn'].apply(
                lambda x: f"₦{x/1e6:.1f}M" if x >= 1e6 else f"₦{x/1e3:.0f}K"
            ),
            textposition='outside',
            textfont=dict(size=9),
            hovertemplate='<b>%{x}</b><br>Expected: ₦%{y:,.0f}<extra></extra>'
        ))
        
        # Add Actual Revenue bars
        fig_revenue.add_trace(go.Bar(
            name='Actual Revenue',
            x=viz_data['country'],
            y=viz_data['actual_revenue_ngn'],
            marker=dict(
                color='#F59E0B',
                line=dict(color='#d97706', width=1)
            ),
            text=viz_data['actual_revenue_ngn'].apply(
                lambda x: f"₦{x/1e6:.1f}M" if x >= 1e6 else f"₦{x/1e3:.0f}K"
            ),
            textposition='outside',
            textfont=dict(size=9),
            hovertemplate='<b>%{x}</b><br>Actual: ₦%{y:,.0f}<extra></extra>'
        ))
        
        fig_revenue.update_layout(
            xaxis=dict(
                tickangle=-45,
                gridcolor='rgba(14, 165, 164, 0.1)',
                showgrid=True
            ),
            yaxis=dict(
                title='Revenue (NGN)',
                gridcolor='rgba(14, 165, 164, 0.1)',
                showgrid=True
            ),
            barmode='group',
            template='plotly_white',
            hovermode='x unified',
            plot_bgcolor='rgba(244, 247, 245, 0.5)',
            paper_bgcolor='white',
            font=dict(family='Inter, sans-serif', color='#1F213A', size=11),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),
            margin=dict(t=50, b=80, l=50, r=20),
            height=400
        )
        
        st.plotly_chart(fig_revenue, width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Row 2: Heatmap (Left) and Revenue Gap Chart (Right)
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
        st.markdown("#### 🔥 Revenue Comparison Heatmap")
        
        # Prepare heatmap data
        heatmap_data = viz_data[['country', 'expected_revenue_ngn', 
                                  'actual_revenue_ngn', 'revenue_gap']].copy()
        
        # Normalize for color scale
        heatmap_data['gap_percentage'] = (
            (heatmap_data['revenue_gap'] / heatmap_data['expected_revenue_ngn']) * 100
        )
        
        # Create heatmap
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=[heatmap_data['expected_revenue_ngn'], 
               heatmap_data['actual_revenue_ngn'],
               heatmap_data['revenue_gap']],
            x=heatmap_data['country'],
            y=['Expected Revenue', 'Actual Revenue', 'Revenue Gap'],
            colorscale=[
                [0, '#F59E0B'],      # Orange for low
                [0.5, '#0EA5A4'],    # Teal for medium
                [1, '#7C3AED']       # Purple for high
            ],
            text=[[f"₦{val/1e6:.1f}M" if val >= 1e6 else f"₦{val/1e3:.0f}K" 
                   for val in heatmap_data['expected_revenue_ngn']],
                  [f"₦{val/1e6:.1f}M" if val >= 1e6 else f"₦{val/1e3:.0f}K" 
                   for val in heatmap_data['actual_revenue_ngn']],
                  [f"₦{val/1e6:.1f}M" if val >= 1e6 else f"₦{val/1e3:.0f}K" 
                   for val in heatmap_data['revenue_gap']]],
            texttemplate='%{text}',
            textfont=dict(size=10, color='white'),
            hovertemplate='%{y}<br>%{x}: %{text}<extra></extra>',
            colorbar=dict(
                title='Amount (NGN)',
                thickness=15,
                len=0.7
            )
        ))
        
        fig_heatmap.update_layout(
            template='plotly_white',
            height=400,
            margin=dict(t=20, b=80, l=120, r=20),
            xaxis=dict(
                tickangle=-45,
                side='bottom'
            ),
            yaxis=dict(
                side='left'
            ),
            font=dict(family='Inter, sans-serif', size=11)
        )
        
        st.plotly_chart(fig_heatmap, width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)
    
    with row2_col2:
        st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
        st.markdown("#### Revenue Gap by Country")
        
        # Create gap bar chart
        waterfall_data = []
        for _, row in viz_data.iterrows():
            gap = row['expected_revenue_ngn'] - row['actual_revenue_ngn']
            waterfall_data.append({
                'country': row['country'],
                'gap': gap
            })
        
        waterfall_df = pd.DataFrame(waterfall_data)
        colors = ['#DC2626' if gap > 0 else '#16A34A' for gap in waterfall_df['gap']]
        
        fig_gap = go.Figure()
        
        fig_gap.add_trace(go.Bar(
            x=waterfall_df['country'],
            y=waterfall_df['gap'],
            marker=dict(
                color=colors,
                line=dict(color='rgba(0,0,0,0.3)', width=1)
            ),
            text=waterfall_df['gap'].apply(
                lambda x: f"₦{abs(x)/1e6:.1f}M" if abs(x) >= 1e6 else f"₦{abs(x)/1e3:.0f}K"
            ),
            textposition='outside',
            textfont=dict(size=9),
            hovertemplate='<b>%{x}</b><br>Gap: ₦%{y:,.0f}<extra></extra>',
            name='Revenue Gap'
        ))
        
        fig_gap.update_layout(
            xaxis=dict(
                tickangle=-45,
                gridcolor='rgba(14, 165, 164, 0.1)'
            ),
            yaxis=dict(
                title='Revenue Gap (NGN)',
                gridcolor='rgba(14, 165, 164, 0.1)',
                zeroline=True,
                zerolinecolor='rgba(14, 165, 164, 0.3)',
                zerolinewidth=2
            ),
            template='plotly_white',
            plot_bgcolor='rgba(244, 247, 245, 0.5)',
            paper_bgcolor='white',
            height=400,
            showlegend=False,
            margin=dict(t=20, b=80, l=50, r=20),
            font=dict(family='Inter, sans-serif', color='#1F213A', size=11)
        )
        
        st.plotly_chart(fig_gap, width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)

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

    # Header buttons styling for full-width alignment
    st.markdown("""
    <style>
    /* Full-width button container */
    .header-buttons-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-bottom: 20px;
        width: 100%;
    }
    
    /* Stretch buttons to fill grid cells */
    .header-buttons-container button {
        width: 100% !important;
        padding: 12px 20px !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header buttons in a single row with selection state
    header_cols = st.columns(2, gap="medium")
    
    # Initialize button states in session state if not present
    if 'active_section' not in st.session_state:
        st.session_state.active_section = None
    
    with header_cols[0]:
        if st.button(
            "📊 Data Configuration",
            key="live_data_btn",
            help="Configure data source and select platforms",
            width='stretch'
        ):
            st.session_state.show_live_data = not st.session_state.show_live_data
            st.session_state.active_section = "data_source" if not st.session_state.show_live_data else None
    
    with header_cols[1]:
        if st.button(
            "🔍 Apply Filter",
            key="filters_btn",
            help="Set time period and country filters",
            width='stretch'
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
            
            web_scraper_col1, web_scraper_col2 = st.columns([1.5, 1], gap="medium")
            with web_scraper_col1:
                # Artist selection has been moved to Filters & Analysis.
                current_filter_artist = st.session_state.get('filter_artist', NIGERIAN_ARTISTS[0] if NIGERIAN_ARTISTS else 'Unknown')
                st.markdown(f"**Artist (Filters & Analysis):** {current_filter_artist}")
            with web_scraper_col2:
                fetch_web_data = st.button("🔎 Web Scraper", key="web_scrape_btn", help="Scrape Web Data", width='stretch')
            
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
                                st.dataframe(web_df[available_cols], width='stretch')
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
                # --- Calendar-based time period selection ---
                st.markdown("**Time Period**")

                # Determine default start and end dates from selected_months
                def _get_month_range(month_code: str):
                    year, month = map(int, month_code.split('-'))
                    start_date = pd.Timestamp(year=year, month=month, day=1)
                    end_date = (start_date + pd.offsets.MonthEnd(1))
                    return start_date, end_date

                # If session state already has months, get first and last date range
                selected_months = st.session_state.get('selected_months', months)
                start_default, _ = _get_month_range(selected_months[0])
                _, end_default = _get_month_range(selected_months[-1])

                # Calendar picker (range select)
                date_range = st.date_input(
                    "Select Date Range",
                    value=(start_default, end_default),
                    help="Select the start and end dates for analysis"
                )

                # Convert selected range back to list of month codes
                if isinstance(date_range, tuple) and len(date_range) == 2:
                    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
                    all_months = pd.period_range(start=start, end=end, freq='M').strftime("%Y-%m").tolist()
                else:
                    all_months = [pd.to_datetime(date_range).strftime("%Y-%m")]

                st.session_state.selected_months = all_months

            with filter_cols[1]:
                # --- Artist selector ---
                st.selectbox(
                    "Select Artist",
                    options=NIGERIAN_ARTISTS,
                    index=NIGERIAN_ARTISTS.index('Burna Boy') if 'Burna Boy' in NIGERIAN_ARTISTS else 0,
                    key="filter_artist",
                    help="Choose a Nigerian artist to analyze"
                )

                # --- Country selector ---
                header_country = st.selectbox(
                    "Country",
                    country_options,
                    key="header_country"
                )

            st.markdown('</div>', unsafe_allow_html=True)

    # Sidebar mirror of filters (synced with header)
    selected_platforms = header_platforms
    selected_months = st.session_state.selected_months
    drill_country = header_country


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
        country_agg = filtered_df.groupby('platform').agg({'streams': 'sum', 'expected_revenue_ngn': 'sum', 'actual_revenue_ngn': 'sum'}).reset_index()
        
        # Toolbar for the country detail table
        render_table_toolbar(
            f"🌍 Details for {drill_country}",
            df=country_agg,
            file_name=f"{drill_country}_platform_breakdown.csv"
        )

        fig_country = px.bar(country_agg, x='platform', y='streams', title=f"Streams in {drill_country} by Platform", template='plotly_dark')
        st.plotly_chart(fig_country, width='stretch')

        st.dataframe(country_agg.assign(
            expected_revenue_ngn=country_agg['expected_revenue_ngn'].map(lambda x: f"₦{x:,.0f}"),
            actual_revenue_ngn=country_agg['actual_revenue_ngn'].map(lambda x: f"₦{x:,.0f}")
        ), hide_index=True, width='stretch')
    
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
            cols_to_display = ['artist', 'title', 'source', 'url', 'date_fetched']
            cols_available = [col for col in cols_to_display if col in web_df.columns]
            
            # Format and display
            display_df = web_df[cols_available].copy()
            
            # Add clickable links if URL column exists
            if 'url' in display_df.columns:
                display_df['url'] = display_df['url'].apply(
                    lambda x: f"[🔗 Link]({x})" if pd.notna(x) and x != 'N/A' else 'N/A'
                )
            
            # Toolbar above the All Sources table
            render_table_toolbar(
                f"📋 Total sources found: {len(web_df)}",
                df=web_df[cols_available],
                file_name=f"{web_artist}_web_sources.csv"
            )

            st.dataframe(
                display_df,
                width='stretch',
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
                
                # Toolbar above the Source List table
                render_table_toolbar(
                    "Source List",
                    df=source_breakdown,
                    file_name=f"{web_artist}_source_breakdown.csv"
                )

                st.dataframe(source_breakdown, hide_index=True, width='stretch')
            
            with col_right:
                # Pie chart of source distribution
                fig_sources = px.pie(
                    source_breakdown,
                    names='Source',
                    values='Count',
                    title='Data Distribution by Source',
                    template='plotly_dark'
                )
                st.plotly_chart(fig_sources, width='stretch')
        
        with tab3:
            # Source statistics and metadata
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
            
            # Toolbar above the Source Statistics table
            render_table_toolbar(
                "📊 Source Statistics",
                df=stats_df,
                file_name=f"{web_artist}_web_statistics.csv"
            )

            st.dataframe(stats_df, hide_index=True, width='stretch')
    
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
        
        # Toolbar above the Economic Impact metrics table (download enabled via toolbar)
        impact_export_df = pd.DataFrame([{
            'Metric': 'Direct Streaming Revenue',
            'Value': impact_metrics['direct_revenue_ngn']
        }, {
            'Metric': 'Indirect Revenue (Est.)',
            'Value': impact_metrics['indirect_revenue_ngn']
        }, {
            'Metric': 'Cultural Export Value',
            'Value': impact_metrics['cultural_export_value_ngn']
        }, {
            'Metric': 'Total Economic Impact',
            'Value': impact_metrics['total_economic_impact_ngn']
        }])

        render_table_toolbar(
            "Economic Impact Metrics",
            df=impact_export_df,
            file_name="economic_impact_analysis.csv"
        )

        st.table(impact_df)
    
    # AI Economic Impact & Job Creation Predictions
    st.markdown("---")
    if display_economic_impact_section:
        display_economic_impact_section()
    else:
        st.warning("⚠️ AI Economic Impact module not loaded. Check imports.")
    
    # ============================================

# helper function for revenue gap visualizaton
def render_revenue_gap_visualization(country_impact, top10):
    """
    Render an engaging revenue gap analysis visualization as a standalone section
    
    Args:
        country_impact: DataFrame with country-level aggregated data
        top10: DataFrame with top 10 countries by impact
    """
    
    # Section header with styling
    st.markdown("---")
    st.markdown("""
    <div style="padding: 20px; background: linear-gradient(135deg, rgba(14, 165, 164, 0.1), rgba(124, 58, 237, 0.05)); 
                border-radius: 12px; margin: 20px 0;">
        <h2 style="color: #0EA5A4; margin: 0;">💰 Revenue Gap Analysis</h2>
        <p style="color: #64748B; margin-top: 8px;">
            Comparing expected vs actual revenue to identify underpayment opportunities
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Option 1: Grouped Bar Chart (Recommended for clarity)
    
    # Prepare data for visualization
    viz_data = top10.copy()
    
    # Create grouped bar chart
    fig_revenue = go.Figure()
    
    # Add Expected Revenue bars
    fig_revenue.add_trace(go.Bar(
        name='Expected Revenue',
        x=viz_data['country'],
        y=viz_data['expected_revenue_ngn'],
        marker=dict(
            color='#0EA5A4',  # Your primary teal color
            line=dict(color='#0c8483', width=1)
        ),
        text=viz_data['expected_revenue_ngn'].apply(lambda x: f"₦{x:,.0f}"),
        textposition='outside',
        textfont=dict(size=10),
        hovertemplate='<b>%{x}</b><br>Expected: ₦%{y:,.0f}<extra></extra>'
    ))
    
    # Add Actual Revenue bars
    fig_revenue.add_trace(go.Bar(
        name='Actual Revenue',
        x=viz_data['country'],
        y=viz_data['actual_revenue_ngn'],
        marker=dict(
            color='#F59E0B',  # Your accent orange color
            line=dict(color='#d97706', width=1)
        ),
        text=viz_data['actual_revenue_ngn'].apply(lambda x: f"₦{x:,.0f}"),
        textposition='outside',
        textfont=dict(size=10),
        hovertemplate='<b>%{x}</b><br>Actual: ₦%{y:,.0f}<extra></extra>'
    ))
    
    # Update layout for modern look
    fig_revenue.update_layout(
        title={
            'text': 'Expected vs Actual Revenue by Country',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=18, color='#1F213A', weight='bold')
        },
        xaxis=dict(
            title='Country',
            tickangle=-45,
            gridcolor='rgba(14, 165, 164, 0.1)',
            showgrid=True
        ),
        yaxis=dict(
            title='Revenue (NGN)',
            gridcolor='rgba(14, 165, 164, 0.1)',
            showgrid=True
        ),
        barmode='group',
        template='plotly_white',
        hovermode='x unified',
        plot_bgcolor='rgba(244, 247, 245, 0.5)',
        paper_bgcolor='white',
        font=dict(family='Inter, sans-serif', color='#1F213A'),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='rgba(14, 165, 164, 0.2)',
            borderwidth=1
        ),
        margin=dict(t=100, b=100),
        height=500
    )
    
    st.plotly_chart(fig_revenue, width='stretch')
    
    # Option 2: Revenue Gap Waterfall Chart (Shows the gap more dramatically)
    st.markdown("### Revenue Gap Breakdown")
    
    # Calculate total gaps
    total_expected = viz_data['expected_revenue_ngn'].sum()
    total_actual = viz_data['actual_revenue_ngn'].sum()
    total_gap = total_expected - total_actual
    
    # Create waterfall data
    waterfall_data = []
    cumulative = 0
    
    for _, row in viz_data.iterrows():
        gap = row['expected_revenue_ngn'] - row['actual_revenue_ngn']
        waterfall_data.append({
            'country': row['country'],
            'gap': gap,
            'cumulative': cumulative + gap
        })
        cumulative += gap
    
    waterfall_df = pd.DataFrame(waterfall_data)
    
    # Create waterfall chart
    fig_waterfall = go.Figure()
    
    # Add bars for each country's gap
    colors = ['#DC2626' if gap > 0 else '#16A34A' 
              for gap in waterfall_df['gap']]
    
    fig_waterfall.add_trace(go.Bar(
        x=waterfall_df['country'],
        y=waterfall_df['gap'],
        marker=dict(
            color=colors,
            line=dict(color='rgba(0,0,0,0.3)', width=1)
        ),
        text=waterfall_df['gap'].apply(lambda x: f"₦{x:,.0f}"),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Gap: ₦%{y:,.0f}<extra></extra>',
        name='Revenue Gap'
    ))
    
    fig_waterfall.update_layout(
        title={
            'text': f'Revenue Gap by Country (Total Gap: ₦{total_gap:,.0f})',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis=dict(
            title='Country',
            tickangle=-45,
            gridcolor='rgba(14, 165, 164, 0.1)'
        ),
        yaxis=dict(
            title='Revenue Gap (NGN)',
            gridcolor='rgba(14, 165, 164, 0.1)',
            zeroline=True,
            zerolinecolor='rgba(14, 165, 164, 0.3)',
            zerolinewidth=2
        ),
        template='plotly_white',
        plot_bgcolor='rgba(244, 247, 245, 0.5)',
        paper_bgcolor='white',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig_waterfall, width='stretch')
    
    # Option 3: Heatmap for detailed comparison
    with st.expander("📊 Detailed Revenue Comparison Matrix"):
        # Prepare heatmap data
        heatmap_data = viz_data[['country', 'expected_revenue_ngn', 
                                  'actual_revenue_ngn', 'revenue_gap']].copy()
        
        # Normalize for color scale
        heatmap_data['gap_percentage'] = (
            (heatmap_data['revenue_gap'] / heatmap_data['expected_revenue_ngn']) * 100
        )
        
        # Create heatmap
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=[heatmap_data['expected_revenue_ngn'], 
               heatmap_data['actual_revenue_ngn'],
               heatmap_data['revenue_gap']],
            x=heatmap_data['country'],
            y=['Expected Revenue', 'Actual Revenue', 'Revenue Gap'],
            colorscale=[
                [0, '#F59E0B'],      # Orange for low
                [0.5, '#0EA5A4'],    # Teal for medium
                [1, '#7C3AED']       # Purple for high
            ],
            text=[[f"₦{val:,.0f}" for val in heatmap_data['expected_revenue_ngn']],
                  [f"₦{val:,.0f}" for val in heatmap_data['actual_revenue_ngn']],
                  [f"₦{val:,.0f}" for val in heatmap_data['revenue_gap']]],
            texttemplate='%{text}',
            textfont=dict(size=10),
            hovertemplate='%{y}<br>%{x}: %{text}<extra></extra>',
            colorbar=dict(title='Amount (NGN)')
        ))
        
        fig_heatmap.update_layout(
            title='Revenue Comparison Heatmap',
            xaxis=dict(tickangle=-45),
            template='plotly_white',
            height=300
        )
        
        st.plotly_chart(fig_heatmap, width='stretch')
    
    # # Summary metrics in columns
    # col1, col2, col3 = st.columns(3)
    
    # with col1:
    #     st.metric(
    #         "Total Expected Revenue",
    #         f"₦{total_expected:,.0f}",
    #         help="Sum of expected revenue across top 10 countries"
    #     )
    
    # with col2:
    #     st.metric(
    #         "Total Actual Revenue",
    #         f"₦{total_actual:,.0f}",
    #         help="Sum of actual revenue received"
    #     )
    
    # with col3:
    #     gap_percentage = ((total_gap / total_expected) * 100) if total_expected > 0 else 0
    #     st.metric(
    #         "Total Revenue Gap",
    #         f"₦{total_gap:,.0f}",
    #         f"-{gap_percentage:.1f}%",
    #         delta_color="inverse",
    #         help="Difference between expected and actual revenue"
    #     )

if __name__ == "__main__":
    main()