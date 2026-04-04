import streamlit as st


def apply_theme():
    st.markdown("""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;800&family=Source+Serif+4:opsz,wght@8..60,300;400;600&family=JetBrains+Mono:wght@400;500&display=swap');

    #MainMenu, footer, header, .stDeployButton {display:none !important;}

    /* ── Base ─────────────────────────────────────────────── */
    * { box-sizing: border-box; }

    html, body, .main, [data-testid="stAppViewContainer"] {
        background: #0F0F0E !important;
        color: #E8E4DC !important;
        font-family: 'Source Serif 4', Georgia, serif !important;
    }

    .block-container {
        background: #0F0F0E !important;
        padding-top: 1.5rem !important;
        max-width: 1100px;
    }

    section.main {
        background: #0F0F0E !important;
    }

    div[data-testid="stVerticalBlock"] {
        background: transparent !important;
    }

    /* ── Sidebar ──────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: #111110 !important;
        border-right: 1px solid #2A2820 !important;
    }

    [data-testid="stSidebar"] * {
        font-family: 'Source Serif 4', Georgia, serif !important;
    }

    /* ── Typography ───────────────────────────────────────── */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', Georgia, serif !important;
        color: #E8E4DC !important;
        letter-spacing: -0.01em;
    }

    p, span, div, li {
        font-family: 'Source Serif 4', Georgia, serif !important;
    }

    /* ── Hero Section ─────────────────────────────────────── */
    .hero-section {
        background: linear-gradient(135deg, #1A1915 0%, #161512 50%, #1E1B16 100%);
        border: 1px solid #2E2B22;
        border-radius: 4px;
        padding: 52px 48px;
        text-align: center;
        margin-bottom: 32px;
        position: relative;
        overflow: hidden;
    }

    .hero-section::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: radial-gradient(ellipse at 50% 0%, rgba(212,175,55,0.07) 0%, transparent 65%);
        pointer-events: none;
    }

    .hero-title {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-size: 34px;
        font-weight: 800;
        color: #D4AF37;
        margin-bottom: 12px;
        line-height: 1.15;
        letter-spacing: -0.02em;
    }

    .hero-subtitle {
        color: #9E9A8E;
        font-family: 'Source Serif 4', Georgia, serif !important;
        font-size: 15px;
        font-weight: 300;
        line-height: 1.7;
        max-width: 560px;
        margin: 0 auto;
    }

    /* ── Glass Cards ──────────────────────────────────────── */
    .glass-card {
        background: #161512;
        border: 1px solid #2A2820;
        border-radius: 4px;
        padding: 24px;
        margin-bottom: 18px;
        transition: border-color 0.25s ease;
    }

    .glass-card:hover {
        border-color: #3A3628;
    }

    /* ── Section Titles ───────────────────────────────────── */
    .section-title {
        font-family: 'Playfair Display', Georgia, serif !important;
        font-size: 18px;
        font-weight: 700;
        margin-top: 24px;
        margin-bottom: 14px;
        color: #E8E4DC !important;
        letter-spacing: -0.01em;
        padding-bottom: 7px;
        border-bottom: 1px solid #2A2820;
    }

    /* ── Buttons ──────────────────────────────────────────── */
    .stButton > button {
        background: linear-gradient(135deg, #C9A030 0%, #D4AF37 60%, #BF9628 100%) !important;
        color: #0F0F0E !important;
        border-radius: 3px !important;
        border: none !important;
        padding: 10px 22px !important;
        font-family: 'Source Serif 4', Georgia, serif !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 0.01em !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 2px 8px rgba(212,175,55,0.15) !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #D4AF37 0%, #F0CC5A 60%, #C9A030 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px rgba(212,175,55,0.25) !important;
    }

    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* Primary button override */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #C9A030, #D4AF37) !important;
    }

    /* ── Download Button ──────────────────────────────────── */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #C9A030, #D4AF37) !important;
        color: #0F0F0E !important;
        font-family: 'Source Serif 4', Georgia, serif !important;
        font-weight: 600 !important;
        border-radius: 3px !important;
        border: none !important;
    }

    /* ── Inputs ───────────────────────────────────────────── */
    input, textarea, select {
        background: #161512 !important;
        color: #E8E4DC !important;
        border: 1px solid #2A2820 !important;
        border-radius: 3px !important;
        font-family: 'Source Serif 4', Georgia, serif !important;
    }

    input:focus, textarea:focus {
        border-color: #C9A030 !important;
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(201,160,48,0.12) !important;
    }

    .stTextInput input {
        background: #161512 !important;
        color: #E8E4DC !important;
        font-family: 'Source Serif 4', Georgia, serif !important;
    }

    .stTextInput > div > div {
        background: #161512 !important;
    }

    /* ── Select Boxes ─────────────────────────────────────── */
    .stSelectbox > div > div {
        background: #161512 !important;
        border: 1px solid #2A2820 !important;
        color: #E8E4DC !important;
        border-radius: 3px !important;
    }

    .stSelectbox div {
        background: #161512 !important;
        color: #E8E4DC !important;
    }

    /* ── Slider ───────────────────────────────────────────── */
    .stSlider div {
        color: #E8E4DC !important;
    }

    .stSlider [data-baseweb="slider"] {
        padding: 0 !important;
    }

    /* ── Checkbox ─────────────────────────────────────────── */
    .stCheckbox label {
        color: #C8C4BC !important;
        font-family: 'Source Serif 4', Georgia, serif !important;
    }

    /* ── Tabs ─────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: #161512 !important;
        border-radius: 4px !important;
        border: 1px solid #2A2820 !important;
        gap: 0 !important;
    }

    .stTabs [data-baseweb="tab"] {
        color: #9E9A8E !important;
        font-family: 'Source Serif 4', Georgia, serif !important;
        font-size: 14px !important;
        font-weight: 400 !important;
        border-radius: 3px !important;
        padding: 8px 18px !important;
    }

    .stTabs [aria-selected="true"] {
        background: #2A2820 !important;
        border: 1px solid #C9A030 !important;
        color: #D4AF37 !important;
        font-weight: 600 !important;
    }

    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 20px !important;
    }

    /* ── Expander ─────────────────────────────────────────── */
    .streamlit-expanderHeader {
        background: #161512 !important;
        border: 1px solid #2A2820 !important;
        color: #E8E4DC !important;
        font-family: 'Source Serif 4', Georgia, serif !important;
        border-radius: 3px !important;
    }

    .streamlit-expanderContent {
        background: #161512 !important;
        border: 1px solid #2A2820 !important;
        border-top: none !important;
    }

    details summary {
        font-family: 'Source Serif 4', Georgia, serif !important;
        color: #E8E4DC !important;
    }

    /* ── Metrics ──────────────────────────────────────────── */
    [data-testid="stMetricValue"] {
        color: #D4AF37 !important;
        font-family: 'Playfair Display', Georgia, serif !important;
        font-weight: 700 !important;
        font-size: 28px !important;
    }

    [data-testid="stMetricLabel"] {
        color: #9E9A8E !important;
        font-family: 'Source Serif 4', Georgia, serif !important;
        font-size: 12px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }

    .metric-card {
        background: #161512;
        border: 1px solid #2A2820;
        border-radius: 4px;
        padding: 18px;
        text-align: center;
    }

    .metric-card-value {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 28px;
        font-weight: 700;
        color: #D4AF37;
    }

    .metric-card-label {
        font-family: 'Source Serif 4', Georgia, serif;
        font-size: 11px;
        color: #6E6A5E;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    /* ── Paper Cards ──────────────────────────────────────── */
    .paper-card {
        background: #161512;
        border: 1px solid #2A2820;
        border-radius: 4px;
        padding: 18px;
        margin-bottom: 14px;
        transition: all 0.25s ease;
    }

    .paper-card:hover {
        border-color: #C9A030;
        transform: translateY(-1px);
    }

    .paper-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 16px;
        font-weight: 700;
        color: #E8E4DC;
        margin-bottom: 8px;
        line-height: 1.4;
    }

    .paper-title a {
        color: #D4AF37;
        text-decoration: none;
    }

    .paper-title a:hover {
        color: #F0CC5A;
    }

    .paper-authors {
        color: #9E9A8E;
        font-family: 'Source Serif 4', Georgia, serif;
        font-size: 13px;
    }

    .paper-meta {
        color: #6E6A5E;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
    }

    /* ── Badges ───────────────────────────────────────────── */
    .badge {
        padding: 3px 9px;
        border-radius: 2px;
        font-family: 'Source Serif 4', Georgia, serif;
        font-size: 11px;
        font-weight: 600;
        background: #2A2820;
        color: #9E9A8E;
        letter-spacing: 0.04em;
    }

    .badge-gold {
        background: rgba(212, 175, 55, 0.12);
        color: #D4AF37;
        border: 1px solid rgba(212, 175, 55, 0.3);
    }

    /* ── HR divider ───────────────────────────────────────── */
    hr {
        border: none !important;
        height: 1px !important;
        background: #2A2820 !important;
        margin: 20px 0 !important;
    }

    /* ── DataFrame ────────────────────────────────────────── */
    [data-testid="stDataFrame"] {
        background: #161512 !important;
        border: 1px solid #2A2820 !important;
        border-radius: 4px !important;
    }

    /* ── Notifications / Alerts ───────────────────────────── */
    .stAlert {
        background: #161512 !important;
        border: 1px solid #2A2820 !important;
        border-radius: 4px !important;
        font-family: 'Source Serif 4', Georgia, serif !important;
    }

    /* ── Scrollbar ────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0F0F0E; }
    ::-webkit-scrollbar-thumb { background: #2A2820; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #C9A030; }

    /* ── Code / Mono ──────────────────────────────────────── */
    code, pre, .stCodeBlock {
        font-family: 'JetBrains Mono', monospace !important;
        background: #161512 !important;
        border: 1px solid #2A2820 !important;
        color: #D4AF37 !important;
    }

    /* ── Spinner ──────────────────────────────────────────── */
    .stSpinner > div {
        border-top-color: #D4AF37 !important;
    }

    /* ── Info / Warning / Error ───────────────────────────── */
    div[data-testid="stNotification"] {
        background: #161512 !important;
        border-left-color: #D4AF37 !important;
        font-family: 'Source Serif 4', Georgia, serif !important;
    }

    </style>
    """, unsafe_allow_html=True)