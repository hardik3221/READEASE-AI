import streamlit as st

from config import (
    bg_color, text_color, card_color, cyan_color, accent_color, border_color,
    paper_bg, paper_ink, paper_border, paper_accent,
)


def inject_global_css(logo_src):
    """The full app stylesheet."""
    dynamic_css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Figtree:wght@400;500;600;700&display=swap');

/* Clean minimal hiding, leaves the sidebar toggle completely untouched */
#MainMenu {{visibility: hidden !important;}}
footer {{visibility: hidden !important;}}

/* --- ENABLE SMOOTH SCROLLING FOR STREAMLIT CONTAINERS --- */
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMainContainer"], [data-testid="stMain"] {{
    scroll-behavior: smooth !important;
}}

@font-face {{
    font-family: 'OpenDyslexic';
    src: url('https://cdn.jsdelivr.net/gh/antijingoist/opendyslexic@master/compiled/OpenDyslexic-Regular.otf') format('opentype');
    font-weight: normal;
    font-style: normal;
}}

.stApp {{ background-color: {bg_color}; }}

/* --- TYPOGRAPHY --- */
html, body, [class*="css"], p, li, label, .stMarkdown {{
    font-family: 'OpenDyslexic', 'Figtree', sans-serif !important;
    color: {text_color} !important;
}}
h1, h2, h3, h4, h5, h6, .nav-title, .hero-text-light, .hero-text-cyan {{
    font-family: 'OpenDyslexic', 'Fraunces', Georgia, serif !important;
    font-weight: 700 !important;
    color: {text_color} !important;
}}

/* --- UPGRADED ACCESSIBILITY TWEAKS --- */
[data-testid="stUploadedFile"] {{ border: 1px solid #5A5E73 !important; border-radius: 4px !important; background-color: #222530 !important; }}
[data-testid="stAlert"] {{ background-color: rgba(105, 240, 174, 0.15) !important; border: 1px solid {accent_color} !important; color: #FFFFFF !important; }}

/* --- DASHBOARD CARD CONTAINERS --- */
.dashboard-card {{
    background: rgba(30, 28, 41, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 13px;
    border-radius: 9px;
    box-shadow: 0 5px 16px rgba(0, 0, 0, 0.5);
    margin-bottom: 14px;
}}

/* --- FILE UPLOADER REFINEMENT --- */
[data-testid="stFileUploader"] {{
    background: rgba(14, 17, 23, 0.9);
    border: 1px dashed rgba(0, 229, 255, 0.4) !important;
    border-radius: 6px;
    padding: 5px;
}}

/* --- TABS POLISH --- */
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; background-color: transparent; }}
.stTabs [data-baseweb="tab"] {{ background-color: rgba(30, 28, 41, 0.7); border-radius: 4px 4px 0 0; color: #8b949e; padding: 4px 9px; border: 1px solid {border_color}; }}
.stTabs [aria-selected="true"] {{ background-color: rgba(0, 229, 255, 0.12) !important; color: {cyan_color} !important; border-color: rgba(0, 229, 255, 0.4) !important; }}

/* --- READING PANE --- */
.reading-pane {{
    position: relative;
    background-color: {paper_bg};
    padding: 18px 27px;
    border-radius: 3px 5px 5px 3px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.35), inset 0 0 0 1px {paper_border};
    border: 1px solid {paper_border};
    transition: all 0.3s ease;
}}
.reading-pane::after {{
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 0; height: 0;
    border-style: solid;
    border-width: 0 12px 12px 0;
    border-color: transparent #DCCEA4 transparent transparent;
    filter: drop-shadow(-1px 1px 2px rgba(0,0,0,0.18));
    border-top-right-radius: 3px;
}}
.reading-pane, .reading-pane p, .reading-pane li, .reading-pane div, .reading-pane span, .reading-pane h1, .reading-pane h2, .reading-pane h3 {{
    font-family: 'OpenDyslexic', sans-serif !important;
    letter-spacing: 0.02em !important;
    color: {paper_ink} !important;
}}
.reading-pane p, .reading-pane li {{ line-height: 1.85 !important; margin-bottom: 6px !important; }}
.reading-pane strong, .reading-pane b {{ font-family: 'OpenDyslexic', sans-serif !important; font-weight: 700 !important; color: {paper_accent} !important; }}
.reading-pane h1, .reading-pane h2, .reading-pane h3 {{ margin-bottom: 9px !important; border-bottom: 1px solid {paper_border}; padding-bottom: 4px; }}
.reading-container {{ max-width: 495px; margin: 0 auto; }}
.badge {{ background-color: {border_color}; color: {cyan_color}; padding: 2px 5px; border-radius: 7px; font-size: 0.38rem; font-weight: 600; letter-spacing: 0.03em; margin-bottom: 7px; display: inline-block; font-family: 'OpenDyslexic', 'Figtree', sans-serif !important; }}

/* --- PRIMARY BUTTON STYLING --- */
.stButton button {{
    white-space: nowrap !important;
}}
button[kind="primary"] {{
    background-color: {cyan_color} !important;
    border: none !important;
    font-weight: 600 !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
button[kind="primary"] * {{ color: #0E1117 !important; }}
button[kind="primary"]:hover {{
    background-color: {accent_color} !important; transform: translateY(-2px); box-shadow: 0 3px 8px rgba(0, 229, 255, 0.25);
}}

/* --- GEMINI STYLE SIDEBAR UI --- */
[data-testid="collapsedControl"] svg {{
    display: none !important;
}}
[data-testid="collapsedControl"] {{
    background-image: url('{logo_src}');
    background-size: cover;
    background-position: center;
    border-radius: 50%;
    width: 19px !important;
    height: 19px !important;
    border: 1px solid {cyan_color};
    margin-top: 5px;
    margin-left: 8px;
    transition: transform 0.2s ease;
    z-index: 999999 !important;
}}
[data-testid="collapsedControl"]:hover {{
    transform: scale(1.1);
}}
[data-testid="stSidebar"] {{ background-color: #13151C !important; border-right: 1px solid {border_color}; }}
[data-testid="stSidebar"] button[kind="secondary"] {{
    background-color: transparent !important; border: none !important; justify-content: flex-start !important; 
    padding: 4px 5px !important; box-shadow: none !important;
}}
[data-testid="stSidebar"] button[kind="secondary"]:hover {{ background-color: #1E212B !important; }}

/* --- ABSOLUTE ZERO-GAP SIDEBAR TRICKS --- */
[data-testid="stSidebar"] .block-container {{ 
    padding-top: 0px !important;
    padding-left: 6px !important;
    padding-right: 6px !important;
    padding-bottom: 15px !important; 
}}

/* Force Streamlit's first internal element block to strip its top margin entirely */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:first-child {{
    margin-top: -15px !important;
}}

[data-testid="stSidebar"] .stButton button {{
    font-size: 10px !important;
    padding: 4px 6px !important;
    min-height: 26px !important;
}}

/* --- LANDING PAGE ANIMATIONS --- */
@keyframes fadeUp {{ 0% {{ opacity: 0; transform: translateY(11px); }} 100% {{ opacity: 1; transform: translateY(0); }} }}
.hero-wrapper {{ padding: 1.6rem 0 1.1rem 0; margin-top: 33px; text-align: center; animation: fadeUp 1s ease-out; position: relative; overflow: hidden; }}
.hero-wrapper::before, .hero-wrapper::after {{
    content: ''; position: absolute; width: 137px; height: 137px;
    background: radial-gradient(circle, rgba(0,229,255,0.07) 0%, transparent 60%); border-radius: 50%;
    animation: floatShape 12s infinite alternate ease-in-out; z-index: 0;
}}
.hero-wrapper::before {{ top: -10%; left: 15%; }}
.hero-wrapper::after {{ bottom: -10%; right: 15%; background: radial-gradient(circle, rgba(105,240,174,0.06) 0%, transparent 60%); animation-duration: 15s; animation-direction: alternate-reverse; }}
@keyframes floatShape {{ 0% {{ transform: translate(0, 0) scale(1); }} 100% {{ transform: translate(22px, -33px) scale(1.3); }} }}
.hero-text-light {{ position: relative; z-index: 1; font-size: 1.87rem; font-weight: 600; color: {text_color} !important; line-height: 1.25; }}
.hero-text-cyan {{ position: relative; z-index: 1; font-size: 2.2rem; font-weight: 700; color: {cyan_color} !important; line-height: 1.15; font-style: italic; }}
.text-accent {{ color: {accent_color} !important; font-style: italic; }}
.standard-pane {{ background-color: {card_color}; padding: 16px; border-radius: 6px; border: 1px solid {border_color}; }}
.standard-pane, .standard-pane p, .standard-pane strong, .standard-pane div {{ font-family: 'Arial', sans-serif !important; font-size: 0.55rem !important; color: #8b949e !important; }}

.mega-footer {{
    display: flex; justify-content: space-around; background-color: {card_color}; padding: 22px 11px; border-top: 1px solid {border_color};
    margin-top: 33px; border-radius: 6px;
}}
.footer-col {{ display: flex; flex-direction: column; text-align: left; }}
.footer-col h4 {{ color: #FFFFFF !important; font-size: 0.57rem; margin-bottom: 8px; font-weight: 600; font-family: 'OpenDyslexic', 'Figtree', sans-serif !important;}}
.footer-col a {{ color: #9AA0A6 !important; text-decoration: none; font-size: 0.49rem; margin-bottom: 5px; transition: color 0.2s, transform 0.2s; }}
.footer-col a:hover {{ color: {cyan_color} !important; transform: translateX(2px); }}

/* --- HERO --- */
.hero-eyebrow {{
    font-family: 'OpenDyslexic', 'Figtree', sans-serif; font-size: 0.44rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: {accent_color}; margin-bottom: 7px;
}}
.hero-copy h1 {{
    font-family: 'OpenDyslexic', 'Fraunces', Georgia, serif !important; font-size: 1.7rem; line-height: 1.12;
    font-weight: 600 !important; margin: 0 0 9px 0 !important; color: {text_color} !important; text-align: left;
}}
.hero-copy h1 em {{ font-style: italic; color: {cyan_color}; font-weight: 700; }}
.hero-copy p {{ font-size: 0.59rem; color: #9AA0A6 !important; max-width: 253px; margin-bottom: 15px !important; text-align: left; }}
.cta-btn {{
    display: inline-block; background-color: {cyan_color}; color: #0E1117 !important; text-decoration: none !important;
    font-family: 'OpenDyslexic', 'Figtree', sans-serif; font-weight: 700; font-size: 0.55rem; padding: 7px 15px; border-radius: 4px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.cta-btn:hover {{ transform: translateY(-1px); box-shadow: 0 4px 11px rgba(0,229,255,0.3); }}
.cta-sub {{ font-size: 0.45rem; color: #6D6558; margin-top: 5px; }}

/* --- SIGNATURE --- */
.stack-wrap {{ position: relative; height: 220px; }}
.stack-back {{
    position: absolute; top: 5px; left: 16px; width: 78%; padding: 14px 16px; border-radius: 5px;
    background-color: {card_color}; border: 1px solid {border_color}; transform: rotate(-7deg);
    box-shadow: 0 6px 13px rgba(0,0,0,0.35); opacity: 0.7;
}}
.stack-back p {{ font-family: 'Arial', sans-serif !important; font-size: 0.45rem !important; line-height: 1.6 !important; color: #857D6E !important; margin: 0 !important; }}
.stack-back .stack-label {{ font-family: 'OpenDyslexic', 'Figtree', sans-serif; font-size: 0.38rem; font-weight: 700; color: #6D6558; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 5px; display: block; }}
.stack-front {{
    position: absolute; top: 30px; left: 0; width: 82%; padding: 16px 18px; border-radius: 3px 8px 8px 3px;
    background-color: {paper_bg}; border: 1px solid {paper_border}; transform: rotate(3deg);
    box-shadow: 0 11px 22px rgba(0,0,0,0.45);
}}
.stack-front::after {{
    content: ''; position: absolute; top: 0; right: 0; width: 0; height: 0;
    border-style: solid; border-width: 0 12px 12px 0; border-color: transparent #DCCEA4 transparent transparent;
}}
.stack-front .stack-label {{ font-family: 'OpenDyslexic', 'Figtree', sans-serif; font-size: 0.38rem; font-weight: 700; color: {paper_accent}; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 5px; display: block; }}
.stack-front p {{ font-family: 'OpenDyslexic', sans-serif !important; font-size: 0.55rem !important; line-height: 1.75 !important; color: {paper_ink} !important; margin: 0 !important; }}
.stack-pill {{
    position: absolute; bottom: 9px; right: 6%; background-color: {accent_color}; color: #0E1117;
    font-family: 'OpenDyslexic', 'Figtree', sans-serif; font-weight: 700; font-size: 0.42rem; padding: 3px 8px 3px 6px;
    border-radius: 11px; box-shadow: 0 4px 9px rgba(0,0,0,0.35); z-index: 5;
}}

/* --- FEATURE CARDS --- */
.feature-grid {{ display: flex; gap: 11px; margin-top: 5px; }}
.feature-card {{
    flex: 1; background-color: {card_color}; border: 1px solid {border_color}; border-left: 1px solid var(--accent, {cyan_color});
    border-radius: 5px; padding: 13px 12px; transition: transform 0.2s ease, border-color 0.2s ease;
}}
.feature-card:hover {{ transform: translateY(-2px); }}
.feature-icon {{
    width: 23px; height: 23px; border-radius: 5px; display: flex; align-items: center; justify-content: center;
    font-size: 0.66rem; background-color: rgba(255,255,255,0.06); margin-bottom: 7px;
}}
.feature-card h4 {{ font-family: 'OpenDyslexic', 'Fraunces', Georgia, serif !important; font-size: 0.59rem; margin: 0 0 4px 0 !important; color: {text_color} !important; }}
.feature-card p {{ font-size: 0.48rem; color: #9AA0A6 !important; margin: 0 !important; line-height: 1.55; }}

/* --- MISSION --- */
.mission-block {{ border-left: 1px solid {cyan_color}; padding-left: 14px; }}
.mission-block .kicker {{ font-family: 'OpenDyslexic', 'Figtree', sans-serif; font-size: 0.42rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: {accent_color}; margin-bottom: 5px; }}
.mission-block p {{ font-size: 0.55rem; color: #C9C0AE !important; line-height: 1.7; margin-bottom: 7px !important; }}
.mission-block p:first-of-type {{ font-family: 'OpenDyslexic', 'Fraunces', Georgia, serif; font-size: 0.68rem; color: {text_color} !important; font-style: italic; }}

/* --- AUTH CARD --- */
.auth-card-header {{ text-align: center; margin-bottom: 12px; }}
.auth-card-header .icon-badge {{
    width: 28px; height: 28px; border-radius: 50%; background-color: rgba(0,229,255,0.12); border: 1px solid {cyan_color};
    display: flex; align-items: center; justify-content: center; font-size: 0.77rem; margin: 0 auto 7px auto;
    overflow: hidden;
}}
.auth-card-header .icon-badge img {{ width: 100%; height: 100%; object-fit: cover; }}
.auth-card-header h3 {{ margin: 0 0 2px 0 !important; }}
.auth-card-header p {{ color: #9AA0A6 !important; font-size: 0.49rem; margin: 0 !important; }}
div[class*="st-key-auth_card"] {{
    background-color: {card_color} !important;
    border: 1px solid {border_color} !important;
    border-radius: 8px !important;
    padding: 18px 20px 13px 20px !important;
    box-shadow: 0 7px 16px rgba(0,0,0,0.4);
}}

/* ======================================================================
   WORKSPACE (post-login) — SCALED DOWN AND CLEANED UP
   ====================================================================== */

[data-testid="stMain"] .block-container {{
    padding-top: 35px !important; 
    padding-bottom: 10px !important;
}}

[data-testid="stMain"] {{
    background-color: {bg_color};
}}
[data-testid="stMain"] button[kind="primary"]:hover {{
    background-color: {accent_color} !important; transform: none !important; box-shadow: none !important;
}}

.ws-topbar {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 0 2px 8px 2px; margin-bottom: 3px; border-bottom: 1px solid {border_color};
    flex-wrap: wrap; gap: 8px;
}}
.ws-greeting-title {{
    font-family: 'OpenDyslexic', 'Fraunces', Georgia, serif !important; 
    font-size: 22px !important; 
    font-weight: 700 !important;
    color: {text_color} !important; margin: 0 !important; line-height: 1.2;
}}
.ws-doc-chip {{
    display: flex; align-items: center; gap: 5px; background: {card_color};
    border: 1px solid {border_color}; border-radius: 5px; padding: 4px 6px 4px 4px;
}}
.ws-doc-chip .dot {{
    width: 14px; height: 14px; border-radius: 4px; display:flex; align-items:center; justify-content:center;
    background: rgba(0,229,255,0.10); font-size: 10px; flex-shrink: 0;
}}
.ws-doc-chip .doc-meta {{ line-height: 1.15; }}
.ws-doc-chip .doc-meta .lbl {{ font-size: 9px; color: #6D7280; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700; }}
.ws-doc-chip .doc-meta .val {{ font-size: 12px; color: {text_color}; font-weight: 600; max-width: 110px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}

/* --- ACTION ROW BUTTONS IN WORKSPACE --- */
[data-testid="stMain"] .stButton button {{
    padding: 6px 8px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    border-radius: 4px !important;
    min-height: 26px !important;
}}

/* --- UPLOAD DROPZONE --- */
[data-testid="stFileUploaderDropzone"] {{
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    padding: 8px !important;
    min-height: 45px !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"] span {{
    font-size: 10px !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"] small,
[data-testid="stFileUploaderDropzoneInstructions"] div {{
    font-size: 8px !important;
    color: #6D7280 !important;
}}
[data-testid="stFileUploaderDropzone"] svg {{
    width: 14px !important;
    height: 14px !important;
}}
[data-testid="stFileUploaderDropzone"] button {{
    padding: 2px 6px !important;
    font-size: 9px !important;
    min-height: auto !important;
    margin-top: 2px !important;
}}

.content-stats {{
    display: flex; gap: 4px; margin: 8px 0 6px 0; flex-wrap: wrap; justify-content: center;
}}
.stat-chip {{
    background: {card_color}; border: 1px solid {border_color}; border-radius: 3px;
    padding: 3px 6px; font-size: 9px; color: #9AA0A6; font-family: 'OpenDyslexic', 'Figtree', sans-serif; font-weight: 500;
}}
.stat-chip b {{ color: {cyan_color}; font-weight: 700; }}

/* --- SIDEBAR --- */
.sb-brand {{ display:flex; align-items:center; gap:6px; margin-bottom: 12px; }}
.sb-brand .logo-dot {{ width:14px; height:14px; border-radius:50%; background: linear-gradient(135deg, {cyan_color}, {accent_color}); flex-shrink:0; }}
.sb-brand .name {{ font-family:'OpenDyslexic', 'Fraunces', Georgia, serif; font-style: italic; font-weight:700; font-size:12px; color:#FFFFFF; }}
.sb-section-label {{
    color: #6D7280 !important; font-size: 9px !important; font-weight: 700 !important; text-transform: uppercase;
    letter-spacing: 0.08em; margin: 12px 0 6px 2px; display:block; font-family: 'OpenDyslexic', 'Figtree', sans-serif !important;
}}
[data-testid="stSidebar"] [data-testid="stFileUploader"] {{ padding: 4px; }}
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {{ padding-top: 2px; }}

[data-testid="stSidebar"] button[kind="secondary"] {{
    border-radius: 4px !important; margin-bottom: 2px !important;
}}
[data-testid="stSidebar"] button[kind="secondary"]:hover {{ background-color: rgba(0,229,255,0.08) !important; }}

/* Profile popover inner styling */
div[data-testid="stPopoverBody"] {{
    background-color: {card_color} !important;
    border: 1px solid {border_color} !important;
}}
</style>
"""
    st.markdown(dynamic_css, unsafe_allow_html=True)


def inject_workspace_css():
    """Workspace-wide readability tweaks applied on top of the base font."""
    st.markdown("""
    <style>
    .stApp *:not([data-testid="stIconMaterial"]):not([class*="material-icons"]):not([class*="material-symbols"]),
    .stApp {
        font-family: 'OpenDyslexic', 'Figtree', sans-serif !important;
    }
    [data-testid="stIconMaterial"],
    [class*="material-icons"],
    [class*="material-symbols"] {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
    }

    [data-testid="stTextInput"] input {
        font-size: 13px !important;
        padding-top: 4px !important;
        padding-bottom: 4px !important;
    }
    [data-testid="stTextInput"] input::placeholder {
        font-size: 13px !important;
    }
    
    /* Make the Sidebar inputs and fonts perfectly scaled down to fit */
    [data-testid="stSidebar"] [data-testid="stTextInput"] input,
    [data-testid="stSidebar"] [data-testid="stTextInput"] input::placeholder {
        font-size: 10px !important;
        padding-top: 2px !important;
        padding-bottom: 2px !important;
    }

    .stApp p, .stApp li, .stApp label, .stApp span, .stApp div,
    [data-testid="stMarkdownContainer"] p {
        letter-spacing: 0.01em;
        line-height: 1.65 !important;
    }
    .stApp label, [data-testid="stWidgetLabel"] p {
        font-size: 12px !important;
    }
    
    /* Target the text inside sidebar buttons strictly to 10px */
    [data-testid="stSidebar"] button p { 
        font-size: 10px !important; 
    }
    </style>
    """, unsafe_allow_html=True)


def inject_reading_pane_size_css(font_size, line_spacing):
    """Applies the user's font-size / line-spacing sliders to the reading pane."""
    st.markdown(f"""
    <style>
        .reading-pane, .reading-pane p, .reading-pane li, .reading-pane span {{
            font-size: {font_size}px !important;
            line-height: {line_spacing} !important;
        }}
    </style>
    """, unsafe_allow_html=True)