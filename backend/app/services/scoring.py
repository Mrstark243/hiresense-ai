import re
import os
import requests
import numpy as np
from typing import List, Dict
from numpy.linalg import norm
from ..config import settings

# Technical Skill Categories
SKILL_CATEGORIES = {
    "Frontend": ["react", "vue", "angular", "next.js", "tailwind", "html", "css", "javascript", "typescript"],
    "Backend": ["fastapi", "flask", "django", "node.js", "express", "go", "rust", "python"],
    "Databases": ["postgresql", "mongodb", "sql", "nosql", "redis", "elasticsearch", "pinecone", "chroma"],
    "Cloud/DevOps": ["aws", "docker", "kubernetes", "git", "ci/cd", "terraform", "azure", "gcp"],
    "AI/ML": ["pytorch", "tensorflow", "rag", "embeddings", "nlp", "transformers", "llm", "langchain"]
}

TECH_KEYWORDS = [item for sublist in SKILL_CATEGORIES.values() for item in sublist]

STOP_WORDS = {
    'experience', 'work', 'using', 'used', 'like', 'plus', 'requirements', 
    'responsibilities', 'good', 'knowledge', 'understanding', 'skills', 
    'qualified', 'benefits', 'join', 'team', 'startup', 'into', 'highly', 
    'plus', 'degree', 'bachelors'
}

class ScoringEngine:
    def __init__(self):
        # We use the free Hugging Face Inference API instead of running SentenceTransformer locally
        self.api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
        self.hf_token = getattr(settings, "HF_TOKEN", os.getenv("HF_TOKEN"))
        self.headers = {"Authorization": f"Bearer {self.hf_token}"} if self.hf_token else {}
        print("DEBUG: ScoringEngine initialized with HF API. Memory footprint: Minimal.")

    def get_embedding(self, text: str) -> np.ndarray:
        """Fetches vector embeddings from Hugging Face API"""
        try:
            # We strictly limit text to roughly 4000 chars to avoid API payload limits
            truncated_text = text[:4000]
            response = requests.post(
                self.api_url, 
                headers=self.headers, 
                json={"inputs": [truncated_text], "options": {"wait_for_model": True}},
                timeout=20
            )
            if response.status_code == 200:
                result = response.json()
                # The API returns a list of lists, we grab the first embedding
                return np.array(result[0] if isinstance(result[0], list) else result)
            else:
                print(f"HF API Error: {response.status_code} - {response.text}")
                return np.zeros(384) # Fallback empty vector (all-MiniLM-L6-v2 is 384d)
        except Exception as e:
            print(f"HF API Exception: {e}")
            return np.zeros(384)

    def extract_entities(self, text: str) -> Dict:
        """Extract Experience and Education using Heuristics (Replaces heavy spaCy model)"""
        text_lower = text.lower()
        
        # Simple heuristic for Education
        edu_keywords = ["bachelor", "master", "phd", "university", "college", "degree", "b.sc", "b.tech", "m.sc"]
        education = "Not identified"
        for word in edu_keywords:
            if word in text_lower:
                education = f"{word.capitalize()} found"
                break
                
        # Simple heuristic for Years of Experience
        exp_match = re.search(r'(\d+)\+?\s*(years?|yrs?)\s+(of\s+)?experience', text_lower)
        experience = f"{exp_match.group(1)} years+" if exp_match else "Not explicitly specified"
        
        return {
            "companies": ["Analyzed via Lightweight Heuristics mode"],
            "experience": experience,
            "education": education
        }

    def calculate_category_scores(self, resume_text: str, jd_text: str) -> List[Dict]:
        """Calculate match scores per category for the Radar Chart"""
        scores = []
        resume_lower = resume_text.lower()
        jd_lower = jd_text.lower()
        
        for category, skills in SKILL_CATEGORIES.items():
            jd_skills = [s for s in skills if s in jd_lower]
            if not jd_skills:
                continue
                
            matched = [s for s in jd_skills if s in resume_lower]
            score = (len(matched) / len(jd_skills)) * 100 if jd_skills else 0
            scores.append({"category": category, "score": round(score)})
            
        return scores

    def calculate_keyword_score(self, resume_text: str, jd_text: str) -> Dict:
        resume_words = set(re.findall(r'\w+', resume_text.lower()))
        jd_words = set(re.findall(r'\w+', jd_text.lower()))

        jd_keywords = [w for w in jd_words if (w in TECH_KEYWORDS or (len(w) > 3 and w not in STOP_WORDS))]
        
        strong_matches = [w for w in jd_keywords if w in resume_words]
        missing_areas = [w for w in jd_keywords if w not in resume_words]

        return {
            "strong_matches": list(set(strong_matches)),
            "missing_areas": list(set(missing_areas))
        }

    def analyze(self, resume_text: str, jd_text: str) -> Dict:
        print("DEBUG: Sending text to Hugging Face API for vector embeddings...")
        resume_emb = self.get_embedding(resume_text)
        jd_emb = self.get_embedding(jd_text)
        
        # Semantic similarity
        if norm(resume_emb) == 0 or norm(jd_emb) == 0:
            score = 0  # Fallback if API totally failed
        else:
            similarity = float((resume_emb @ jd_emb.T) / (norm(resume_emb) * norm(jd_emb)))
            score = similarity * 100

        # Keyword analysis
        resume_keywords = self.calculate_keyword_score(resume_text, jd_text)
        entities = self.extract_entities(resume_text)
        categories = self.calculate_category_scores(resume_text, jd_text)

        total_keywords = len(resume_keywords['strong_matches']) + len(resume_keywords['missing_areas'])
        keyword_score = (len(resume_keywords['strong_matches']) / max(total_keywords, 1)) * 100
        
        # Final score blending: 60% semantic similarity, 40% exact keyword match
        final_score = (score * 0.6) + (keyword_score * 0.4)
        # If API failed, lean 100% on keyword matching
        if score == 0:
            final_score = keyword_score
            
        final_score = round(min(max(final_score, 0), 100), 2)

        return {
            "score": final_score,
            "explanation": f"Candidate is an {self.get_match_level(final_score)} match with a score of {final_score}%. "
                           f"Key strengths identified in {', '.join(resume_keywords['strong_matches'][:3]) if resume_keywords['strong_matches'] else 'general areas'}.",
            "strong_skills": resume_keywords['strong_matches'],
            "missing_skills": resume_keywords['missing_areas'],
            "suggestions": self.generate_suggestions(resume_keywords['missing_areas']),
            "entities": entities,
            "categories": categories
        }

    def get_match_level(self, score: float) -> str:
        if score >= 80: return "exceptional"
        if score >= 60: return "strong"
        if score >= 40: return "moderate"
        return "developing"

    def generate_suggestions(self, missing_skills: List[str]) -> List[str]:
        if not missing_skills:
            return ["Resume is highly optimized. Consider adding specific project metrics."]
        
        tech_missing = [s for s in missing_skills if s in TECH_KEYWORDS]
        suggestions = []
        if tech_missing:
            suggestions.append(f"Consider adding more details about your experience with: {', '.join(tech_missing[:5])}.")
        suggestions.append("Quantify your achievements with metrics to show impact (e.g., 'Improved performance by 20%').")
        suggestions.append("Ensure your summary highlights your most relevant projects for this specific job description.")
        return suggestions

