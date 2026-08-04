import streamlit as st
import sqlite3
import base64
import os
import requests  

# Backend URL pointing to your running FastAPI server
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Readora AI", page_icon="📚", layout="wide")

def get_image_base64(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "logo readora ai.jpeg")
logo_b64 = get_image_base64(logo_path)

conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
conn.commit()

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""

if 'simplified_text' not in st.session_state:
    st.session_state.simplified_text = ""

bg_color = "#0E1117"
text_color = "#E0E0E0"
card_color = "#1A1C23"
cyan_color = "#00E5FF"
accent_color = "#69F0AE"
border_color = "#2D303E"

dynamic_css = f"""
<style>
/* Hide Streamlit Deploy Artifacts */
#MainMenu {{visibility: hidden;}}
header {{visibility: hidden;}}
footer {{visibility: hidden;}}

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

/* --- TYPOGRAPHY HIERARCHY FIX --- */
/* 1. Clean UI Font for body, headers, and Hero text (reverted to sleek SaaS look) */
html, body, [class*="css"], p, li, label, .stMarkdown, h1, h2, h3, h4, h5, h6, .nav-title {{
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
    color: {text_color} !important;
}}

h1, h2, h3, h4, h5, h6, .nav-title {{
    font-weight: 700 !important;
}}

.hero-text-light, .hero-text-cyan {{
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
}}

/* 2. Force OpenDyslexic specifically on the Accessible Reading Panes ONLY */
.reading-pane, .reading-pane p, .reading-pane strong, .reading-pane div {{
    font-family: 'OpenDyslexic', sans-serif !important;
    font-size: 1.1rem !important;
    line-height: 1.8 !important;
    color: {text_color} !important;
}}

/* 3. Keep Standard Font for the standard web text demo */
.standard-pane, .standard-pane p, .standard-pane strong, .standard-pane div {{
    font-family: 'Arial', sans-serif !important;
    font-size: 1rem !important;
    color: #787B86 !important;
}}


/* --- CUSTOM TOP NAVBAR --- */
.custom-navbar {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    background-color: rgba(19, 23, 31, 0.85);
    backdrop-filter: blur(10px);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 50px;
    z-index: 99999;
    border-bottom: 1px solid {border_color};
}}
.nav-left {{
    display: flex;
    align-items: center;
    gap: 12px;
}}
.nav-logo {{
    width: 36px;
    height: 36px; 
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid {cyan_color};
}}
.nav-title {{
    font-size: 1.2rem;
    font-weight: bold;
    color: {text_color};
    letter-spacing: 1px;
}}
.nav-login-btn {{
    background-color: transparent;
    color: {text_color};
    border: 1px solid {cyan_color};
    padding: 6px 20px;
    border-radius: 25px;
    text-decoration: none !important;
    font-weight: bold;
    transition: all 0.3s ease;
}}
.nav-login-btn:hover {{
    background-color: {cyan_color};
    color: #0E1117;
    box-shadow: 0 0 15px rgba(0, 229, 255, 0.4);
}}

/* Custom Primary Button Styling */
button[kind="primary"] {{
    background-color: {cyan_color} !important;
    color: #0E1117 !important;
    border: none !important;
    font-weight: bold !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
button[kind="primary"]:hover {{
    background-color: {accent_color} !important;
    transform: translateY(-3px);
    box-shadow: 0 6px 15px rgba(0, 229, 255, 0.2);
}}

@keyframes fadeUp {{
    0% {{ opacity: 0; transform: translateY(20px); }}
    100% {{ opacity: 1; transform: translateY(0); }}
}}

.hero-wrapper {{ 
    padding: 3rem 0 2rem 0; 
    margin-top: 60px;
    text-align: center; 
    animation: fadeUp 1s ease-out;
    position: relative;
    overflow: hidden;
}}
.hero-wrapper::before, .hero-wrapper::after {{
    content: '';
    position: absolute;
    width: 250px; height: 250px;
    background: radial-gradient(circle, rgba(0,229,255,0.04) 0%, transparent 60%);
    border-radius: 50%;
    animation: floatShape 12s infinite alternate ease-in-out;
    z-index: 0;
}}
.hero-wrapper::before {{ top: -10%; left: 15%; }}
.hero-wrapper::after {{ bottom: -10%; right: 15%; animation-duration: 15s; animation-direction: alternate-reverse; }}

@keyframes floatShape {{
    0% {{ transform: translate(0, 0) scale(1); }}
    100% {{ transform: translate(40px, -60px) scale(1.3); }}
}}

.hero-text-light {{ position: relative; z-index: 1; font-size: 3.5rem; font-weight: 700; color: {text_color} !important; line-height: 1.2; }}
.hero-text-cyan {{ position: relative; z-index: 1; font-size: 4rem; font-weight: 800; color: {cyan_color} !important; line-height: 1.1; }}
.text-accent {{ color: {accent_color} !important; }}

.reading-pane {{
    background-color: {card_color}; padding: 30px;
    border-radius: 12px; box-shadow: 0px 8px 16px rgba(0,0,0,0.1);
    border: 1px solid {border_color}; transition: all 0.3s ease;
}}

.standard-pane {{
    background-color: #12141A; padding: 30px;
    border-radius: 12px; border: 1px solid #1E212B;
}}

.mega-footer {{
    display: flex; justify-content: space-around; background-color: #13171F;
    padding: 40px 20px; border-top: 1px solid {border_color};
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

    # --- TOP NAVBAR INJECTION ---
    logo_src = f"data:image/jpeg;base64,{logo_b64}" if logo_b64 else "https://via.placeholder.com/45"
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

    # --- HERO SECTION ---
    hero_html = """
    <div class="hero-wrapper">
        <div class="hero-text-light">Your Brain Isn't Behind the AI Curve.</div>
        <div class="hero-text-cyan">It's Been <span class="text-accent">Ahead</span> of It for Years.</div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)
    
    # CTA Button
    _, btn_col, _ = st.columns([1.5, 1, 1.5])
    with btn_col:
        st.markdown('<a href="#login-section" style="text-decoration: none;"><button style="width: 100%; background-color: #00E5FF; color: #0E1117; border: none; padding: 12px; border-radius: 8px; font-size: 16px; font-weight: bold; cursor: pointer; transition: all 0.2s ease;">🚀 Get Started & Try Live Demo</button></a>', unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- INTERACTIVE BEFORE & AFTER DEMO ---
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
        <div class='reading-pane'>
            <strong>Readora AI (Simplified & OpenDyslexic)</strong><br><br>
            Plants use sunlight to make their own food.<br><br>They turn the light into energy and store it as sugar. Later, they use this sugar to grow and stay alive.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # --- ABOUT US / FEATURES SECTION ---
    st.markdown("<h2 style='text-align: center; margin-bottom: 30px;'>Built for Neurodivergent Minds</h2>", unsafe_allow_html=True)
    
    col_about, col_features = st.columns(2)
    with col_about:
        st.subheader("Our Mission")
        st.write("We are Mayank Joshi and the UI engineering team from NSUT CSAI. We are building accessible tech designed *with* neurodivergent users, not just *for* them.")
        st.write("Most tools force students to adapt to rigid technology. Our AI adapts to the student, offering a safe space to process complex information without sensory overload.")
        
    with col_features:
        st.subheader("Core Features")
        st.write("- 📄 **Dyslexia-Friendly UI:** Open-Dyslexic font and sensory-friendly dark mode overlays.")
        st.write("- ✨ **Text Simplification:** Advanced AI that breaks down complex, abstract paragraphs into digestible concepts.")
        st.write("- 🔊 **Read Aloud (Coming Soon):** Audio conversion for seamless sensory processing.")
        
    st.markdown("---")

    # --- DEDICATED AUTHENTICATION SECTION ---
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
                    st.rerun()
                else:
                    st.toast("Invalid credentials. Please try again.", icon="🚨")
        with c2:
            if st.button("Sign Up", use_container_width=True):
                if log_user and log_pass:
                    c.execute('INSERT INTO users VALUES (?, ?)', (log_user, log_pass))
                    conn.commit()
                    st.toast("Account created! You can now log in.", icon="✅")

    # --- MEGA FOOTER ---
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
    st.sidebar.button("Log Out", on_click=lambda: st.session_state.update(logged_in=False))
    
    st.sidebar.header("Visual Settings")
    font_size = st.sidebar.slider("Font Size", 14, 48, 22)
    line_spacing = st.sidebar.slider("Line Spacing", 1.0, 4.0, 1.8)

    st.title("📚 Readora AI")
    st.markdown("---")

    uploaded_file = st.file_uploader("Drop your reading material here (PDF)", type=['pdf'])

    # --- FASTAPI BACKEND INTEGRATION 1: AUTOMATIC PDF EXTRACTION ---
    if uploaded_file is not None:
        if st.session_state.get('last_uploaded_file') != uploaded_file.name:
            with st.spinner("Extracting text from PDF via FastAPI..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    response = requests.post(f"{BACKEND_URL}/upload", files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.extracted_text = data.get("text", "")
                        st.session_state.last_uploaded_file = uploaded_file.name
                        st.session_state.simplified_text = ""  # Reset simplified text for new upload
                        st.success("PDF processed successfully!")
                    else:
                        st.error(f"Upload Error: {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"Connection Error: Could not connect to FastAPI backend on {BACKEND_URL}")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        btn_simplify = st.button("✨ Simplify Text", type="primary", use_container_width=True)
    with col2:
        btn_read = st.button("🔊 Read Aloud", use_container_width=True)

    # --- FASTAPI BACKEND INTEGRATION 2: AI SIMPLIFICATION ---
    if btn_simplify:
        if st.session_state.extracted_text:
            with st.spinner("Simplifying text using Groq AI..."):
                try:
                    payload = {"text": st.session_state.extracted_text}
                    response = requests.post(f"{BACKEND_URL}/simplify", json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.simplified_text = data.get("simplified_text", "")
                        st.success("Text simplified!")
                    else:
                        st.error(f"Simplification Error: {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"Connection Error: Could not connect to FastAPI backend on {BACKEND_URL}")
        else:
            st.warning("Please upload a PDF document first!")

    st.markdown("---")
    st.subheader("Reading Area")

    # Display dynamic font controls inside partner's reading-pane class
    custom_text_style = f"font-size: {font_size}px !important; line-height: {line_spacing} !important;"

    # Displays simplified text if available, otherwise extracted text, or default helper text
    display_text = (
        st.session_state.simplified_text 
        or st.session_state.extracted_text 
        or "This is a live preview. Upload a PDF document above to begin reading."
    )

    st.markdown(
        f'<div class="reading-pane" style="{custom_text_style}">{display_text}</div>', 

       unsafe_allow_html=True
    )