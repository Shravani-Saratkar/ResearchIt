import streamlit as st


def apply_theme():
    st.markdown("""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    #MainMenu, footer, header, .stDeployButton {display:none !important;}

    * {
        font-family: 'Inter', sans-serif;
    }

    /* ---------- Base ---------- */

    .main {
        background: #1A1A1A;
        color: #F5F5F0;
    }

    /* ---------- Sidebar ---------- */

    [data-testid="stSidebar"] {
        background: #1A1A1A;
        border-right: 1px solid #3A3A3A;
    }

    /* ---------- Cards ---------- */

    .glass-card {
        background: #2A2A2A;
        border: 1px solid #3A3A3A;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }

    .glass-card:hover {
        border-color: #4A4A4A;
    }

    /* ---------- Hero ---------- */

    .hero-section {
        background: #2A2A2A;
        border: 1px solid #3A3A3A;
        border-radius: 14px;
        padding: 48px;
        text-align: center;
        margin-bottom: 28px;
    }

    .hero-title {
        font-size: 38px;
        font-weight: 800;
        background: linear-gradient(135deg, #D4AF37, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 12px;
    }

    .hero-subtitle {
        color: #C0C0C0;
        font-size: 16px;
    }

    /* ---------- Section ---------- */

    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin-top: 32px;
        margin-bottom: 16px;
        color: #F5F5F0;
    }

    /* ---------- Buttons ---------- */

    .stButton > button {
        background: linear-gradient(135deg, #D4AF37, #C9A636);
        color: #1A1A1A;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: 700;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #FFD700, #D4AF37);
        transform: translateY(-2px);
    }

    /* ---------- Inputs ---------- */

    input, textarea {
        background: #2A2A2A !important;
        color: #F5F5F0 !important;
        border: 1px solid #3A3A3A !important;
        border-radius: 8px !important;
    }

    input:focus, textarea:focus {
        border-color: #D4AF37 !important;
    }

    /* ---------- Tabs ---------- */

    .stTabs [data-baseweb="tab-list"] {
        background: #2A2A2A;
        border-radius: 10px;
    }

    .stTabs [aria-selected="true"] {
        background: #3A3A3A !important;
        border: 1px solid #D4AF37;
        color: #D4AF37 !important;
    }

    /* ---------- Paper card ---------- */

    .paper-card {
        background: #2A2A2A;
        border: 1px solid #3A3A3A;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }

    .paper-card:hover {
        border-color: #D4AF37;
        transform: translateY(-2px);
    }

    .paper-title {
        font-size: 16px;
        font-weight: 700;
        color: #F5F5F0;
        margin-bottom: 8px;
    }

    .paper-title a {
        color: #D4AF37;
        text-decoration: none;
        font-weight: 700;
    }

    .paper-title a:hover {
        color: #FFD700;
    }

    .paper-authors {
        color: #C0C0C0;
        font-size: 13px;
    }

    .paper-meta {
        color: #808080;
        font-size: 12px;
    }

    /* ---------- Metrics ---------- */

    [data-testid="stMetricValue"] {
        color: #D4AF37;
        font-weight: 800;
        font-size: 28px;
    }

    [data-testid="stMetricLabel"] {
        color: #C0C0C0;
        font-size: 12px;
        text-transform: uppercase;
    }

    .metric-card {
        background: #2A2A2A;
        border: 1px solid #3A3A3A;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }

    .metric-card-value {
        font-size: 28px;
        font-weight: 800;
        color: #D4AF37;
    }

    .metric-card-label {
        font-size: 11px;
        color: #808080;
        text-transform: uppercase;
    }

    /* ---------- Badges ---------- */

    .badge {
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        background: #3A3A3A;
        color: #C0C0C0;
    }

    .badge-gold {
        background: rgba(212, 175, 55, 0.2);
        color: #D4AF37;
        border: 1px solid #D4AF37;
    }

    hr {
        border: none;
        height: 1px;
        background: #3A3A3A;
        margin: 24px 0;
    }

    /* ---------- Select Box ---------- */

    .stSelectbox > div > div {
        background: #2A2A2A;
        border: 1px solid #3A3A3A;
        color: #F5F5F0;
    }

    /* ---------- Dataframe ---------- */

    [data-testid="stDataFrame"] {
        background: #2A2A2A;
        border: 1px solid #3A3A3A;
    }

    /* ---------- Expander ---------- */

    .streamlit-expanderHeader {
        background: #2A2A2A;
        border: 1px solid #3A3A3A;
        color: #F5F5F0;
    }

    /* ---------- Download Button ---------- */

    .stDownloadButton > button {
        background: linear-gradient(135deg, #D4AF37, #C9A636);
        color: #1A1A1A;
        font-weight: 700;
    }
    /* FIX WHITE BOXES */

input, textarea, select {
    background: #2A2A2A !important;
    color: #F5F5F0 !important;
    border: 1px solid #3A3A3A !important;
}

.stTextInput input {
    background: #2A2A2A !important;
    color: #F5F5F0 !important;
}

.stSlider div {
    color: #F5F5F0 !important;
}

.stSelectbox div {
    background: #2A2A2A !important;
    color: #F5F5F0 !important;
}

.stCheckbox label {
    color: #F5F5F0 !important;
}

.block-container {
    background: #1A1A1A !important;
}

section.main {
    background: #1A1A1A !important;
}

div[data-testid="stVerticalBlock"] {
    background: transparent !important;
}
                
    </style>
    """, unsafe_allow_html=True)