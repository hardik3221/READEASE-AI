import streamlit as st
import sqlite3
import base64
import os

st.set_page_config(page_title="Readora AI", page_icon="📚", layout="wide")

def get_image_base64(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(current_dir, "logo readora ai.png")
logo_b64 = get_image_base64(logo_path)

conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
conn.commit()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

bg_color = "#0E1117"
text_color = "#E0E0E0"
card_color = "#1A1C23"
cyan_color = "#00E5FF"
accent_color = "#69F0AE"
border_color = "#2D303E"

dynamic_css = f"""
<style>
@font-face {{
    font-family: 'OpenDyslexic';
    src: url('https://cdn.jsdelivr.net/gh/antijingoist/opendyslexic@master/compiled/OpenDyslexic-Regular.otf') format('opentype');
    font-weight: normal;
    font-style: normal;
}}
.stApp {{ background-color: {bg_color}; }}

html, body, [class*="css"], .stMarkdown, p, h1, h2, h3, h4, h5, h6, label {{
    font-family: 'OpenDyslexic', sans-serif !important;
}}
.stMarkdown, p, h1, h2, h3, h4, h5, h6, label {{
    color: {text_color} !important;
}}

@keyframes fadeUp {{
    0% {{ opacity: 0; transform: translateY(20px); }}
    100% {{ opacity: 1; transform: translateY(0); }}
}}

/* Interactive Background Animation for the Top Space */
.hero-wrapper {{ 
    padding: 3rem 0 4rem 0; 
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
    background-color: {card_color}; color: {text_color} !important; padding: 30px;
    border-radius: 12px; box-shadow: 0px 8px 16px rgba(0,0,0,0.1);
    border: 1px solid {border_color}; transition: all 0.3s ease;
}}

/* New Mega Footer Styling */
.mega-footer {{
    display: flex;
    justify-content: space-around;
    background-color: #13171F;
    padding: 40px 20px;
    border-top: 1px solid {border_color};
    margin-top: 60px;
    border-radius: 12px;
}}
.footer-col {{ display: flex; flex-direction: column; text-align: left; }}
.footer-col h4 {{ color: #FFFFFF !important; font-size: 1.1rem; margin-bottom: 15px; font-weight: bold; }}
.footer-col a {{ color: #9AA0A6 !important; text-decoration: none; font-size: 0.9rem; margin-bottom: 10px; transition: color 0.2s, transform 0.2s; }}
.footer-col a:hover {{ color: {cyan_color} !important; transform: translateX(5px); }}

.stButton > button {{ transition: transform 0.2s ease, box-shadow 0.2s ease; }}
.stButton > button:hover {{ transform: translateY(-3px); box-shadow: 0 6px 15px rgba(0, 229, 255, 0.15); }}
.stTextInput input {{ color: {text_color} !important; }}
</style>
"""
st.markdown(dynamic_css, unsafe_allow_html=True)

if not st.session_state.logged_in:
    if logo_b64:
        st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{logo_b64}" width="250" style="border-radius: 15px; border: 1px solid #2D303E; margin-bottom: 20px;"></div>', unsafe_allow_html=True)
    else:
        st.error("Logo file not found. Ensure 'logo readora ai.png' is in the same folder.")

    hero_html = """
    <div class="hero-wrapper">
        <div class="hero-text-light">Your Brain Isn't Behind the AI Curve.</div>
        <div class="hero-text-cyan">It's Been <span class="text-accent">Ahead</span> of It for Years.</div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)
    st.markdown("---")

    col_about, col_login = st.columns(2)
    
    with col_about:
        st.subheader("About Us")
        st.write("We are Mayank Joshi and [Teammate Name], developers from NSUT CSAI building accessible tech for neurodivergent minds.")
        st.write("### Features")
        st.write("- 📄 **Dyslexia-Friendly UI:** Open-Dyslexic font and sensory-friendly dark mode.")
        st.write("- ✨ **Text Simplification:** AI that breaks down complex paragraphs.")
        st.write("- 🔊 **Read Aloud:** Audio conversion for sensory processing ease.")

    with col_login:
        st.subheader("Access the App")
        log_user = st.text_input("Username")
        log_pass = st.text_input("Password", type="password")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Log In", use_container_width=True):
                c.execute('SELECT * FROM users WHERE username=? AND password=?', (log_user, log_pass))
                if c.fetchone():
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        with c2:
            if st.button("Sign Up", use_container_width=True):
                if log_user and log_pass:
                    c.execute('INSERT INTO users VALUES (?, ?)', (log_user, log_pass))
                    conn.commit()
                    st.success("Account created! You can now log in.")

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

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        btn_simplify = st.button("✨ Simplify Text", use_container_width=True)
    with col2:
        btn_read = st.button("🔊 Read Aloud", use_container_width=True)

    st.markdown("---")
    st.subheader("Reading Area")

    sample_text = "This is a live preview. Use the sidebar settings to adjust the text size and line spacing. Finding the right spacing can make reading much easier."

    st.markdown(f'<div class="reading-pane">{sample_text}</div>', unsafe_allow_html=True)