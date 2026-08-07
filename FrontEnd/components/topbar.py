import streamlit as st


def render_topbar():
    active_doc_name = st.session_state.get('last_uploaded_file')
    if active_doc_name:
        doc_status_label, doc_status_val = "Current document", (active_doc_name[:28] + '…') if len(active_doc_name) > 28 else active_doc_name
        doc_icon = "📄"
    else:
        doc_status_label, doc_status_val = "Current document", "None loaded yet"
        doc_icon = "📥"

    st.markdown(f"""
    <div class="ws-topbar">
        <div>
            <h2 class="ws-greeting-title">Welcome back, {st.session_state.username.title()}</h2>
        </div>
        <div class="ws-doc-chip">
            <div class="dot">{doc_icon}</div>
            <div class="doc-meta">
                <div class="lbl">{doc_status_label}</div>
                <div class="val">{doc_status_val}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)