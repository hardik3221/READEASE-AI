import streamlit as st


def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'extracted_text' not in st.session_state:
        st.session_state.extracted_text = ""
    if 'simplified_text' not in st.session_state:
        st.session_state.simplified_text = ""
    if 'vocabulary' not in st.session_state:
        st.session_state.vocabulary = ""
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
    if 'is_reading' not in st.session_state:
        st.session_state.is_reading = False