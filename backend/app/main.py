import os
from dotenv import load_dotenv

# Load environment variables FIRST before importing components that might use them
load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from .routes import analyze, ranking
from .config import settings

app = FastAPI(title=settings.APP_NAME)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(analyze.router, prefix="/api", tags=["Analysis"])
app.include_router(ranking.router, prefix="/api", tags=["Ranking"])

@app.get("/")
async def root():
    return {"message": "Welcome to HireSense AI API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
