import streamlit as st

from config import (
    bg_color, text_color, card_color, cyan_color, accent_color, border_color,
    paper_bg, paper_ink, paper_border, paper_accent,
)


def inject_global_css(logo_src):
    """The full app stylesheet — landing page, auth card, workspace shell,
    sidebar, reading pane. Unchanged from the original single-file app.
    logo_src is needed for the sidebar collapse-control background image."""
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

/* --- TYPOGRAPHY: serif display paired with a humanist sans body --- */
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
[data-testid="stUploadedFile"] {{ border: 1px solid #5A5E73 !important; border-radius: 8px !important; background-color: #222530 !important; }}
[data-testid="stAlert"] {{ background-color: rgba(105, 240, 174, 0.15) !important; border: 1px solid {accent_color} !important; color: #FFFFFF !important; }}

/* --- DASHBOARD CARD CONTAINERS --- */
.dashboard-card {{
    background: rgba(30, 28, 41, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    margin-bottom: 25px;
}}

/* --- FILE UPLOADER REFINEMENT --- */
[data-testid="stFileUploader"] {{
    background: rgba(14, 17, 23, 0.9);
    border: 1px dashed rgba(0, 229, 255, 0.4) !important;
    border-radius: 12px;
    padding: 10px;
}}

/* --- TABS POLISH --- */
.stTabs [data-baseweb="tab-list"] {{ gap: 8px; background-color: transparent; }}
.stTabs [data-baseweb="tab"] {{ background-color: rgba(30, 28, 41, 0.7); border-radius: 8px 8px 0 0; color: #8b949e; padding: 10px 20px; border: 1px solid {border_color}; }}
.stTabs [aria-selected="true"] {{ background-color: rgba(0, 229, 255, 0.12) !important; color: {cyan_color} !important; border-color: rgba(0, 229, 255, 0.4) !important; }}

/* --- READING PANE: a warm page, not another dark card --- */
.reading-pane {{
    position: relative;
    background-color: {paper_bg};
    padding: 40px 60px;
    border-radius: 6px 12px 12px 6px;
    box-shadow: 0 14px 34px rgba(0,0,0,0.35), inset 0 0 0 1px {paper_border};
    border: 1px solid {paper_border};
    transition: all 0.3s ease;
}}
/* folded page corner — the recurring visual signature of "this is a page you can actually read" */
.reading-pane::after {{
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 0; height: 0;
    border-style: solid;
    border-width: 0 26px 26px 0;
    border-color: transparent #DCCEA4 transparent transparent;
    filter: drop-shadow(-2px 2px 3px rgba(0,0,0,0.18));
    border-top-right-radius: 6px;
}}
.reading-pane, .reading-pane p, .reading-pane li, .reading-pane div, .reading-pane span, .reading-pane h1, .reading-pane h2, .reading-pane h3 {{
    font-family: 'OpenDyslexic', sans-serif !important;
    letter-spacing: 0.02em !important;
    color: {paper_ink} !important;
}}
.reading-pane p, .reading-pane li {{ line-height: 1.85 !important; margin-bottom: 14px !important; }}
.reading-pane strong, .reading-pane b {{ font-family: 'OpenDyslexic', sans-serif !important; font-weight: 700 !important; color: {paper_accent} !important; }}
.reading-pane h1, .reading-pane h2, .reading-pane h3 {{ margin-bottom: 20px !important; border-bottom: 1px solid {paper_border}; padding-bottom: 10px; }}
.reading-container {{ max-width: 900px; margin: 0 auto; }}
.badge {{ background-color: {border_color}; color: {cyan_color}; padding: 4px 12px; border-radius: 15px; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.03em; margin-bottom: 15px; display: inline-block; font-family: 'OpenDyslexic', 'Figtree', sans-serif !important; }}

/* --- CUSTOM TOP NAVBAR (legacy / unused variant, kept in sync) --- */
.custom-navbar {{
    position: fixed; top: 0; left: 0; width: 100%; background-color: rgba(19, 18, 26, 0.85); backdrop-filter: blur(10px);
    display: flex; justify-content: space-between; align-items: center; padding: 10px 50px; z-index: 99999; border-bottom: 1px solid {border_color};
}}
.nav-left {{ display: flex; align-items: center; gap: 12px; }}
.nav-logo {{ width: 36px; height: 36px; border-radius: 50%; object-fit: cover; border: 2px solid {cyan_color}; }}
.nav-title {{ font-size: 1.2rem; font-weight: bold; color: {text_color}; letter-spacing: 1px; }}
.nav-login-btn {{
    background-color: transparent; color: {text_color}; border: 1px solid {cyan_color};
    padding: 6px 20px; border-radius: 25px; text-decoration: none !important; font-weight: bold; transition: all 0.3s ease;
}}
.nav-login-btn:hover {{ background-color: {cyan_color}; color: #0E1117; box-shadow: 0 0 15px rgba(0, 229, 255, 0.4); }}

/* --- PRIMARY BUTTON STYLING --- */
button[kind="primary"] {{
    background-color: {cyan_color} !important;
    border: none !important;
    font-weight: 600 !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
button[kind="primary"] * {{ color: #0E1117 !important; }}
button[kind="primary"]:hover {{
    background-color: {accent_color} !important; transform: translateY(-3px); box-shadow: 0 6px 15px rgba(0, 229, 255, 0.25);
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
    width: 36px !important;
    height: 36px !important;
    border: 2px solid {cyan_color};
    margin-top: 10px;
    margin-left: 15px;
    transition: transform 0.2s ease;
    z-index: 999999 !important;
}}
[data-testid="collapsedControl"]:hover {{
    transform: scale(1.1);
}}
[data-testid="stSidebar"] {{ background-color: #13151C !important; border-right: 1px solid {border_color}; }}
[data-testid="stSidebar"] button[kind="secondary"] {{
    background-color: transparent !important; border: none !important; justify-content: flex-start !important; 
    padding: 8px 10px !important; box-shadow: none !important;
}}
[data-testid="stSidebar"] button[kind="secondary"]:hover {{ background-color: #1E212B !important; }}
[data-testid="stSidebar"] button[kind="secondary"] p {{ color: {text_color} !important; font-size: 14.5px !important; }}

/* --- LANDING PAGE ANIMATIONS --- */
@keyframes fadeUp {{ 0% {{ opacity: 0; transform: translateY(20px); }} 100% {{ opacity: 1; transform: translateY(0); }} }}
.hero-wrapper {{ padding: 3rem 0 2rem 0; margin-top: 60px; text-align: center; animation: fadeUp 1s ease-out; position: relative; overflow: hidden; }}
.hero-wrapper::before, .hero-wrapper::after {{
    content: ''; position: absolute; width: 250px; height: 250px;
    background: radial-gradient(circle, rgba(0,229,255,0.07) 0%, transparent 60%); border-radius: 50%;
    animation: floatShape 12s infinite alternate ease-in-out; z-index: 0;
}}
.hero-wrapper::before {{ top: -10%; left: 15%; }}
.hero-wrapper::after {{ bottom: -10%; right: 15%; background: radial-gradient(circle, rgba(105,240,174,0.06) 0%, transparent 60%); animation-duration: 15s; animation-direction: alternate-reverse; }}
@keyframes floatShape {{ 0% {{ transform: translate(0, 0) scale(1); }} 100% {{ transform: translate(40px, -60px) scale(1.3); }} }}
.hero-text-light {{ position: relative; z-index: 1; font-size: 3.4rem; font-weight: 600; color: {text_color} !important; line-height: 1.25; }}
.hero-text-cyan {{ position: relative; z-index: 1; font-size: 4rem; font-weight: 700; color: {cyan_color} !important; line-height: 1.15; font-style: italic; }}
.text-accent {{ color: {accent_color} !important; font-style: italic; }}
.standard-pane {{ background-color: {card_color}; padding: 30px; border-radius: 12px; border: 1px solid {border_color}; }}
.standard-pane, .standard-pane p, .standard-pane strong, .standard-pane div {{ font-family: 'Arial', sans-serif !important; font-size: 1rem !important; color: #8b949e !important; }}
.mega-footer {{
    display: flex; justify-content: space-around; background-color: {card_color}; padding: 40px 20px; border-top: 1px solid {border_color};
    margin-top: 60px; border-radius: 12px;
}}
.footer-col {{ display: flex; flex-direction: column; text-align: left; }}
.footer-col h4 {{ color: #FFFFFF !important; font-size: 1.05rem; margin-bottom: 15px; font-weight: 600; font-family: 'OpenDyslexic', 'Figtree', sans-serif !important;}}
.footer-col a {{ color: #9AA0A6 !important; text-decoration: none; font-size: 0.9rem; margin-bottom: 10px; transition: color 0.2s, transform 0.2s; }}
.footer-col a:hover {{ color: {cyan_color} !important; transform: translateX(5px); }}

/* --- HERO: asymmetric split, not a centered stack --- */
.hero-eyebrow {{
    font-family: 'OpenDyslexic', 'Figtree', sans-serif; font-size: 0.8rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: {accent_color}; margin-bottom: 14px;
}}
.hero-copy h1 {{
    font-family: 'OpenDyslexic', 'Fraunces', Georgia, serif !important; font-size: 3.1rem; line-height: 1.12;
    font-weight: 600 !important; margin: 0 0 18px 0 !important; color: {text_color} !important; text-align: left;
}}
.hero-copy h1 em {{ font-style: italic; color: {cyan_color}; font-weight: 700; }}
.hero-copy p {{ font-size: 1.08rem; color: #9AA0A6 !important; max-width: 460px; margin-bottom: 28px !important; text-align: left; }}
.cta-btn {{
    display: inline-block; background-color: {cyan_color}; color: #0E1117 !important; text-decoration: none !important;
    font-family: 'OpenDyslexic', 'Figtree', sans-serif; font-weight: 700; font-size: 1rem; padding: 13px 28px; border-radius: 8px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.cta-btn:hover {{ transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,229,255,0.3); }}
.cta-sub {{ font-size: 0.82rem; color: #6D6558; margin-top: 10px; }}

/* --- SIGNATURE: overlapping page-stack showing the actual transformation --- */
.stack-wrap {{ position: relative; height: 400px; }}
.stack-back {{
    position: absolute; top: 10px; left: 30px; width: 78%; padding: 26px 30px; border-radius: 10px;
    background-color: {card_color}; border: 1px solid {border_color}; transform: rotate(-7deg);
    box-shadow: 0 12px 24px rgba(0,0,0,0.35); opacity: 0.7;
}}
.stack-back p {{ font-family: 'Arial', sans-serif !important; font-size: 0.82rem !important; line-height: 1.6 !important; color: #857D6E !important; margin: 0 !important; }}
.stack-back .stack-label {{ font-family: 'OpenDyslexic', 'Figtree', sans-serif; font-size: 0.7rem; font-weight: 700; color: #6D6558; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 10px; display: block; }}
.stack-front {{
    position: absolute; top: 55px; left: 0; width: 82%; padding: 30px 34px; border-radius: 6px 16px 16px 6px;
    background-color: {paper_bg}; border: 1px solid {paper_border}; transform: rotate(3deg);
    box-shadow: 0 20px 40px rgba(0,0,0,0.45);
}}
.stack-front::after {{
    content: ''; position: absolute; top: 0; right: 0; width: 0; height: 0;
    border-style: solid; border-width: 0 22px 22px 0; border-color: transparent #DCCEA4 transparent transparent;
}}
.stack-front .stack-label {{ font-family: 'OpenDyslexic', 'Figtree', sans-serif; font-size: 0.7rem; font-weight: 700; color: {paper_accent}; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 10px; display: block; }}
.stack-front p {{ font-family: 'OpenDyslexic', sans-serif !important; font-size: 1rem !important; line-height: 1.75 !important; color: {paper_ink} !important; margin: 0 !important; }}
.stack-pill {{
    position: absolute; bottom: 18px; right: 6%; background-color: {accent_color}; color: #0E1117;
    font-family: 'OpenDyslexic', 'Figtree', sans-serif; font-weight: 700; font-size: 0.78rem; padding: 7px 16px 7px 12px;
    border-radius: 20px; box-shadow: 0 8px 18px rgba(0,0,0,0.35); z-index: 5;
}}

/* --- FEATURE CARDS: color-coded by function, not a bullet dump --- */
.feature-grid {{ display: flex; gap: 20px; margin-top: 10px; }}
.feature-card {{
    flex: 1; background-color: {card_color}; border: 1px solid {border_color}; border-left: 3px solid var(--accent, {cyan_color});
    border-radius: 10px; padding: 24px 22px; transition: transform 0.2s ease, border-color 0.2s ease;
}}
.feature-card:hover {{ transform: translateY(-4px); }}
.feature-icon {{
    width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem; background-color: rgba(255,255,255,0.06); margin-bottom: 14px;
}}
.feature-card h4 {{ font-family: 'OpenDyslexic', 'Fraunces', Georgia, serif !important; font-size: 1.08rem; margin: 0 0 8px 0 !important; color: {text_color} !important; }}
.feature-card p {{ font-size: 0.88rem; color: #9AA0A6 !important; margin: 0 !important; line-height: 1.55; }}

/* --- MISSION: editorial block with a spine, not two plain paragraphs --- */
.mission-block {{ border-left: 3px solid {cyan_color}; padding-left: 26px; }}
.mission-block .kicker {{ font-family: 'OpenDyslexic', 'Figtree', sans-serif; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: {accent_color}; margin-bottom: 10px; }}
.mission-block p {{ font-size: 1rem; color: #C9C0AE !important; line-height: 1.7; margin-bottom: 14px !important; }}
.mission-block p:first-of-type {{ font-family: 'OpenDyslexic', 'Fraunces', Georgia, serif; font-size: 1.25rem; color: {text_color} !important; font-style: italic; }}

/* --- AUTH CARD: a real panel instead of bare inputs on the page --- */
.auth-card-header {{ text-align: center; margin-bottom: 22px; }}
.auth-card-header .icon-badge {{
    width: 52px; height: 52px; border-radius: 50%; background-color: rgba(0,229,255,0.12); border: 1px solid {cyan_color};
    display: flex; align-items: center; justify-content: center; font-size: 1.4rem; margin: 0 auto 14px auto;
    overflow: hidden;
}}
.auth-card-header .icon-badge img {{ width: 100%; height: 100%; object-fit: cover; }}
.auth-card-header h3 {{ margin: 0 0 4px 0 !important; }}
.auth-card-header p {{ color: #9AA0A6 !important; font-size: 0.9rem; margin: 0 !important; }}
/* Real Streamlit container (st.container(border=True, key="auth_card")) —
   replaces the old manually-opened/closed <div class="auth-card"> which
   rendered as an empty styled bar because the two markdown() calls that
   opened and closed it were separate, unnested DOM siblings. */
div[class*="st-key-auth_card"] {{
    background-color: {card_color} !important;
    border: 1px solid {border_color} !important;
    border-radius: 16px !important;
    padding: 34px 38px 24px 38px !important;
    box-shadow: 0 14px 30px rgba(0,0,0,0.4);
}}

/* ======================================================================
   WORKSPACE (post-login) — everything below is scoped to the dashboard,
   the landing page above is untouched.
   ====================================================================== */

/* --- App shell background: flat and calm, not competing gradients --- */
[data-testid="stMain"] {{
    background-color: {bg_color};
}}

/* Reduce hover motion in the workspace — sudden lift/glow on every
   button is exactly the kind of visual noise that breaks focus for
   ADHD readers. Keep it on the landing page (outside stMain). */
[data-testid="stMain"] button[kind="primary"]:hover {{
    background-color: {accent_color} !important; transform: none !important; box-shadow: none !important;
}}
[data-testid="stMain"] .feature-card:hover {{ transform: none; }}

/* --- Workspace top bar: greeting + live doc status, replaces the bare avatar row --- */
.ws-topbar {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 4px 4px 20px 4px; margin-bottom: 6px; border-bottom: 1px solid {border_color};
}}
.ws-greeting-eyebrow {{
    font-family: 'OpenDyslexic', 'Figtree', sans-serif; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: {accent_color}; margin-bottom: 4px;
}}
.ws-greeting-title {{
    font-family: 'OpenDyslexic', 'Fraunces', Georgia, serif !important; font-size: 1.5rem; font-weight: 700 !important;
    color: {text_color} !important; margin: 0 !important; line-height: 1.2;
}}
.ws-doc-chip {{
    display: flex; align-items: center; gap: 10px; background: {card_color};
    border: 1px solid {border_color}; border-radius: 10px; padding: 8px 16px 8px 8px;
}}
.ws-doc-chip .dot {{
    width: 28px; height: 28px; border-radius: 8px; display:flex; align-items:center; justify-content:center;
    background: rgba(0,229,255,0.10); font-size: 0.9rem; flex-shrink: 0;
}}
.ws-doc-chip .doc-meta {{ line-height: 1.15; }}
.ws-doc-chip .doc-meta .lbl {{ font-size: 0.68rem; color: #6D7280; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700; }}
.ws-doc-chip .doc-meta .val {{ font-size: 0.86rem; color: {text_color}; font-weight: 600; max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}

/* --- Action row: the two main buttons, centered and sized up since
   these are the primary actions on the page (no card wrapper — the old
   one rendered as an empty bar, see the upload-dropzone fix note). --- */
[data-testid="stMain"] .stButton button {{
    padding: 1rem 1.6rem !important;
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    border-radius: 12px !important;
    min-height: 3.6rem !important;
}}

/* --- Upload dropzone: compact, centered, no file-size fine print --- */
[data-testid="stFileUploaderDropzone"] {{
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    padding: 20px 24px !important;
    min-height: 100px !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"] {{
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"] span {{
    font-size: 1.05rem !important;
}}
/* The "Limit 200MB per file • PDF" fine print — not needed on screen. */
[data-testid="stFileUploaderDropzoneInstructions"] small {{
    display: none !important;
}}
[data-testid="stFileUploaderDropzone"] svg {{
    width: 32px !important;
    height: 32px !important;
}}
[data-testid="stFileUploaderDropzone"] button {{
    padding: 0.7rem 1.3rem !important;
    font-size: 1rem !important;
    min-height: auto !important;
    margin-top: 6px !important;
}}

/* --- Content stats strip above the reading tabs: kept to the essentials
   (word count + simplify status) — font size/spacing are already visible
   as sidebar sliders, repeating them here was just more numbers to scan --- */
.content-stats {{
    display: flex; gap: 10px; margin: 22px 0 16px 0; flex-wrap: wrap; justify-content: center;
}}
.stat-chip {{
    background: {card_color}; border: 1px solid {border_color}; border-radius: 8px;
    padding: 6px 14px; font-size: 0.82rem; color: #9AA0A6; font-family: 'OpenDyslexic', 'Figtree', sans-serif; font-weight: 500;
}}
.stat-chip b {{ color: {cyan_color}; font-weight: 700; }}

/* --- Sidebar: section cards instead of a flat stack of widgets --- */
[data-testid="stSidebar"] .block-container {{ padding-top: 1.2rem; }}
.sb-brand {{ display:flex; align-items:center; gap:10px; margin-bottom: 18px; }}
.sb-brand .logo-dot {{ width:30px; height:30px; border-radius:50%; background: linear-gradient(135deg, {cyan_color}, {accent_color}); flex-shrink:0; }}
.sb-brand .name {{ font-family:'OpenDyslexic', 'Fraunces', Georgia, serif; font-style: italic; font-weight:700; font-size:1.08rem; color:#FFFFFF; }}
.sb-section-label {{
    color: #6D7280 !important; font-size: 0.72rem !important; font-weight: 700 !important; text-transform: uppercase;
    letter-spacing: 0.08em; margin: 18px 0 8px 2px; display:block; font-family: 'OpenDyslexic', 'Figtree', sans-serif !important;
}}
[data-testid="stSidebar"] [data-testid="stFileUploader"] {{ padding: 6px; }}
[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {{ padding-top: 4px; }}

/* Recent-document buttons: give the active/hover state some presence */
[data-testid="stSidebar"] button[kind="secondary"] {{
    border-radius: 8px !important; margin-bottom: 2px !important;
}}
[data-testid="stSidebar"] button[kind="secondary"]:hover {{ background-color: rgba(0,229,255,0.08) !important; }}

/* Sidebar profile footer card */
.sb-profile-card {{
    background: rgba(255,255,255,0.03); border: 1px solid {border_color}; border-radius: 12px;
    padding: 10px 12px; margin-top: 10px; display:flex; align-items:center; gap: 10px;
}}
</style>
"""
    st.markdown(dynamic_css, unsafe_allow_html=True)


def inject_workspace_css():
    """Workspace-wide readability tweaks applied on top of the base font,
    widened to catch popovers/toasts/tooltips too. Only used post-login."""
    st.markdown("""
    <style>
    /* .stApp wraps the entire rendered page (including popovers, toasts,
       tooltips) so this reaches further than just the main/sidebar
       containers used before. Icon elements are excluded — Streamlit
       renders its sidebar-collapse arrow, expander chevron, and upload
       icon as ligature text through a dedicated icon font, and forcing
       those into OpenDyslexic breaks the ligature so the raw icon name
       ("keyboard_double_arrow_left", "expand_more"...) shows up as
       literal, overlapping text instead of a small glyph. */
    .stApp *:not([data-testid="stIconMaterial"]):not([class*="material-icons"]):not([class*="material-symbols"]),
    .stApp {
        font-family: 'OpenDyslexic', 'Figtree', sans-serif !important;
    }
    [data-testid="stIconMaterial"],
    [class*="material-icons"],
    [class*="material-symbols"] {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
    }

    /* Small UI text tends to get squeezed by default Streamlit styling —
       give it room to breathe so it reads as easily as the big pane does. */
    .stApp p, .stApp li, .stApp label, .stApp span, .stApp div,
    [data-testid="stMarkdownContainer"] p {
        letter-spacing: 0.01em;
        line-height: 1.65 !important;
    }
    .stApp label, [data-testid="stWidgetLabel"] p {
        font-size: 0.95rem !important;
    }
    .stat-chip, .badge, .toolbar-label, .sb-section-label, .ws-doc-chip .lbl {
        font-size: 0.85rem !important;
        letter-spacing: 0.02em !important;
    }
    .ws-doc-chip .val { font-size: 0.95rem !important; }
    [data-testid="stSidebar"] button p { font-size: 0.95rem !important; }
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