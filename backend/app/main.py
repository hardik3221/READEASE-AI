from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import upload, simplify

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