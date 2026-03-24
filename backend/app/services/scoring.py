import re
from typing import List, Dict
import spacy
from sentence_transformers import SentenceTransformer
from numpy.linalg import norm

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
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # Initialize spaCy for NER
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except:
            self.nlp = None

    def extract_entities(self, text: str) -> Dict:
        """Extract Companies, Experience, and Education using spaCy"""
        if not self.nlp:
            return {"companies": [], "experience": "Unknown", "education": "Unknown"}
            
        doc = self.nlp(text[:10000]) # Limit for performance
        companies = list(set([ent.text for ent in doc.ents if ent.label_ == "ORG"]))
        dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
        
        # Simple heuristic for Education
        edu_keywords = ["Bachelor", "Master", "PhD", "University", "College", "Degree"]
        education = "Not identified"
        for word in edu_keywords:
            if word.lower() in text.lower():
                education = f"{word} found"
                break
                
        return {
            "companies": companies[:5],
            "experience": f"Timeline identified in: {', '.join(dates[:3])}" if dates else "Not specified",
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
                # If JD doesn't mention this category, give a default high score or skip
                continue
                
            matched = [s for s in jd_skills if s in resume_lower]
            score = (len(matched) / len(jd_skills)) * 100 if jd_skills else 0
            scores.append({"category": category, "score": round(score)})
            
        return scores

    def analyze(self, resume_text: str, jd_text: str) -> Dict:
        # Embedding-based similarity
        resume_emb = self.model.encode(resume_text)
        jd_emb = self.model.encode(jd_text)
        similarity = float((resume_emb @ jd_emb.T) / (norm(resume_emb) * norm(jd_emb)))
        score = similarity * 100

        # Keyword analysis
        resume_keywords = self.calculate_keyword_score(resume_text, jd_text)
        entities = self.extract_entities(resume_text)
        categories = self.calculate_category_scores(resume_text, jd_text)

        # Restore perfect 60/40 scoring match calculation from original analyzer
        total_keywords = len(resume_keywords['strong_matches']) + len(resume_keywords['missing_areas'])
        keyword_score = (len(resume_keywords['strong_matches']) / max(total_keywords, 1)) * 100
        
        # Final score blending: 60% semantic similarity, 40% exact keyword match
        final_score = (score * 0.6) + (keyword_score * 0.4)
        final_score = round(min(max(final_score, 0), 100), 2)

        return {
            "score": final_score,
            "explanation": f"Candidate is an {self.get_match_level(final_score)} match with a score of {final_score}%. "
                           f"Our deep tech analysis identified key strengths in {', '.join(resume_keywords['strong_matches'][:3])}.",
            "strong_skills": resume_keywords['strong_matches'],
            "missing_skills": resume_keywords['missing_areas'],
            "suggestions": self.generate_suggestions(resume_keywords['missing_areas']),
            "entities": entities,
            "categories": categories
        }

    def calculate_keyword_score(self, resume_text: str, jd_text: str) -> Dict:
        resume_words = set(re.findall(r'\w+', resume_text.lower()))
        jd_words = set(re.findall(r'\w+', jd_text.lower()))

        # Filter keywords
        jd_keywords = [w for w in jd_words if (w in TECH_KEYWORDS or (len(w) > 3 and w not in STOP_WORDS))]
        
        strong_matches = [w for w in jd_keywords if w in resume_words]
        missing_areas = [w for w in jd_keywords if w not in resume_words]

        return {
            "strong_matches": list(set(strong_matches)),
            "missing_areas": list(set(missing_areas))
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

from numpy.linalg import norm
