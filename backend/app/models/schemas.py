from pydantic import BaseModel
from typing import List, Dict, Optional

class AnalysisRequest(BaseModel):
    jd_text: str

class AnalysisResponse(BaseModel):
    score: float
    strong_skills: List[str]
    missing_skills: List[str]
    explanation: str
    suggestions: List[str]

class CandidateRanking(BaseModel):
    filename: str
    score: float
    explanation: str
    rank: int
    ranking_reason: str

class RankingResponse(BaseModel):
    candidates: List[CandidateRanking]
