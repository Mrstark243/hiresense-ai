from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List
from .analyze import analyze_resume
from ..services.ranking_engine import RankingEngine
from ..models.schemas import RankingResponse
import io

router = APIRouter()
ranking_engine = RankingEngine()

@router.post("/rank", response_model=RankingResponse)
async def rank_candidates(
    files: List[UploadFile] = File(...),
    jd_text: str = Form(...)
):
    results = []
    for file in files:
        # Reuse analysis logic
        analysis = await analyze_resume(file, jd_text)
        results.append({
            "filename": file.filename,
            "score": analysis.score,
            "explanation": analysis.explanation
        })
    
    ranked_candidates = ranking_engine.rank_candidates(results)
    return RankingResponse(candidates=ranked_candidates)
