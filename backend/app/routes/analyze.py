from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ..services.parser import ResumeParser
from ..utils.chunking import semantic_chunking
from ..services.scoring import ScoringEngine
from ..services.retriever import VectorStore
from ..models.schemas import AnalysisResponse
import numpy as np
import shutil
import os
import tempfile

router = APIRouter()
scoring_engine: ScoringEngine = None
vector_store: VectorStore = None

def get_scoring_engine():
    global scoring_engine
    if scoring_engine is None:
        print("DEBUG: Initializing API-based Scoring Engine...")
        scoring_engine = ScoringEngine()
    return scoring_engine

def get_vector_store():
    global vector_store
    if vector_store is None:
        print("DEBUG: Initializing FAISS VectorStore...")
        vector_store = VectorStore(dimension=384)
    return vector_store

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

        print("DEBUG: Preparing the ScoringEngine API caller...")
        engine = get_scoring_engine()
        
        # 2. RAG Pipeline: Chunk -> Embed -> Store -> Retrieve
        print("DEBUG: Chunking resume text for RAG pipeline...")
        chunks = semantic_chunking(clean_text, chunk_size=500, overlap=100)
        
        if chunks:
            print(f"DEBUG: Generated {len(chunks)} chunks. Embedding each chunk via HF API...")
            # Embed each chunk using the ScoringEngine's HF API (not local EmbeddingService)
            chunk_embeddings = []
            for i, chunk in enumerate(chunks):
                emb = engine.get_embedding(chunk)
                chunk_embeddings.append(emb)
            chunk_embeddings_np = np.array(chunk_embeddings).astype('float32')
            
            # Store in FAISS VectorStore (reset first for fresh per-request index)
            store = get_vector_store()
            store.reset()
            store.add_chunks(chunks, chunk_embeddings_np)
            
            # Retrieve top-5 chunks relevant to the JD
            print("DEBUG: Embedding JD for retrieval query...")
            jd_embedding = engine.get_embedding(jd).reshape(1, -1)
            retrieved = store.search(jd_embedding, k=5)
            
            # Console verification: print top 3 retrieved chunks
            print("\n" + "=" * 60)
            print("RAG VERIFICATION: Top 3 Retrieved Chunks")
            print("=" * 60)
            for i, rc in enumerate(retrieved[:3]):
                print(f"\n--- Chunk {i+1} (relevance score: {rc['score']:.4f}) ---")
                print(rc['chunk'][:200] + ("..." if len(rc['chunk']) > 200 else ""))
            print("=" * 60 + "\n")
        else:
            print("DEBUG: No chunks generated from resume text. Skipping RAG retrieval.")
            retrieved = []
        
        # 3. Analyze using the ScoringEngine with RAG context
        print("DEBUG: Making HTTP requests to external AI API...")
        analysis = engine.analyze(clean_text, jd, retrieved_context=retrieved if retrieved else None)
        
        print("DEBUG: Analysis successfully finished! Returning result to Frontend...")
        return analysis
    
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
