import base64
import streamlit as st
import streamlit.components.v1 as components
from database import get_user_documents


def render_sidebar():
    if 'font_size' not in st.session_state:
        st.session_state.font_size = 15
    if 'line_spacing' not in st.session_state:
        st.session_state.line_spacing = 1.8

    with st.sidebar:
        display_name = st.session_state.username.title() if st.session_state.username else "User"
        initial = display_name[0].upper()

        # --- 1. TOP: READORA AI BRAND ---
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 4px;">
            <div class="logo-dot" style="width:12px; height:12px; border-radius:50%; background: linear-gradient(135deg, #00E5FF, #69F0AE); flex-shrink:0;"></div>
            <span style="font-family:'OpenDyslexic', 'Fraunces', Georgia, serif; font-style: italic; font-weight:700; font-size:13px; color:#FFFFFF;">Readora AI</span>
        </div>
        """, unsafe_allow_html=True)

        # --- 2. DIRECTLY BELOW: PROFILE BUTTON ---
        with st.popover(initial, use_container_width=True, help="Account Settings"):
            st.markdown("⚙️ **Account**")
            
            if st.session_state.get('profile_photo'):
                b64_img = base64.b64encode(st.session_state.profile_photo).decode()
                st.markdown(f'<div style="text-align: center; margin-bottom: 10px;"><img src="data:image/jpeg;base64,{b64_img}" style="width: 45px; height: 45px; border-radius: 50%; object-fit: cover;"></div>', unsafe_allow_html=True)
                if st.button("🗑️ Delete Photo", use_container_width=True):
                    st.session_state.profile_photo = None
                    st.rerun()
            else:
                uploaded_img = st.file_uploader("Upload Profile Photo", type=["jpg", "png", "jpeg"])
                if uploaded_img:
                    st.session_state.profile_photo = uploaded_img.getvalue()
                    st.rerun()

            st.info(f"User: {display_name}\n\nPlan: Free")
            
            if st.button("🚪 Log Out", use_container_width=True, type="primary"):
                st.session_state.logged_in = False
                st.rerun()

        if st.session_state.get('profile_photo'):
            b64_trigger = base64.b64encode(st.session_state.profile_photo).decode()
            avatar_js = f"""
            <script>
                setTimeout(function() {{
                    const doc = window.parent.document;
                    doc.querySelectorAll('[data-testid="stPopover"] button').forEach(btn => {{
                        if (btn.innerText.trim() === "{initial}") {{
                            btn.innerHTML = '<img src="data:image/jpeg;base64,{b64_trigger}" style="width: 18px; height: 18px; border-radius: 50%; object-fit: cover; display: block; margin: auto;">';
                        }}
                    }});
                }}, 50);
            </script>
            """
            components.html(avatar_js, height=0)

        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
        st.text_input("Search", placeholder="🔍 Search documents...", label_visibility="collapsed")

        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
        
        if st.button("✨ New Chat", use_container_width=True, type="primary"):
            st.session_state.extracted_text = ""
            st.session_state.simplified_text = ""
            st.session_state.last_uploaded_file = None
            st.session_state.current_doc_id = None
            st.session_state.is_reading = False
            st.rerun()

        st.markdown("<span class='sb-section-label'>Recent Documents</span>", unsafe_allow_html=True)

        user_history = get_user_documents(st.session_state.username)

        with st.container(height=160):
            if not user_history:
                st.markdown("<span style='color: #5A5E73; font-size: 0.4rem;'>No documents yet — upload a PDF to get started.</span>", unsafe_allow_html=True)
            else:
                for doc in user_history:
                    doc_id, doc_name, orig_text, simp_text = doc
                    display_name_doc = (doc_name[:22] + '…') if len(doc_name) > 22 else doc_name
                    is_active = st.session_state.get('current_doc_id') == doc_id
                    icon = "🟢" if is_active else "📄"
                    if st.button(f"{icon} {display_name_doc}", key=f"hist_{doc_id}", use_container_width=True):
                        st.session_state.current_doc_id = doc_id
                        st.session_state.last_uploaded_file = doc_name
                        st.session_state.extracted_text = orig_text
                        st.session_state.simplified_text = simp_text
                        st.session_state.is_reading = False
                        st.rerun()

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

        with st.expander("🔤 Visual Settings", expanded=False):
            st.slider("Font Size", 16, 40, key='font_size')
            st.slider("Line Spacing", 1.0, 4.0, step=0.1, key='line_spacing')
