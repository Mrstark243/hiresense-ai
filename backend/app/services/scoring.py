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
        api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
        prompt = f"""You are an expert AI recruiter refining an existing resume analysis.
        
        INPUT:
        Resume Text: {resume_text[:3000]}
        Job Description: {jd_text[:3000]}
        Current Analysis Score: {current['score']}%
        
        INSTRUCTIONS:
        CONVERT KEYWORD MATCHING TO CONTEXTUAL REASONING.
        Infer hidden skills from resume. Add recruiter-level insights.
        Transform suggestions into actionable strategy with specifics.
        Identify substitutable skills (e.g. Docker <-> Podman).
        
        OUTPUT FORMAT (Strict JSON, no markdown):
        {{
            "refined_match_summary": "Explain WHY this score makes sense based on the JD and Resume",
            "strong_matches": [{{"skill": "Skill Name", "reason": "Reason + Evidence"}}],
            "critical_gaps": [{{"skill": "Skill Name", "explanation": "Explanation + whether implicit match exists"}}],
            "inferred_skills": ["List hidden strengths derived from experience"],
            "recruiter_insights": ["1-2 high-level observations"],
            "action_plan": ["3-5 sharp, non-generic real project ideas/improvements"],
            "substitutable_skills": [{{"required": "Skill", "alternative": "Skill", "explanation": "Why it's transferable"}}]
        }}
        """
        import json
        try:
            print("DEBUG: Calling HF Instruct model for RAG insights...")
            response = requests.post(
                api_url, 
                headers=self.headers, 
                json={"inputs": prompt, "parameters": {"max_new_tokens": 1200, "return_full_text": False, "temperature": 0.2}}, 
                timeout=40
            )
            if response.status_code == 200:
                result = response.json()
                generated_text = result[0]['generated_text'].strip()
                if generated_text.startswith("```json"): generated_text = generated_text[7:]
                if generated_text.startswith("```"): generated_text = generated_text[3:]
                if generated_text.endswith("```"): generated_text = generated_text[:-3]
                
                return json.loads(generated_text)
            else:
                print(f"HF Gen API Error: {response.text}")
        except Exception as e:
            print(f"HF Gen API Exception: {e}")
            
        # Fallback
        return {
            "refined_match_summary": current["explanation"],
            "strong_matches": [{"skill": s, "reason": "Matching keyword"} for s in current["strong_skills"]],
            "critical_gaps": [{"skill": s, "explanation": "Missing core requirement"} for s in current["missing_skills"]],
            "inferred_skills": ["Unable to infer skills, API fallback."],
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

