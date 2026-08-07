import base64

import streamlit as st

from database import get_user_documents


def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div class="sb-brand">
            <div class="logo-dot"></div>
            <span class="name">Readora AI</span>
        </div>
        """, unsafe_allow_html=True)

        st.text_input("Search", placeholder="🔍 Search documents...", label_visibility="collapsed")

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
        if st.button("✨ New Chat Session", use_container_width=True, type="primary"):
            st.session_state.extracted_text = ""
            st.session_state.simplified_text = ""
            st.session_state.last_uploaded_file = None
            st.session_state.current_doc_id = None
            st.session_state.is_reading = False
            st.rerun()

        st.markdown("<span class='sb-section-label'>Recent Documents</span>", unsafe_allow_html=True)

        user_history = get_user_documents(st.session_state.username)

        with st.container(height=280):
            if not user_history:
                st.markdown("<span style='color: #5A5E73; font-size: 0.85rem;'>No documents yet — upload a PDF to get started.</span>", unsafe_allow_html=True)
            else:
                for doc in user_history:
                    doc_id, doc_name, orig_text, simp_text = doc
                    display_name = (doc_name[:22] + '…') if len(doc_name) > 22 else doc_name
                    is_active = st.session_state.get('current_doc_id') == doc_id
                    icon = "🟢" if is_active else "📄"
                    if st.button(f"{icon} {display_name}", key=f"hist_{doc_id}", use_container_width=True):
                        st.session_state.current_doc_id = doc_id
                        st.session_state.last_uploaded_file = doc_name
                        st.session_state.extracted_text = orig_text
                        st.session_state.simplified_text = simp_text
                        st.session_state.is_reading = False
                        st.rerun()

        with st.expander("🔤 Visual Settings", expanded=False):
            st.session_state.font_size = st.slider("Font Size", 14, 48, st.session_state.get('font_size', 22))
            st.session_state.line_spacing = st.slider("Line Spacing", 1.0, 4.0, st.session_state.get('line_spacing', 1.8), step=0.1)

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        initial = st.session_state.username[0].upper() if st.session_state.username else "U"
        if st.session_state.get('profile_photo'):
            b64_img = base64.b64encode(st.session_state.profile_photo).decode()
            avatar_html = f'<img src="data:image/jpeg;base64,{b64_img}" style="width: 34px; height: 34px; border-radius: 50%; object-fit: cover;">'
        else:
            avatar_html = f'<div style="width: 34px; height: 34px; border-radius: 50%; background-color: #00E5FF; color: #0E1117; display: flex; justify-content: center; align-items: center; font-weight: 700; font-family: \'OpenDyslexic\', \'Figtree\', sans-serif; font-size: 14px; flex-shrink:0;">{initial}</div>'

        display_name = st.session_state.username.lower() if st.session_state.username else "user"

        st.markdown(f"""
        <div class="sb-profile-card">
            {avatar_html}
            <div style="line-height: 1.15; flex:1;">
                <div style="font-weight: 600; color: #E0E0E0; font-size: 13.5px;">{display_name}</div>
                <div style="font-size: 11px; color: #00E5FF;">Free Plan</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        pop_col, log_col = st.columns([7, 3])
        with pop_col:
            with st.popover("⚙️ Settings & Profile", use_container_width=True):
                st.markdown("##### Account Settings")
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
            st.button("🚪 Out", use_container_width=True, help="Log Out",
                       on_click=lambda: st.session_state.update(logged_in=False))