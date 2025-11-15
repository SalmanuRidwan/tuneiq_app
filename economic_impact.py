"""
Economic Impact & Job Creation Module

Displays AI-powered predictions for GDP contribution and job creation
based on streaming data from APIs or web scraping.
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict
import importlib
import json

# Import predictor and data pipeline
try:
    # Try package-style imports first
    dp = importlib.import_module("tuneiq_app.data_pipeline")
    get_model_predictions = getattr(dp, "get_model_predictions")
    load_sample_data = getattr(dp, "load_sample_data")
    fetch_live_data = getattr(dp, "fetch_live_data")
    na_mod = importlib.import_module("tuneiq_app.nigerian_artists")
    NIGERIAN_ARTISTS = getattr(na_mod, "NIGERIAN_ARTISTS")
except Exception:
    # Fallback to direct imports
    try:
        dp = importlib.import_module("data_pipeline")
        get_model_predictions = getattr(dp, "get_model_predictions")
        load_sample_data = getattr(dp, "load_sample_data")
        fetch_live_data = getattr(dp, "fetch_live_data")
        na_mod = importlib.import_module("nigerian_artists")
        NIGERIAN_ARTISTS = getattr(na_mod, "NIGERIAN_ARTISTS")
    except Exception as e:
        raise ImportError(
            "Could not import data_pipeline and nigerian_artists functions. "
            "Run from project root or install package."
        ) from e

# Modern dashboard CSS styling
st.markdown("""
<style>
/* Light theme background */
body, [class*="stAppViewContainer"] {
    background-color: #f7f9fc;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Main card styling */
.main-card {
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    padding: 20px;
    margin-bottom: 25px;
    border: 1px solid rgba(14, 165, 164, 0.1);
}

/* KPI card styling */
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

/* Metric value styling */
.metric-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #0EA5A4;
    margin: 10px 0;
}

.metric-label {
    font-size: 0.9rem;
    color: #64748B;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-change {
    font-size: 0.85rem;
    margin-top: 8px;
    font-weight: 600;
}

/* Section styling */
.section-header {
    font-size: 1.4rem;
    font-weight: 700;
    color: #1F213A;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Expander card styling */
.streamlit-expanderHeader {
    background-color: rgba(14, 165, 164, 0.05) !important;
    border-radius: 10px !important;
    border: 1px solid rgba(14, 165, 164, 0.1) !important;
}

.streamlit-expanderHeader:hover {
    background-color: rgba(14, 165, 164, 0.08) !important;
}
</style>
""", unsafe_allow_html=True)

def format_currency(value: Optional[float]) -> str:
    """Format value as Nigerian Naira currency."""
    if value is None:
        return "N/A"
    return f"₦{value:,.0f}"


def format_number(value: Optional[float]) -> str:
    """Format value as integer with commas."""
    if value is None:
        return "N/A"
    return f"{int(value):,}"


def display_economic_impact_section():
    """
    Render the AI Economic Impact & Job Creation section with modern card styling.
    
    Allows users to:
    1. Select data source (Sample, Spotify, YouTube, Web Scraper)
    2. Select artist from dropdown
    3. Run predictions using the pre-trained model
    4. Display predicted GDP contribution and jobs created in modern KPI cards
    """
    
    # Section header (renamed)
    st.markdown('<div class="section-header">🤖 AI  Economic Impact & Job Creation Estimator</div>', unsafe_allow_html=True)
    st.markdown(
        "Use AI to estimate GDP contribution and job creation from streaming data. "
        "Select a data source and artist below."
    )
    
    # Input section with modern card styling
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    # Create two columns for input controls
    col1, col2 = st.columns(2)
    
    with col1:
        data_source = st.radio(
            "📊 Select Data Source",
            options=["Sample", "Spotify", "Apple Music", "YouTube", "Web Scraper"],
            horizontal=False,
            help="Choose where to fetch data for predictions"
        )
    
    with col2:
        # Get current artist from session state (set in main dashboard)
        # Default to first artist if not set
        default_artist = st.session_state.get('filter_artist', NIGERIAN_ARTISTS[0] if NIGERIAN_ARTISTS else 'Burna Boy')
        default_index = NIGERIAN_ARTISTS.index(default_artist) if default_artist in NIGERIAN_ARTISTS else 0
        
        # Artist dropdown selection
        artist_name = st.selectbox(
            "🎤 Select Artist",
            options=NIGERIAN_ARTISTS,
            index=default_index,
            key="ai_artist_selector",
            help="Choose a Nigerian artist to analyze"
        )
    
    # Run prediction button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    with col_btn1:
        run_prediction = st.button(
            "🚀 Run Prediction",
            use_container_width=True,
            key="run_prediction_btn"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if run_prediction and artist_name:
        with st.spinner(f"🔄 Analyzing {artist_name}..."):
            try:
                # Fetch data based on selected source
                if data_source == "Sample":
                    df = load_sample_data()
                    st.info(f"📊 Using sample data")
                elif data_source == "Web Scraper":
                    df = fetch_live_data(source="web", artist_name=artist_name)
                    if df.empty:
                        st.warning(f"⚠️ No web data found for {artist_name}. Using sample data instead.")
                        df = load_sample_data()
                else:
                    # Spotify, Apple Music, or YouTube require API credentials
                    if data_source == "Apple Music":
                        source_lower = "apple_music"
                    else:
                        source_lower = data_source.lower()
                    df = fetch_live_data(source=source_lower, artist_name=artist_name)
                    if df.empty:
                        st.warning(
                            f"⚠️ No {data_source} data found. "
                            f"Ensure API credentials are configured. "
                            f"Using sample data instead."
                        )
                        df = load_sample_data()
                
                # Run model prediction
                predictions = get_model_predictions(df)
                
                # Display results
                if predictions.get("error"):
                    error_msg = predictions['error']
                    st.error(f"❌ Prediction Error: {error_msg}")
                    
                    # Show helpful troubleshooting message
                    if "Model could not be loaded" in error_msg:
                        st.warning("""
                        **Model Loading Issue**: The ML model file may not be found or loaded correctly.
                        
                        ℹ️ **Troubleshooting**:
                        1. Ensure `tuneiq_gdp_jobs_model.joblib` exists in the project directory
                        2. Check that the file is not corrupted
                        3. Try running the dashboard from the project root: `cd c:\\tuneiq_app && streamlit run app.py`
                        4. Check the terminal output for detailed error logs
                        """)
                else:
                    st.success(f"✅ Predictions generated for {artist_name}")

                    # Show estimation/auto-scale notice when relevant
                    if predictions.get("estimation"):
                        st.warning(
                            "Estimation mode: model unavailable — values shown are heuristic estimates."
                        )
                    elif predictions.get("auto_scaled"):
                        st.info(
                            "Note: model output was auto-scaled for display due to high stream volume."
                        )

                    # Display KPI metrics in modern cards
                    st.markdown('<div class="main-card">', unsafe_allow_html=True)
                    st.markdown("####  AI Predicted Impact Metrics")
                    
                    kpi_cols = st.columns(3)
                    
                    with kpi_cols[0]:
                        st.markdown(f"""
                        <div class="kpi-card">
                            <div class="metric-label">💰 GDP Contribution</div>
                            <div class="metric-value">{format_currency(predictions.get('predicted_gdp'))}</div>
                            <div class="metric-change">Nigeria (NGN)</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with kpi_cols[1]:
                        st.markdown(f"""
                        <div class="kpi-card">
                            <div class="metric-label">👥 Jobs Created</div>
                            <div class="metric-value">{format_number(predictions.get('predicted_jobs'))}</div>
                            <div class="metric-change">Direct Impact</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with kpi_cols[2]:
                        confidence = predictions.get("confidence", 0)
                        confidence_pct = (confidence * 100) if confidence else 0
                        confidence_color = "#10b981" if confidence_pct >= 80 else "#f59e0b" if confidence_pct >= 60 else "#ef4444"
                        st.markdown(f"""
                        <div class="kpi-card">
                            <div class="metric-label">🎯 Confidence</div>
                            <div class="metric-value" style="color: {confidence_color};">{confidence_pct:.0f}%</div>
                            <div class="metric-change">Model Accuracy</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Show data summary
                    st.markdown('<div class="main-card">', unsafe_allow_html=True)
                    st.markdown("#### Input Data Summary")
                    
                    # Add export buttons for data
                    exp_col1, exp_col2, exp_col3 = st.columns([2, 1, 1])
                    with exp_col2:
                        csv_data = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Export (CSV)",
                            data=csv_data,
                            file_name=f"{artist_name}_{data_source}_data.csv",
                            mime="text/csv",
                            use_container_width=True,
                            key="export_data_csv"
                        )
                    with exp_col3:
                        json_data = df.to_json(orient='records', indent=2)
                        st.download_button(
                            label="📥 Export (JSON)",
                            data=json_data,
                            file_name=f"{artist_name}_{data_source}_data.json",
                            mime="application/json",
                            use_container_width=True,
                            key="export_data_json"
                        )
                    
                    summary_cols = st.columns(3)
                    
                    with summary_cols[0]:
                        st.markdown(f"""
                        <div class="kpi-card">
                            <div class="metric-label">Total Records</div>
                            <div class="metric-value">{len(df):,}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with summary_cols[1]:
                        total_streams = df['streams'].sum() if 'streams' in df.columns else 0
                        st.markdown(f"""
                        <div class="kpi-card">
                            <div class="metric-label">Total Streams</div>
                            <div class="metric-value">{format_number(total_streams)}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with summary_cols[2]:
                        unique_countries = df['country'].nunique() if 'country' in df.columns else 0
                        st.markdown(f"""
                        <div class="kpi-card">
                            <div class="metric-label">Countries</div>
                            <div class="metric-value">{unique_countries:,}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Show data preview
                    with st.expander("📋 Data Preview", expanded=False):
                        display_cols = ['artist', 'streams', 'country', 'platform', 'month']
                        available_cols = [col for col in display_cols if col in df.columns]
                        preview_df = df[available_cols].head(10)
                        
                        # Display table with export options
                        col_table, col_export = st.columns([4, 1])
                        with col_table:
                                                        # Toolbar above the preview table (Font Awesome icons)
                                                        csv_text = preview_df.to_csv(index=False)
                                                        csv_js = json.dumps(csv_text)
                                                        template = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
.tuneiq-toolbar{position:relative;margin-bottom:8px}
.tuneiq-toolbar .toolbar{position:relative;display:inline-flex;gap:6px;right:0;float:right}
.tuneiq-toolbar .icon{width:34px;height:34px;border-radius:6px;background:rgba(255,255,255,0.96);border:1px solid rgba(0,0,0,0.06);box-shadow:0 1px 2px rgba(0,0,0,0.06);display:flex;align-items:center;justify-content:center;cursor:pointer;opacity:0.95;font-size:14px}
.tuneiq-toolbar .icon:hover{transform:translateY(-1px);opacity:1}
.tuneiq-toolbar h4{margin:0;padding:6px 0;font-weight:600}
.tuneiq-toolbar:after{content:'';display:block;clear:both}
</style>
<div class='tuneiq-toolbar' data-csv={CSV_JS} data-filename='{FILE_NAME}'><h4>📋 Data Preview</h4>
    <div class='toolbar' aria-label='table-toolbar'>
        <button class='icon' title='Screenshot' onclick='tui_screenshot(this)'><i class='fa fa-camera'></i></button>
        <button class='icon' title='Zoom Area' onclick='tui_zoom_area(this)'><i class='fa fa-vector-square'></i></button>
        <button class='icon' title='Zoom In' onclick='tui_scale(this,1.2)'><i class='fa fa-search-plus'></i></button>
        <button class='icon' title='Zoom Out' onclick='tui_scale(this,0.8)'><i class='fa fa-search-minus'></i></button>
        <button class='icon' title='Fullscreen' onclick='tui_fullscreen(this)'><i class='fa fa-expand'></i></button>
        <button class='icon' title='Download CSV' onclick='tui_download(this)'><i class='fa fa-download'></i></button>
    </div>
</div>

<script>
function tui_find_table(toolbarEl){
        var node = toolbarEl.nextElementSibling;
        while(node){
                try{
                        var tbl = node.querySelector && node.querySelector('table');
                        if(tbl) return tbl;
                }catch(e){}
                node = node.nextElementSibling;
        }
        return null;
}
function tui_screenshot(btn){
    var toolbar = btn.closest('.tuneiq-toolbar');
    var tbl = tui_find_table(toolbar);
    if(!tbl){alert('Table not found for screenshot'); return;}
    if(typeof html2canvas === 'undefined'){
        var s=document.createElement('script');
        s.src='https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
        s.onload=function(){ html2canvas(tbl).then(function(c){ var a=document.createElement('a'); a.href=c.toDataURL(); a.download='table_screenshot.png'; a.click(); }); };
        document.body.appendChild(s);
    }else{
        html2canvas(tbl).then(function(c){ var a=document.createElement('a'); a.href=c.toDataURL(); a.download='table_screenshot.png'; a.click(); });
    }
}
function tui_scale(btn,factor){
    var toolbar = btn.closest('.tuneiq-toolbar');
    var tbl = tui_find_table(toolbar);
    if(!tbl){alert('Table not found for zoom'); return;}
    var cur = tbl.style.transform.match(/scale\\(([^)]+)\\)/);
    var val = cur ? parseFloat(cur[1]) : 1;
    val = Math.max(0.25, Math.min(5, val * factor));
    tbl.style.transformOrigin = '0 0';
    tbl.style.transform = 'scale('+val+')';
}
function tui_zoom_area(btn){
    var toolbar = btn.closest('.tuneiq-toolbar');
    var tbl = tui_find_table(toolbar);
    if(!tbl){alert('Table not found for zoom area'); return;}
    if(tbl.classList.contains('tui-zoom-area')){ tbl.classList.remove('tui-zoom-area'); tbl.style.transform='scale(1)'; tbl.style.maxHeight=''; tbl.style.overflow=''; }
    else{ tbl.classList.add('tui-zoom-area'); tbl.style.transform='scale(1.25)'; tbl.style.maxHeight='600px'; tbl.style.overflow='auto'; }
}
function tui_fullscreen(btn){ var toolbar = btn.closest('.tuneiq-toolbar'); var tbl = tui_find_table(toolbar); if(!tbl){alert('Table not found for fullscreen'); return;} var w = window.open('','_blank'); w.document.write('<html><head><title>Table Fullscreen</title></head><body>'+tbl.outerHTML+'</body></html>'); w.document.close(); }
function tui_download(btn){ var toolbar = btn.closest('.tuneiq-toolbar'); var csv = toolbar.getAttribute('data-csv'); var filename = toolbar.getAttribute('data-filename') || 'table.csv'; if(!csv || csv==='null'){ alert('No CSV available for this table'); return; } var a = document.createElement('a'); a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv); a.download = filename; a.click(); }
</script>
"""
                                                        toolbar_html = template.replace('{CSV_JS}', csv_js).replace('{FILE_NAME}', f"{artist_name}_preview.csv")
                                                        st.markdown(toolbar_html, unsafe_allow_html=True)
                                                        st.dataframe(preview_df, use_container_width=True)
                        with col_export:
                            # Quick export button for preview
                            preview_csv = preview_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Export Preview",
                                data=preview_csv,
                                file_name=f"{artist_name}_preview.csv",
                                mime="text/csv",
                                use_container_width=True,
                                key="export_preview_csv"
                            )
            
            except Exception as e:
                st.error(f"❌ Error during prediction: {str(e)}")
    
    elif run_prediction:
        st.warning("⚠️ Please select an artist")
    
    # Add information box
    # About/Info expander removed as requested
