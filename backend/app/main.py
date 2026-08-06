from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now your existing imports will work 100% of the time:
from app.routes import upload, simplify, history


app = FastAPI(
    title="ReadEase AI Backend"
)

# Allow frontend / Swagger requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(simplify.router)

# Made this async!
@app.get("/")
async def home():
    return {
        "message": "ReadEase AI Backend Running"
    }