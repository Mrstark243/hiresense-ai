from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ..services.parser import ResumeParser
from ..utils.chunking import semantic_chunking
from ..services.scoring import ScoringEngine
from ..models.schemas import AnalysisResponse
import shutil
import os
import tempfile

router = APIRouter()
scoring_engine: ScoringEngine = None

def get_scoring_engine():
    global scoring_engine
    if scoring_engine is None:
        print("Initializing ML models for the first time...")
        scoring_engine = ScoringEngine()
    return scoring_engine

@router.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    jd: str = Form(...)
):
    # Save file to temp
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(resume.file, tmp)
        tmp_path = tmp.name

    try:
        print("DEBUG: Extracting text from PDF...")
        # 1. Parse
        parser = ResumeParser()
        raw_text = parser.extract_text(tmp_path)
        clean_text = parser.clean_text(raw_text)
        
        if not clean_text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

        print("DEBUG: Fetching the ScoringEngine and loading ML models into RAM...")
        # 2. Analyze using the NEW ScoringEngine logic
        engine = get_scoring_engine()
        
        print("DEBUG: Running ML model Analysis (This is where it usually crashes if Out of Memory)...")
        analysis = engine.analyze(clean_text, jd)
        
        print("DEBUG: Analysis successfully finished! Returning result to Frontend...")
        return analysis
    
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
