import streamlit as st
import sqlite3
import base64
import os
import requests  
import markdown 
import json
import re
import streamlit.components.v1 as components

# Backend URL pointing to your running FastAPI server
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Readora AI", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

def get_image_base64(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "logo readora ai.jpeg")
logo_b64 = get_image_base64(logo_path)

# 1. DEFINED ONCE GLOBALLY HERE
logo_src = f"data:image/jpeg;base64,{logo_b64}" if logo_b64 else "https://via.placeholder.com/45"

conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, doc_name TEXT, original_text TEXT, simplified_text TEXT)')
conn.commit()

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""
if 'simplified_text' not in st.session_state:
    st.session_state.simplified_text = ""
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'current_doc_id' not in st.session_state:
    st.session_state.current_doc_id = None
if 'profile_photo' not in st.session_state:
    st.session_state.profile_photo = None
if 'font_size' not in st.session_state:
    st.session_state.font_size = 22
if 'line_spacing' not in st.session_state:
    st.session_state.line_spacing = 1.8

bg_color = "#0E1117"
text_color = "#E0E0E0"
card_color = "#1A1C23"
cyan_color = "#00E5FF"
accent_color = "#69F0AE"
border_color = "#2D303E"

dynamic_css = f"""
<style>
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

/* --- TYPOGRAPHY HIERARCHY --- */
html, body, [class*="css"], p, li, label, .stMarkdown, h1, h2, h3, h4, h5, h6, .nav-title {{
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
    color: {text_color} !important;
}}
h1, h2, h3, h4, h5, h6, .nav-title {{ font-weight: 700 !important; }}
.hero-text-light, .hero-text-cyan {{ font-family: 'Inter', 'Segoe UI', sans-serif !important; }}

/* --- UPGRADED ACCESSIBILITY TWEAKS --- */
[data-testid="stUploadedFile"] {{ border: 1px solid #5A5E73 !important; border-radius: 8px !important; background-color: #222530 !important; }}
[data-testid="stAlert"] {{ background-color: rgba(105, 240, 174, 0.15) !important; border: 1px solid {accent_color} !important; color: #FFFFFF !important; }}

/* --- READING PANE DESIGN --- */
.reading-pane {{
    background-color: {card_color}; 
    padding: 40px 60px;
    border-radius: 12px; 
    box-shadow: 0px 8px 16px rgba(0,0,0,0.1);
    border: 1px solid {border_color}; 
    transition: all 0.3s ease;
}}
.reading-pane, .reading-pane p, .reading-pane li, .reading-pane div, .reading-pane span, .reading-pane h1, .reading-pane h2, .reading-pane h3 {{
    font-family: 'OpenDyslexic', sans-serif !important;
    letter-spacing: normal !important; 
    color: {text_color} !important;
}}
.reading-pane strong, .reading-pane b {{ font-family: 'OpenDyslexic', sans-serif !important; font-weight: 700 !important; color: {cyan_color} !important; }}
.reading-pane h1, .reading-pane h2, .reading-pane h3 {{ margin-bottom: 20px !important; border-bottom: 1px solid {border_color}; padding-bottom: 10px; }}
.reading-container {{ max-width: 900px; margin: 0 auto; }}
.badge {{ background-color: #2D303E; color: {cyan_color}; padding: 4px 12px; border-radius: 15px; font-size: 0.85rem; font-weight: bold; margin-bottom: 15px; display: inline-block; }}

/* --- CUSTOM TOP NAVBAR --- */
.custom-navbar {{
    position: fixed; top: 0; left: 0; width: 100%; background-color: rgba(19, 23, 31, 0.85); backdrop-filter: blur(10px);
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

/* --- PRIMARY BUTTON STYLING (FIXED BLACK TEXT) --- */
button[kind="primary"] {{
    background-color: {cyan_color} !important;
    border: none !important;
    font-weight: bold !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
button[kind="primary"] * {{ color: #0E1117 !important; }}
button[kind="primary"]:hover {{
    background-color: {accent_color} !important; transform: translateY(-3px); box-shadow: 0 6px 15px rgba(0, 229, 255, 0.2);
}}

/* --- GEMINI STYLE SIDEBAR UI --- */
/* --- MAGIC LOGO SIDEBAR TOGGLE --- */
/* Hides the default Streamlit expand arrow */
[data-testid="collapsedControl"] svg {{
    display: none !important;
}}
/* Replaces it with the Readora logo */
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
[data-testid="stSidebar"] button[kind="secondary"] p {{ color: #E0E0E0 !important; font-size: 14.5px !important; }}

/* --- LANDING PAGE ANIMATIONS --- */
@keyframes fadeUp {{ 0% {{ opacity: 0; transform: translateY(20px); }} 100% {{ opacity: 1; transform: translateY(0); }} }}
.hero-wrapper {{ padding: 3rem 0 2rem 0; margin-top: 60px; text-align: center; animation: fadeUp 1s ease-out; position: relative; overflow: hidden; }}
.hero-wrapper::before, .hero-wrapper::after {{
    content: ''; position: absolute; width: 250px; height: 250px;
    background: radial-gradient(circle, rgba(0,229,255,0.04) 0%, transparent 60%); border-radius: 50%;
    animation: floatShape 12s infinite alternate ease-in-out; z-index: 0;
}}
.hero-wrapper::before {{ top: -10%; left: 15%; }}
.hero-wrapper::after {{ bottom: -10%; right: 15%; animation-duration: 15s; animation-direction: alternate-reverse; }}
@keyframes floatShape {{ 0% {{ transform: translate(0, 0) scale(1); }} 100% {{ transform: translate(40px, -60px) scale(1.3); }} }}
.hero-text-light {{ position: relative; z-index: 1; font-size: 3.5rem; font-weight: 700; color: {text_color} !important; line-height: 1.2; }}
.hero-text-cyan {{ position: relative; z-index: 1; font-size: 4rem; font-weight: 800; color: {cyan_color} !important; line-height: 1.1; }}
.text-accent {{ color: {accent_color} !important; }}
.standard-pane {{ background-color: #12141A; padding: 30px; border-radius: 12px; border: 1px solid #1E212B; }}
.standard-pane, .standard-pane p, .standard-pane strong, .standard-pane div {{ font-family: 'Arial', sans-serif !important; font-size: 1rem !important; color: #787B86 !important; }}
.mega-footer {{
    display: flex; justify-content: space-around; background-color: #13171F; padding: 40px 20px; border-top: 1px solid {border_color};
    margin-top: 60px; border-radius: 12px;
}}
.footer-col {{ display: flex; flex-direction: column; text-align: left; }}
.footer-col h4 {{ color: #FFFFFF !important; font-size: 1.1rem; margin-bottom: 15px; font-weight: bold; font-family: sans-serif !important;}}
.footer-col a {{ color: #9AA0A6 !important; text-decoration: none; font-size: 0.9rem; margin-bottom: 10px; transition: color 0.2s, transform 0.2s; }}
.footer-col a:hover {{ color: {cyan_color} !important; transform: translateX(5px); }}
</style>
"""
st.markdown(dynamic_css, unsafe_allow_html=True)

if not st.session_state.logged_in:
    navbar_html = f"""
    <div class="custom-navbar">
        <div class="nav-left">
            <img src="{logo_src}" class="nav-logo" alt="Logo">
            <span class="nav-title">Readora AI</span>
        </div>
        <div>
            <a href="#login-section" class="nav-login-btn">Log In</a>
        </div>
    </div>
    """
    st.markdown(navbar_html, unsafe_allow_html=True)

    hero_html = """
    <div class="hero-wrapper">
        <div class="hero-text-light">Your Brain Isn't Behind the AI Curve.</div>
        <div class="hero-text-cyan">It's Been <span class="text-accent">Ahead</span> of It for Years.</div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)
    
    _, btn_col, _ = st.columns([1.5, 1, 1.5])
    with btn_col:
        st.markdown('<a href="#login-section" style="text-decoration: none;"><button style="width: 100%; background-color: #00E5FF; color: #0E1117; border: none; padding: 12px; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; transition: all 0.2s ease;">🚀 Get Started & Try Live Demo</button></a>', unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #E0E0E0;'>Experience the Difference</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9AA0A6; margin-bottom: 30px;'>See how Readora AI transforms rigid, academic text into sensory-friendly, accessible formats.</p>", unsafe_allow_html=True)
    
    demo_col1, demo_col2 = st.columns(2)
    with demo_col1:
        st.markdown("""
        <div class='standard-pane'>
            <strong>Standard Web Text</strong><br><br>
            Photosynthesis is a process used by plants and other organisms to convert light energy into chemical energy that, through cellular respiration, can later be released to fuel the organism's activities. This chemical energy is stored in carbohydrate molecules, such as sugars and starches, which are synthesized from carbon dioxide and water.
        </div>
        """, unsafe_allow_html=True)
    
    with demo_col2:
        st.markdown("""
        <div class='reading-pane' style='font-size: 1.1rem !important; line-height: 1.8 !important;'>
            <strong>Readora AI (Simplified & OpenDyslexic)</strong><br><br>
            Plants use sunlight to make their own food.<br><br>They turn the light into energy and store it as sugar. Later, they use this sugar to grow and stay alive.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("<h2 style='text-align: center; margin-bottom: 30px;'>Built for Neurodivergent Minds</h2>", unsafe_allow_html=True)
    
    col_about, col_features = st.columns(2)
    with col_about:
        st.subheader("Our Mission")
        st.write("We are the UI engineering team from NSUT CSAI. We are building accessible tech designed *with* neurodivergent users, not just *for* them.")
        st.write("Most tools force students to adapt to rigid technology. Our AI adapts to the student, offering a safe space to process complex information without sensory overload.")
        
    with col_features:
        st.subheader("Core Features")
        st.write("- 📄 **Dyslexia-Friendly UI:** Open-Dyslexic font and sensory-friendly dark mode overlays.")
        st.write("- ✨ **Text Simplification:** Advanced AI that breaks down complex, abstract paragraphs into digestible concepts.")
        st.write("- 🔊 **Read Aloud:** Audio conversion for seamless sensory processing.")
        
    st.markdown("---")

    st.markdown('<div id="login-section" style="padding-top: 70px; margin-top: -70px;"></div>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-bottom: 20px;'>Access the App</h2>", unsafe_allow_html=True)
    
    _, auth_col, _ = st.columns([1, 1.5, 1])
    with auth_col:
        log_user = st.text_input("Username")
        log_pass = st.text_input("Password", type="password")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Log In", type="primary", use_container_width=True):
                c.execute('SELECT * FROM users WHERE username=? AND password=?', (log_user, log_pass))
                if c.fetchone():
                    st.session_state.logged_in = True
                    st.session_state.username = log_user
                    st.rerun()
                else:
                    st.toast("Invalid credentials. Please try again.", icon="🚨")
        with c2:
            if st.button("Sign Up", use_container_width=True):
                if log_user and log_pass:
                    c.execute('INSERT INTO users VALUES (?, ?)', (log_user, log_pass))
                    conn.commit()
                    st.toast("Account created! You can now log in.", icon="✅")
        
        st.markdown("<div style='text-align: center; margin: 20px 0; color: #5A5E73; font-size: 0.9rem;'>OR</div>", unsafe_allow_html=True)
        
        if st.button("🌐 Continue with Google", use_container_width=True):
            st.toast("Google OAuth integration coming soon!", icon="ℹ️")

    footer_html = """
    <div class="mega-footer">
        <div class="footer-col">
            <h4>Get to Know Us</h4>
            <a href="#">About Readora AI</a>
            <a href="#">Our Team at NSUT</a>
            <a href="#">Hackathon Mission</a>
            <a href="#">Press Releases</a>
        </div>
        <div class="footer-col">
            <h4>Connect with Us</h4>
            <a href="#">GitHub Repository</a>
            <a href="#">Twitter / X</a>
            <a href="#">Instagram</a>
            <a href="#">LinkedIn</a>
        </div>
        <div class="footer-col">
            <h4>Resources</h4>
            <a href="#">Dyslexia Support</a>
            <a href="#">ADHD Tools</a>
            <a href="#">Accessibility Guide</a>
            <a href="#">API Documentation</a>
        </div>
        <div class="footer-col">
            <h4>Legal & Help</h4>
            <a href="#">Your Account</a>
            <a href="#">Privacy Policy</a>
            <a href="#">Terms of Service</a>
            <a href="#">Help Center</a>
        </div>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

else:
    with st.sidebar:
        st.markdown("""
        <style>
            div[data-testid="stPopoverBody"] {
                background-color: rgba(26, 28, 35, 0.70) !important;
                backdrop-filter: blur(15px);
                border: 1px solid #2D303E;
                border-radius: 12px;
            }
        </style>
        """, unsafe_allow_html=True)

        st.text_input("Search", placeholder="🔍 Search...", label_visibility="collapsed")
        
        if st.button("📝 New chat", use_container_width=True):
            st.session_state.extracted_text = ""
            st.session_state.simplified_text = ""
            st.session_state.last_uploaded_file = None
            st.session_state.current_doc_id = None 
            st.rerun()
            
        st.markdown("<br><span style='color: #787B86; font-size: 0.85rem; font-weight: 600;'>Recents</span>", unsafe_allow_html=True)
        c.execute("SELECT id, doc_name, original_text, simplified_text FROM documents WHERE username=? ORDER BY id DESC", (st.session_state.username,))
        user_history = c.fetchall()
        
        if not user_history:
            st.markdown("<span style='color: #5A5E73; font-size: 0.85rem;'>No documents yet.</span>", unsafe_allow_html=True)
        else:
            for doc in user_history:
                doc_id, doc_name, orig_text, simp_text = doc
                display_name = (doc_name[:22] + '...') if len(doc_name) > 22 else doc_name
                if st.button(f"📄 {display_name}", key=f"hist_{doc_id}", use_container_width=True):
                    st.session_state.current_doc_id = doc_id
                    st.session_state.last_uploaded_file = doc_name
                    st.session_state.extracted_text = orig_text
                    st.session_state.simplified_text = simp_text
                    st.rerun()
                    
        st.markdown("<hr style='margin: 15px 0; border-color: #2D303E;'>", unsafe_allow_html=True)
        st.markdown("<span style='color: #787B86; font-size: 0.85rem; font-weight: 600;'>Visual Settings</span>", unsafe_allow_html=True)
        st.session_state.font_size = st.slider("Font Size", 14, 48, st.session_state.get('font_size', 22))
        st.session_state.line_spacing = st.slider("Line Spacing", 1.0, 4.0, st.session_state.get('line_spacing', 1.8), step=0.1)

        st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
        
        pop_col, log_col = st.columns([8, 2])
        with pop_col:
            with st.popover(f"⚙️ Open Menu & Settings", use_container_width=True):
                m_tab1, m_tab2 = st.tabs(["👤 Profile", "❓ Help"])
                
                with m_tab1:
                    if st.session_state.get('profile_photo'):
                        b64_img = base64.b64encode(st.session_state.profile_photo).decode()
                        st.markdown(f'<img src="data:image/jpeg;base64,{b64_img}" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; margin-bottom: 10px;">', unsafe_allow_html=True)
                        if st.button("🗑️ Delete Photo", use_container_width=True):
                            st.session_state.profile_photo = None
                            st.rerun()
                    else:
                        uploaded_img = st.file_uploader("Upload Profile Photo", type=["jpg", "png", "jpeg"])
                        if uploaded_img:
                            st.session_state.profile_photo = uploaded_img.getvalue()
                            st.rerun()
                            
                    st.text_input("Name")
                    st.text_input("Surname")
                    st.text_area("Preferences for AI", placeholder="E.g., Keep sentences short, I prefer bullets...")
                    
                with m_tab2:
                    st.info("Support: help@readora.ai")
        
        with log_col:
            st.button("🚪", on_click=lambda: st.session_state.update(logged_in=False), use_container_width=True, help="Log Out")

        initial = st.session_state.username[0].upper() if st.session_state.username else "U"
        
        if st.session_state.get('profile_photo'):
            b64_img = base64.b64encode(st.session_state.profile_photo).decode()
            avatar_html = f'<img src="data:image/jpeg;base64,{b64_img}" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover;">'
        else:
            avatar_html = f'<div style="width: 32px; height: 32px; border-radius: 50%; background-color: #D9534F; color: #FFF; display: flex; justify-content: center; align-items: center; font-weight: bold; font-size: 14px;">{initial}</div>'
            
        display_name = st.session_state.username.lower() if st.session_state.username else "user"
        
        ava_col, upg_col = st.columns([2.5, 1.5])
        with ava_col:
            st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 10px; margin-top: 5px;">
                    {avatar_html}
                    <div style="line-height: 1.1;">
                        <div style="font-weight: 500; color: #E0E0E0; font-size: 14px;">{display_name}</div>
                        <div style="font-size: 12px; color: #9AA0A6;">Free</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with upg_col:
            st.markdown("<br>", unsafe_allow_html=True) 
            st.button("Upgrade", use_container_width=True)

    upload_col1, upload_col2, upload_col3 = st.columns([1, 2, 1])
    with upload_col2:
        uploaded_file = st.file_uploader("Drop your reading material here (PDF)", type=['pdf'])

    if uploaded_file is not None:
        if st.session_state.get('last_uploaded_file') != uploaded_file.name:
            with st.spinner("Extracting text from PDF via FastAPI..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    response = requests.post(f"{BACKEND_URL}/upload", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.extracted_text = data.get("text", data.get("content", ""))
                        st.session_state.last_uploaded_file = uploaded_file.name
                        st.session_state.simplified_text = ""
                        
                        c.execute("INSERT INTO documents (username, doc_name, original_text, simplified_text) VALUES (?, ?, ?, ?)", 
                                  (st.session_state.username, uploaded_file.name, st.session_state.extracted_text, ""))
                        conn.commit()
                        st.session_state.current_doc_id = c.lastrowid 
                        st.success("PDF processed and saved to history!")
                    else:
                        st.error(f"Upload Error: {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"Connection Error: Could not connect to FastAPI backend on {BACKEND_URL}")

    st.markdown("<br>", unsafe_allow_html=True)
    btn_c1, btn_c2, btn_c3, btn_c4 = st.columns([1, 1, 1, 1])
    with btn_c2:
        btn_simplify = st.button("✨ Simplify Text", type="primary", use_container_width=True)
    with btn_c3:
        btn_read = st.button("🔊 Read Aloud", use_container_width=True)
    
    if btn_read:
        text_to_read = st.session_state.simplified_text if st.session_state.simplified_text else st.session_state.extracted_text
        if text_to_read:
            clean_text = text_to_read.replace('*', '').replace('#', '')
            clean_text = re.sub(r'\b\d+\.\s+', '', clean_text)
            clean_text = clean_text.replace('- ', '')
            safe_text = json.dumps(clean_text)

            player_html = f"""
            <style>
                @font-face {{ font-family: 'OpenDyslexic'; src: url('https://cdn.jsdelivr.net/gh/antijingoist/opendyslexic@master/compiled/OpenDyslexic-Regular.otf') format('opentype'); }}
                body {{ font-family: 'OpenDyslexic', sans-serif; background-color: #1A1C23; color: #E0E0E0; padding: 20px; border-radius: 12px; margin: 0; }}
                .highlight {{ background-color: #00E5FF; color: #0E1117; font-weight: bold; border-radius: 4px; padding: 2px 4px; box-shadow: 0 0 10px rgba(0,229,255,0.5); transition: background-color 0.1s ease; }}
                #progress-container {{ width: 100%; background-color: #2D303E; border-radius: 8px; margin-bottom: 20px; height: 10px; overflow: hidden; }}
                #progress-bar {{ width: 0%; height: 100%; background-color: #69F0AE; transition: width 0.1s linear; }}
                .controls {{ margin-bottom: 20px; display: flex; gap: 15px; align-items: center; }}
                button {{ background-color: #00E5FF; color: #0E1117; border: none; padding: 8px 16px; border-radius: 20px; font-weight: bold; cursor: pointer; transition: 0.2s; }}
                button:hover {{ background-color: #69F0AE; }}
            </style>
            
            <div id="progress-container"><div id="progress-bar"></div></div>
            <div class="controls">
                <button id="play-pause-btn" onclick="togglePlayPause()">⏸️ Pause Reading</button>
                <span id="status" style="color: #69F0AE; font-weight: bold;">🔊 Speaking...</span>
            </div>
            <div id="text-display" style="font-size: 22px; line-height: 1.8;"></div>

            <script>
                const rawText = {safe_text};
                const display = document.getElementById("text-display");
                const progressBar = document.getElementById("progress-bar");
                const status = document.getElementById("status");
                const playPauseBtn = document.getElementById("play-pause-btn");

                const words = rawText.split(/(\\s+)/); 
                display.innerHTML = words.map((w, i) => `<span id="word-${{i}}">${{w}}</span>`).join('');

                const synth = window.parent.speechSynthesis || window.speechSynthesis;
                synth.cancel();

                let msg = new SpeechSynthesisUtterance(rawText);
                msg.lang = 'en-US';
                msg.rate = 0.9; 

                msg.onboundary = (event) => {{
                    if(event.name === 'word') {{
                        const pct = (event.charIndex / rawText.length) * 100;
                        progressBar.style.width = pct + "%";

                        let charCount = 0;
                        for (let i = 0; i < words.length; i++) {{
                            charCount += words[i].length;
                            if (charCount > event.charIndex) {{
                                document.querySelectorAll('.highlight').forEach(el => el.classList.remove('highlight'));
                                const activeWord = document.getElementById(`word-${{i}}`);
                                if(activeWord && activeWord.innerText.trim().length > 0) {{
                                    activeWord.classList.add('highlight');
                                }}
                                break;
                            }}
                        }}
                    }}
                }};

                msg.onend = () => {{
                    progressBar.style.width = "100%";
                    status.innerText = "✅ Finished";
                    playPauseBtn.style.display = "none"; 
                    document.querySelectorAll('.highlight').forEach(el => el.classList.remove('highlight'));
                }};

                synth.speak(msg);

                function togglePlayPause() {{
                    if (synth.paused) {{
                        synth.resume();
                        playPauseBtn.innerText = "⏸️ Pause Reading";
                        status.innerText = "🔊 Speaking...";
                    }} else if (synth.speaking) {{
                        synth.pause();
                        playPauseBtn.innerText = "▶️ Resume Reading";
                        status.innerText = "⏸️ Paused";
                    }}
                }}
            </script>
            """
            st.markdown("### 🎧 Interactive Reader")
            components.html(player_html, height=400, scrolling=True)
            st.markdown("---")
        else:
            st.warning("Please upload a PDF or generate simplified text first!")

    if btn_simplify:
        if st.session_state.extracted_text and st.session_state.extracted_text.strip():
            with st.spinner("Readora AI is breaking down complex concepts..."):
                try:
                    payload = {"text": st.session_state.extracted_text}
                    response = requests.post(f"{BACKEND_URL}/simplify", json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.simplified_text = data.get("simplified_text", "")
                        
                        if st.session_state.current_doc_id:
                            c.execute("UPDATE documents SET simplified_text = ? WHERE id = ?", 
                                      (st.session_state.simplified_text, st.session_state.current_doc_id))
                            conn.commit()
                            
                        st.toast("Text simplified and saved to history!", icon="✨")
                    else:
                        st.error(f"Simplification Error: {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"Connection Error: Could not connect to FastAPI backend on {BACKEND_URL}")
        elif uploaded_file is not None:
            st.warning("⚠️ The PDF uploaded, but the backend couldn't extract any words. Check the 'Original PDF Text' tab below to verify it's blank.")
        else:
            st.warning("Please upload a PDF document first!")

    st.markdown("---")
    
    st.markdown(f"""
    <style>
        .reading-pane, .reading-pane p, .reading-pane li, .reading-pane span {{
            font-size: {st.session_state.get('font_size', 22)}px !important;
            line-height: {st.session_state.get('line_spacing', 1.8)} !important;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    custom_text_style = ""

    tab1, tab2 = st.tabs(["✨ AI Simplified", "📄 Original PDF Text"])
    
    with tab1:
        st.markdown('<div class="reading-container">', unsafe_allow_html=True)
        if st.session_state.simplified_text:
            st.markdown('<div class="badge">AI Output</div>', unsafe_allow_html=True)
            parsed_html = markdown.markdown(st.session_state.simplified_text)
            st.markdown(f'<div class="reading-pane" style="{custom_text_style}">{parsed_html}</div>', unsafe_allow_html=True)
        else:
            st.info("Upload a PDF and click '✨ Simplify Text' to generate a neurodivergent-friendly version.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="reading-container">', unsafe_allow_html=True)
        if st.session_state.extracted_text:
            st.markdown('<div class="badge">Raw Extraction</div>', unsafe_allow_html=True)
            parsed_raw_html = markdown.markdown(st.session_state.extracted_text)
            st.markdown(f'<div class="reading-pane" style="{custom_text_style}">{parsed_raw_html}</div>', unsafe_allow_html=True)
        else:
            st.info("Your original document text will appear here.")
        st.markdown('</div>', unsafe_allow_html=True)