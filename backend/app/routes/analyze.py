from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ..services.parser import ResumeParser
from ..services.embedding import EmbeddingService
from ..services.retriever import VectorStore
from ..services.analyzer import Analyzer
from ..utils.chunking import semantic_chunking
from ..services.scoring import ScoringEngine
from ..models.schemas import AnalysisResponse
import shutil
import os
import tempfile

router = APIRouter()
embedding_service = EmbeddingService()
vector_store = VectorStore()
scoring_engine = ScoringEngine()
analyzer = Analyzer(scoring_engine)

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
        # 1. Parse
        parser = ResumeParser()
        raw_text = parser.extract_text(tmp_path)
        clean_text = parser.clean_text(raw_text)
        
        if not clean_text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

        # 2. Analyze using the NEW ScoringEngine logic (ChromaDB + spaCy)
        analysis = scoring_engine.analyze(clean_text, jd)
        return analysis
    
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.post("/generate-ideal-resume")
async def generate_ideal_resume_endpoint(jd: str = Form(...)):
    """Standalone endpoint for generating the ideal resume blueprint from JD only"""
    result = scoring_engine.generate_ideal_resume(jd)
    return result
