import os

# Backend URL pointing to your running FastAPI server
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# --- DESIGN TOKENS ---------------------------------------------------------
# Original dark UI palette: near-black background with cyan/mint accents.
bg_color = "#0E1117"        # app background
text_color = "#E0E0E0"      # UI text
card_color = "#1A1C23"      # panel surface
cyan_color = "#00E5FF"      # primary accent
accent_color = "#69F0AE"    # secondary accent
border_color = "#2D303E"

# Paper tokens — used anywhere the user is actually *reading*, so the
# product's core transformation (dense text -> calm text) is visible in
# the UI itself, not just described by it.
paper_bg = "#050411"      # warm cream page
paper_ink = "#FFFEFD"       # ink on paper
paper_border = "#E4D8B8"    # page edge
paper_accent = "#00E5FF"   # terracotta — emphasis on paper (contrast-safe)