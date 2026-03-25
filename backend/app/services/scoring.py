import re
import os
import requests
import numpy as np
from typing import List, Dict
from numpy.linalg import norm
from ..config import settings

# Technical Skill Categories
SKILL_CATEGORIES = {
    "Frontend": ["react", "vue", "angular", "next.js", "tailwind", "html", "css", "javascript", "typescript", "flutter", "responsive"],
    "Backend": ["fastapi", "flask", "django", "node.js", "express", "go", "rust", "python", "java", "spring", "boot", "node", "rest", "restful", "apis", "api", "frameworks", "backend"],
    "Databases": ["postgresql", "mongodb", "sql", "nosql", "redis", "elasticsearch", "pinecone", "chroma", "mysql", "database", "databases"],
    "Cloud/DevOps": ["aws", "docker", "kubernetes", "git", "ci/cd", "terraform", "azure", "gcp", "github", "pipelines", "cloud", "production", "scalability"],
    "AI/ML": ["pytorch", "tensorflow", "rag", "embeddings", "nlp", "transformers", "llm", "langchain", "models", "evaluation", "openai", "huggingface", "ai", "semantic"]
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

        # ONLY match rigorous technical keywords to avoid generic English words like "hands", "with", "data"
        jd_keywords = [w for w in jd_words if w in TECH_KEYWORDS]
        
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

        # Generate dynamic, recruiter-style multi-sentence analysis
        ex_level = self.get_match_level(final_score).upper()
        
        if resume_keywords['strong_matches']:
            strengths_str = ", ".join([sk.title() for sk in resume_keywords['strong_matches'][:4]])
            base_exp = f"This resume represents a {ex_level} match for the role ({final_score}% relevance). The candidate showcases a robust technical foundation, particularly excelling in {strengths_str}."
        else:
            base_exp = f"This resume indicates a {ex_level} match ({final_score}% relevance). However, it struggles to demonstrate the core technical competencies required for this specific role."

        if resume_keywords['missing_areas']:
            gaps_str = ", ".join([sk.title() for sk in resume_keywords['missing_areas'][:3]])
            if final_score > 60:
                base_exp += f" While the profile is strong overall, the absence of explicit experience with {gaps_str} might place them at a slight disadvantage compared to perfectly aligned peers."
            else:
                base_exp += f" A significant hurdle is the lack of visible experience with critical requirements like {gaps_str}. The candidate must bridge this gap to be considered competitive."
        else:
            base_exp += " The candidate seamlessly aligns with virtually every technical requirement listed in the job description, making them an exceptionally competitive applicant."

        base_exp += " To maximize their chances of securing an interview, the candidate should heed the targeted suggestions below to optimize their portfolio and resume narrative."

        current_analysis = {
            "score": final_score,
            "explanation": base_exp,
            "strong_skills": resume_keywords['strong_matches'],
            "missing_skills": resume_keywords['missing_areas'],
            "suggestions": self.generate_suggestions(resume_keywords['strong_matches'], resume_keywords['missing_areas'])
        }

        llm_insights = self.generate_llm_insights(resume_text, jd_text, current_analysis)

        return {
            "score": final_score,
            "llm_insights": llm_insights,
            "entities": entities,
            "categories": categories,
            # Keep legacy
            "explanation": base_exp,
            "strong_skills": resume_keywords['strong_matches'],
            "missing_skills": resume_keywords['missing_areas'],
            "suggestions": current_analysis["suggestions"]
        }

    def generate_llm_insights(self, resume_text: str, jd_text: str, current: Dict) -> Dict:
        # Use a faster, highly reliable model for JSON instruction following on free tier
        api_url = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
        
        # Limit text length to avoid token limits on free HF Inference API
        safe_resume = resume_text[:1800]
        safe_jd = jd_text[:1200]
        
        prompt = f"""<|system|>
You are an expert AI recruiter. Return ONLY a valid JSON object. Do NOT include markdown blocks. Do NOT include any extra text.
</s>
<|user|>
Analyze this and return the exact JSON format requested.
Resume: {safe_resume}
Job Description: {safe_jd}
Base Score: {current['score']}%

Format required:
{{
  "refined_match_summary": "Briefly explain the score",
  "strong_matches": [{{"skill": "Name", "reason": "Short reason"}}],
  "critical_gaps": [{{"skill": "Name", "explanation": "Short explanation"}}],
  "inferred_skills": ["Skill 1", "Skill 2"],
  "recruiter_insights": ["Insight 1", "Insight 2"],
  "action_plan": ["Action 1", "Action 2"],
  "substitutable_skills": [{{"required": "req", "alternative": "alt", "explanation": "why"}}]
}}
</s>
<|assistant|>
{{"""
        import json
        try:
            print("DEBUG: Calling HF Instruct model for RAG insights...")
            response = requests.post(
                api_url, 
                headers=self.headers, 
                json={"inputs": prompt, "parameters": {"max_new_tokens": 1000, "return_full_text": False, "temperature": 0.1}}, 
                timeout=25
            )
            if response.status_code == 200:
                result = response.json()
                generated_text = "{" + result[0]['generated_text'].strip()
                
                # Further cleanup to ensure we can parse
                generated_text = generated_text.replace("```json", "").replace("```", "").strip()
                
                return json.loads(generated_text)
            else:
                print(f"HF Gen API Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"HF Gen API Exception: {str(e)}")
            
        # Fallback
        return {
            "refined_match_summary": current["explanation"] + " (Note: Deep Insights fallback activated due to high AI load.)",
            "strong_matches": [{"skill": s, "reason": "Matching keyword"} for s in current["strong_skills"]],
            "critical_gaps": [{"skill": s, "explanation": "Missing core requirement"} for s in current["missing_skills"]],
            "inferred_skills": ["Evaluated via exact matching algorithms (AI inference temporarily unavailable)."],
            "recruiter_insights": ["Solid baseline matching completed. Review manual checks for nuanced overlaps."],
            "action_plan": current["suggestions"],
            "substitutable_skills": []
        }

    def get_match_level(self, score: float) -> str:
        if score >= 80: return "Exceptional"
        if score >= 60: return "Strong"
        if score >= 40: return "Moderate"
        return "Developing"

    def generate_suggestions(self, strong_skills: List[str], missing_skills: List[str]) -> List[str]:
        suggestions = []
        tech_missing = [s for s in missing_skills if s in TECH_KEYWORDS]
        
        # 1. Address Missing Gaps to standout
        if tech_missing:
            top_missing = tech_missing[:3]
            suggestions.append(f"CRITICAL GAP: The JD heavily emphasizes {', '.join([m.title() for m in top_missing])}. If you have even partial experience with these, add a dedicated bullet point detailing a project where you utilized them.")
        else:
            suggestions.append("YOUR ADVANTAGE: Your skill stack perfectly aligns with the JD! Focus entirely on quantifying your impact rather than adding new buzzwords.")

        # 2. Leverage Existing Strengths
        if strong_skills:
            top_strength = strong_skills[0].title()
            suggestions.append(f"SHOWCASE EXPERTISE: You matched on '{top_strength}'. Don't just list it—prove it. Add metrics (e.g., 'Scaled a {top_strength} application to handle 10k+ daily active users' or 'Reduced latency by 30% using {top_strength}').")
        
        # 3. Actionable Portfolio tip
        if "github" in missing_skills or "git" in missing_skills:
            suggestions.append("PORTFOLIO TIP: The recruiter is looking for version control / GitHub experience. Link a live codebase or open-source contribution at the very top of your resume.")
        elif tech_missing:
            suggestions.append(f"STAND OUT: To beat out senior candidates, build and deploy a rapid weekend prototype combining your existing skills with {tech_missing[0].title()}, and hyperlink it in your resume header.")
        else:
            suggestions.append("STAND OUT: You are a top-tier match. Ensure your LinkedIn profile is equally optimized and reach out directly to the hiring manager with a brief summary of how your stack perfectly mirrors their requirements.")

        return suggestions

