import json
import re

import streamlit as st

from config import paper_bg, paper_ink, paper_border, cyan_color, accent_color


def build_reader_html(text_to_read: str) -> str:
    """Word-by-word TTS reader, styled to match the reading pane, with
    digit-by-digit number pronunciation and synced word highlighting."""
    clean_text = text_to_read.replace('*', '').replace('#', '')
    clean_text = re.sub(r'\b\d+\.\s+', '', clean_text)
    clean_text = clean_text.replace('- ', '')
    safe_text = json.dumps(clean_text)

    return f"""
    <style>
        @font-face {{ font-family: 'OpenDyslexic'; src: url('https://cdn.jsdelivr.net/gh/antijingoist/opendyslexic@master/compiled/OpenDyslexic-Regular.otf') format('opentype'); }}
        body {{ margin: 0; background: transparent; }}
        .reader-page {{
            position: relative;
            font-family: 'OpenDyslexic', sans-serif;
            background-color: {paper_bg};
            color: {paper_ink};
            padding: 28px 32px;
            border-radius: 6px 12px 12px 6px;
            border: 1px solid {paper_border};
            box-shadow: 0 14px 30px rgba(0,0,0,0.35), inset 0 0 0 1px {paper_border};
        }}
        .reader-page::after {{
            content: ''; position: absolute; top: 0; right: 0; width: 0; height: 0;
            border-style: solid; border-width: 0 22px 22px 0;
            border-color: transparent #DCCEA4 transparent transparent;
            filter: drop-shadow(-2px 2px 3px rgba(0,0,0,0.18));
        }}
        .reader-badge {{
            display: inline-block; background-color: rgba(0,229,255,0.14); color: #0E7490;
            padding: 4px 12px; border-radius: 15px; font-size: 0.75rem; font-weight: 700;
            letter-spacing: 0.03em; margin-bottom: 16px; font-family: 'OpenDyslexic', sans-serif;
        }}
        .highlight {{ background-color: {cyan_color}; color: #0E1117; font-weight: bold; border-radius: 4px; padding: 2px 4px; box-shadow: 0 0 8px rgba(0,229,255,0.5); transition: background-color 0.1s ease; }}
        #progress-container {{ width: 100%; background-color: {paper_border}; border-radius: 8px; margin-bottom: 18px; height: 10px; overflow: hidden; }}
        #progress-bar {{ width: 0%; height: 100%; background-color: {accent_color}; transition: width 0.1s linear; }}
        .controls {{ margin-bottom: 20px; display: flex; gap: 15px; align-items: center; font-family: 'OpenDyslexic', sans-serif; }}
        button {{ background-color: {cyan_color}; color: #0E1117; border: none; padding: 8px 16px; border-radius: 20px; font-family: 'OpenDyslexic', sans-serif; font-weight: bold; cursor: pointer; transition: 0.2s; }}
        button:hover {{ background-color: {accent_color}; }}
        #status {{ font-family: 'OpenDyslexic', sans-serif; }}
    </style>

    <div class="reader-page">
        <div class="reader-badge">🔊 AI Output — Reading Aloud</div>
        <div id="progress-container"><div id="progress-bar"></div></div>
        <div class="controls">
            <button id="play-pause-btn" onclick="togglePlayPause()">⏸️ Pause Reading</button>
            <span id="status" style="color: #4E7A67; font-weight: bold;">🔊 Speaking...</span>
        </div>
        <div id="text-display" style="font-size: {st.session_state.get('font_size', 22)}px; line-height: {st.session_state.get('line_spacing', 1.8)};"></div>
    </div>

    <script>
        const rawText = {safe_text};
        const display = document.getElementById("text-display");
        const progressBar = document.getElementById("progress-bar");
        const status = document.getElementById("status");
        const playPauseBtn = document.getElementById("play-pause-btn");

        // Split into alternating word / whitespace tokens so we can
        // render each word in its own <span> for highlighting.
        const tokens = rawText.split(/(\\s+)/);
        display.innerHTML = tokens.map((w, i) => `<span id="word-${{i}}">${{w}}</span>`).join('');

        // Indices of the actual words (skipping whitespace tokens).
        const wordIndices = [];
        for (let i = 0; i < tokens.length; i++) {{
            if (tokens[i].trim().length > 0) wordIndices.push(i);
        }}

        // Numbers should be read digit-by-digit ("8315" -> "eight
        // three one five"), not as a full number ("eight thousand
        // three hundred fifteen"). We keep the on-screen text as-is
        // and only rewrite what gets *spoken* for each word.
        function toSpeechForm(word) {{
            return word.replace(/\\d+/g, (digits) => digits.split('').join(' '));
        }}

        const synth = window.parent.speechSynthesis || window.speechSynthesis;
        synth.cancel();

        // Pick a warm, natural-sounding female voice if the browser exposes one.
        // Voice lists can load asynchronously, so we handle both cases.
        function pickFemaleVoice() {{
            const voices = synth.getVoices();
            if (!voices || voices.length === 0) return null;
            const preferredNames = [
                "Google US English Female", "Google UK English Female",
                "Microsoft Aria Online (Natural) - English (United States)",
                "Microsoft Jenny Online (Natural) - English (United States)",
                "Microsoft Zira Desktop - English (United States)",
                "Samantha", "Victoria", "Karen", "Moira", "Tessa", "Serena",
                "Google US English"
            ];
            for (const name of preferredNames) {{
                const match = voices.find(v => v.name === name);
                if (match) return match;
            }}
            const looseMatch = voices.find(v =>
                /female/i.test(v.name) && /en/i.test(v.lang)
            );
            if (looseMatch) return looseMatch;
            return voices.find(v => /en/i.test(v.lang)) || voices[0];
        }}

        let chosenVoice = null;

        function highlightWord(pos) {{
            document.querySelectorAll('.highlight').forEach(el => el.classList.remove('highlight'));
            if (pos >= wordIndices.length) return;
            const tokenIndex = wordIndices[pos];
            const el = document.getElementById(`word-${{tokenIndex}}`);
            if (el) el.classList.add('highlight');
            progressBar.style.width = ((pos + 1) / wordIndices.length * 100) + "%";
        }}

        // Words are grouped into small chunks (3 at a time) before being
        // spoken as one utterance each. Single-word utterances have a
        // noticeable startup lag per word which reads as "too slow";
        // small chunks keep pace natural while still letting us highlight
        // the exact word as its chunk begins.
        const CHUNK_SIZE = 3;
        function speakFrom(pos) {{
            if (pos >= wordIndices.length) {{
                status.innerText = "✅ Finished";
                playPauseBtn.style.display = "none";
                document.querySelectorAll('.highlight').forEach(el => el.classList.remove('highlight'));
                return;
            }}
            highlightWord(pos);

            const chunkEnd = Math.min(pos + CHUNK_SIZE, wordIndices.length);
            const chunkTokenIdx = wordIndices.slice(pos, chunkEnd);
            const chunkWords = chunkTokenIdx.map(i => toSpeechForm(tokens[i]));
            const spoken = chunkWords.join(' ');

            const utter = new SpeechSynthesisUtterance(spoken);
            utter.lang = 'en-US';
            utter.rate = 1.15;
            utter.pitch = 1.05;
            if (chosenVoice) utter.voice = chosenVoice;
            utter.onend = () => {{
                if (!synth.paused) speakFrom(chunkEnd);
            }};
            synth.speak(utter);
        }}

        function startReading() {{
            chosenVoice = pickFemaleVoice();
            speakFrom(0);
        }}

        if (synth.getVoices().length > 0) {{
            startReading();
        }} else {{
            synth.onvoiceschanged = () => startReading();
        }}

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