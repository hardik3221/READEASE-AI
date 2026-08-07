import markdown
import streamlit as st
import streamlit.components.v1 as components

from config import BACKEND_URL
from api_client import upload_pdf, simplify_text_request
from database import insert_document, update_document_simplified
from styles import inject_workspace_css, inject_reading_pane_size_css
from components.reader import build_reader_html


def render_workspace():
    inject_workspace_css()

    # Wider upload dropzone, still centered.
    _, upload_center_col, _ = st.columns([1, 2, 1])
    with upload_center_col:
        uploaded_file = st.file_uploader("Drop your reading material here (PDF)", type=['pdf'], label_visibility="collapsed")

    if uploaded_file is not None:
        if st.session_state.get('last_uploaded_file') != uploaded_file.name:
            status_placeholder = st.empty()
            status_placeholder.info("⏳ Extracting text from PDF via FastAPI...")

            try:
                status_placeholder.warning("⏳ Processing document... This is taking slightly longer than usual due to file size or complexity.")

                response = upload_pdf(uploaded_file.name, uploaded_file.getvalue())
                status_placeholder.empty()

                if response.status_code == 200:
                    data = response.json()
                    st.session_state.extracted_text = data.get("text", "")
                    st.session_state.last_uploaded_file = uploaded_file.name
                    st.session_state.simplified_text = ""
                    st.session_state.vocabulary = ""

                    doc_id = insert_document(
                        st.session_state.username, uploaded_file.name, st.session_state.extracted_text, ""
                    )
                    st.session_state.current_doc_id = doc_id
                    st.success("PDF processed and saved to history!")
                else:
                    st.error(f"Upload Error: {response.json().get('detail')}")
            except Exception as e:
                status_placeholder.empty()
                st.error(f"Connection Error: Could not connect to FastAPI backend on {BACKEND_URL}")

    # Centered action row.
    st.markdown("<div style='height: 22px;'></div>", unsafe_allow_html=True)
    _, btn1_col, btn2_col, _ = st.columns([1, 1.6, 1.6, 1])
    with btn1_col:
        btn_simplify = st.button("✨ Simplify Text", type="primary", use_container_width=True)
    with btn2_col:
        read_btn_label = "⏹ Stop Reading" if st.session_state.get('is_reading') else "🔊 Read Aloud"
        btn_read = st.button(read_btn_label, use_container_width=True)

    if btn_read:
        if st.session_state.get('is_reading'):
            # Stop was pressed — silence the browser's speech synthesis
            # right away, then drop back to the normal static tab.
            st.session_state.is_reading = False
            components.html(
                "<script>(window.parent.speechSynthesis || window.speechSynthesis).cancel();</script>",
                height=0,
            )
        else:
            if st.session_state.simplified_text:
                st.session_state.is_reading = True
            else:
                st.warning("Generate the AI-simplified version first (click '✨ Simplify Text') — Read Aloud only narrates the simplified text.")
        st.rerun()

    if btn_simplify:
        if st.session_state.extracted_text and st.session_state.extracted_text.strip():
            with st.spinner("Readora AI is breaking down complex concepts..."):
                try:
                    response = simplify_text_request(st.session_state.extracted_text)

                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.simplified_text = data.get("simplified_text", "")
                        st.session_state.vocabulary = data.get("vocabulary", "")

                        if st.session_state.current_doc_id:
                            update_document_simplified(st.session_state.current_doc_id, st.session_state.simplified_text)

                        st.toast("Text simplified and saved to history!", icon="✨")
                        st.rerun()
                    else:
                        st.error(f"Simplification Error: {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"Connection Error: Could not connect to FastAPI backend on {BACKEND_URL}")
        elif uploaded_file is not None:
            st.warning("⚠️ The PDF uploaded, but the backend couldn't extract any words. Check the 'Original PDF Text' tab below to verify it's blank.")
        else:
            st.warning("Please upload a PDF document first!")

    inject_reading_pane_size_css(st.session_state.get('font_size', 22), st.session_state.get('line_spacing', 1.8))

    word_count = len(st.session_state.extracted_text.split()) if st.session_state.extracted_text else 0
    simplified_ready = bool(st.session_state.simplified_text)
    st.markdown(f"""
    <div class="content-stats">
        <div class="stat-chip">📄 <b>{word_count:,}</b> words extracted</div>
        <div class="stat-chip">✨ Simplified: <b>{"Ready" if simplified_ready else "Not yet"}</b></div>
    </div>
    """, unsafe_allow_html=True)

    custom_text_style = ""

    tab1, tab2, tab3 = st.tabs(["✨ AI Simplified", "📚 Key Vocabulary", "📄 Original PDF Text"])

    with tab1:
        st.markdown('<div class="reading-container">', unsafe_allow_html=True)
        if st.session_state.simplified_text:
            if st.session_state.get('is_reading'):
                components.html(build_reader_html(st.session_state.simplified_text), height=520, scrolling=True)
            else:
                st.markdown('<div class="badge">AI Output</div>', unsafe_allow_html=True)
                parsed_html = markdown.markdown(st.session_state.simplified_text)
                st.markdown(f'<div class="reading-pane" style="{custom_text_style}">{parsed_html}</div>', unsafe_allow_html=True)
        else:
            st.info("Upload a PDF and click '✨ Simplify Text' to generate a neurodivergent-friendly version.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="reading-container">', unsafe_allow_html=True)
        if st.session_state.get('vocabulary'):
            st.markdown('<div class="badge">Vocabulary List</div>', unsafe_allow_html=True)
            parsed_vocab_html = markdown.markdown(st.session_state.vocabulary)
            st.markdown(f'<div class="reading-pane" style="{custom_text_style}">{parsed_vocab_html}</div>', unsafe_allow_html=True)
        else:
            st.info("Click '✨ Simplify Text' to generate a vocabulary breakdown.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="reading-container">', unsafe_allow_html=True)
        if st.session_state.extracted_text:
            st.markdown('<div class="badge">Raw Extraction</div>', unsafe_allow_html=True)
            parsed_raw_html = markdown.markdown(st.session_state.extracted_text)
            st.markdown(f'<div class="reading-pane" style="{custom_text_style}">{parsed_raw_html}</div>', unsafe_allow_html=True)
        else:
            st.info("Your original document text will appear here.")
        st.markdown('</div>', unsafe_allow_html=True)