import os

import streamlit as st

from utils import get_image_base64, find_logo_path
from session import init_session_state
from styles import inject_global_css
from database import init_db
from components.landing import render_landing
from components.topbar import render_topbar
from components.sidebar import render_sidebar
from components.workspace import render_workspace

st.set_page_config(page_title="Readora AI", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

# Looks in assets/ first, then the FrontEnd root, and tolerates a slightly
# different filename/extension/casing — see find_logo_path() in utils.py.
current_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = find_logo_path(current_dir)
logo_b64 = get_image_base64(logo_path)
if logo_b64:
    logo_src = f"data:image/jpeg;base64,{logo_b64}"
else:
    # Local inline fallback — a plain "R" badge that never depends on an
    # external network call, unlike the old placeholder.com URL (which is
    # what was silently failing and leaving the icon/background blank).
    logo_src = (
        "data:image/svg+xml;utf8,"
        "<svg xmlns='http://www.w3.org/2000/svg' width='45' height='45'>"
        "<rect width='45' height='45' rx='22.5' fill='%2300E5FF'/>"
        "<text x='50%25' y='58%25' font-family='sans-serif' font-size='20' "
        "fill='%230E1117' text-anchor='middle'>R</text></svg>"
    )

init_db()
init_session_state()
inject_global_css(logo_src)

if not st.session_state.logged_in:
    render_landing(logo_src)
else:
    render_topbar()
    render_sidebar()
    render_workspace()