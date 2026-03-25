import re
import os
import requests
import numpy as np
from typing import List, Dict
from numpy.linalg import norm
from ..config import settings

# Semantic Skill Normalization Groups
SKILL_GROUPS = {
    "api_development": ["rest", "restful", "api", "apis"],
    "databases": ["mysql", "postgresql", "sql", "database"],
    "nosql": ["mongodb", "redis", "elasticsearch", "pinecone", "chroma"],
    "cloud": ["aws", "gcp", "azure", "cloud"],
    "devops": ["docker", "kubernetes", "ci", "cd", "pipelines", "ci/cd", "terraform"],
    "backend": ["fastapi", "flask", "django", "node", "node.js", "express", "go", "rust", "python", "java", "spring", "backend"],
    "frontend": ["react", "vue", "angular", "next.js", "tailwind", "html", "css", "javascript", "typescript", "responsive"],
    "ai_and_ml": ["rag", "llm", "nlp", "transformers", "pytorch", "tensorflow", "openai", "huggingface", "embeddings", "langchain", "semantic", "ai"]
}

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
        """Calculate match scores per semantic group for visualization"""
        scores = []
        resume_lower = resume_text.lower()
        jd_lower = jd_text.lower()
        
        for category, skills in SKILL_GROUPS.items():
            jd_skills = [s for s in skills if s in jd_lower]
            if not jd_skills:
                continue
                
            matched = [s for s in jd_skills if s in resume_lower]
            score = (len(matched) / len(jd_skills)) * 100 if jd_skills else 0
            scores.append({"category": category.replace('_', ' ').capitalize(), "score": round(score)})
            
        return scores

    def calculate_keyword_score(self, resume_text: str, jd_text: str) -> Dict:
        resume_lower = resume_text.lower()
        jd_lower = jd_text.lower()

        strong_groups = set()
        partial_groups = set()
        missing_groups = set()
        evidence_map = {}

        # Semantic Group Matching (replacing raw keyword collision)
        for group_name, keywords in SKILL_GROUPS.items():
            # If the JD asks for any term in this semantic group
            if any(re.search(rf'\b{re.escape(kw)}\b', jd_lower) for kw in keywords):
                matched_kws = [kw for kw in keywords if re.search(rf'\b{re.escape(kw)}\b', resume_lower)]
                required_kws = [kw for kw in keywords if re.search(rf'\b{re.escape(kw)}\b', jd_lower)]
                
                if matched_kws:
                    evidence_map[group_name] = matched_kws
                    
                    # CLOUD
                    if group_name == "cloud":
                        if any(k in resume_lower for k in ["aws", "gcp", "azure"]):
                            if any(k in resume_lower for k in ["deploy", "deployment", "ec2", "hosting", "production"]):
                                strong_groups.add(group_name)
                            else:
                                partial_groups.add(group_name)
                                missing_groups.add("cloud deployment")
                        else:
                            partial_groups.add(group_name)
                            
                    # AI/ML
                    elif group_name == "ai_and_ml":
                        if "llm" in resume_lower and any(k in resume_lower for k in ["fine-tuning", "training", "deployment"]):
                            strong_groups.add(group_name)
                        else:
                            partial_groups.add(group_name)
                            
                    # DATABASES
                    elif group_name == "databases":
                        if len(matched_kws) >= 2:
                            strong_groups.add(group_name)
                        else:
                            partial_groups.add(group_name)
                            
                    # DEVOPS
                    elif group_name == "devops":
                        if re.search(r'\bdocker\b', resume_lower) and re.search(r'\bkubernetes\b', resume_lower):
                            strong_groups.add(group_name)
                        else:
                            partial_groups.add(group_name)
                            
                        if any(req in required_kws for req in ["ci", "cd", "pipelines", "ci/cd"]):
                            if not any(m in matched_kws for m in ["ci", "cd", "pipelines", "ci/cd"]):
                                missing_groups.add("ci/cd pipelines")
                            
                    # BACKEND
                    elif group_name == "backend":
                        backend_frameworks = ["fastapi", "django", "flask", "node", "express", "spring"]
                        if any(re.search(rf'\b{re.escape(f)}\b', resume_lower) for f in backend_frameworks) and re.search(r'\bapi\b', resume_lower):
                            strong_groups.add(group_name)
                        else:
                            partial_groups.add(group_name)
                            
                    # DEFAULT RULE
                    else:
                        partial_groups.add(group_name)
                else:
                    # Semantic Proxy: Docker/K8s gives partial Cloud credit
                    if group_name == "cloud":
                        proxy_kws = [k for k in ["docker", "kubernetes"] if re.search(rf'\b{re.escape(k)}\b', resume_lower)]
                        if proxy_kws:
                            partial_groups.add(group_name)
                            evidence_map[group_name] = proxy_kws
                            missing_groups.add("cloud deployment")
                        else:
                            missing_groups.add(group_name)
                    else:
                        missing_groups.add(group_name)
                    
        print("STRONG:", strong_groups)
        print("PARTIAL:", partial_groups)
        print("MISSING:", missing_groups)

        return {
            "strong_matches": list(strong_groups),
            "partial_matches": list(partial_groups),
            "missing_areas": list(missing_groups),
            "evidence_map": evidence_map
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

        total_keywords = len(resume_keywords['strong_matches']) + len(resume_keywords['missing_areas']) + len(resume_keywords['partial_matches'])
        # Partial matches get 0.5 weight instead of full reduction
        weighted_score = len(resume_keywords['strong_matches']) + (0.5 * len(resume_keywords['partial_matches']))
        keyword_score = (weighted_score / max(total_keywords, 1)) * 100
        
        # Final score blending: 60% semantic similarity, 40% exact keyword match
        final_score = (score * 0.6) + (keyword_score * 0.4)
        # If API failed, lean 100% on keyword matching
        if score == 0:
            final_score = keyword_score
            
        # Apply logic floors: No explicit gaps but possess partials -> highly viable
        if not resume_keywords['missing_areas'] and resume_keywords['partial_matches']:
            final_score = max(final_score, 70)
            
        final_score = round(min(max(final_score, 0), 100), 2)
        
        # HARD SCORE LIMITS
        if resume_keywords['partial_matches']:
            final_score = min(final_score, 90)
            
        if resume_keywords['missing_areas']:
            final_score = min(final_score, 85)

        # Generate dynamic, recruiter-style multi-sentence analysis
        ex_level = self.get_match_level(final_score).upper()
        
        if resume_keywords['strong_matches']:
            strengths_str = ", ".join([sk.replace('_', ' ').title() for sk in resume_keywords['strong_matches'][:4]])
            base_exp = f"This resume represents a {ex_level} match for the role ({final_score}% relevance). The candidate showcases a robust technical foundation, particularly excelling in {strengths_str}."
        else:
            base_exp = f"This resume indicates a {ex_level} match ({final_score}% relevance). However, it struggles to demonstrate the core technical competencies required for this specific role."

        if resume_keywords['missing_areas']:
            gaps_str = ", ".join([sk.title() for sk in resume_keywords['missing_areas'][:3]])
            if final_score > 60:
                base_exp += f" While the profile is strong overall, the absence of explicit experience with {gaps_str} might place them at a slight disadvantage compared to perfectly aligned peers."
            else:
                base_exp += f" A significant hurdle is the lack of visible experience with critical requirements like {gaps_str}. The candidate must bridge this gap to be considered competitive."
        elif resume_keywords['partial_matches']:
            base_exp += " The candidate shows strong alignment with core requirements, with some areas requiring deeper ecosystem exposure."
        else:
            base_exp += " The candidate seamlessly aligns with virtually every technical requirement listed in the job description, making them an exceptionally competitive applicant."

        if resume_keywords['partial_matches']:
            base_exp += " The score reflects partial exposure in certain domains rather than a complete lack of skills."

        base_exp += " To maximize their chances of securing an interview, the candidate should heed the targeted suggestions below to optimize their portfolio and resume narrative."

        current_analysis = {
            "score": final_score,
            "explanation": base_exp,
            "strong_skills": resume_keywords['strong_matches'],
            "partial_skills": resume_keywords['partial_matches'],
            "missing_skills": resume_keywords['missing_areas'],
            "evidence_map": resume_keywords.get('evidence_map', {}),
            "suggestions": self.generate_suggestions(resume_keywords['strong_matches'], resume_keywords['missing_areas'], resume_keywords['partial_matches'])
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
You are a senior AI recruiter. Return ONLY valid JSON matching the schema exactly. Do NOT include markdown blocks.

CRITICAL RULES:
1. PARTIAL MATCH OVERRIDES GAP: If ANY related skill exists, NEVER mark these as Explicit Gaps. Partial Matches must NOT be listed under 'critical_gaps'. They have their own 'partial_matches' json section.
2. NO CONTRADICTIONS: A skill cannot appear in both matches and gaps. If a skill is listed in partial_matches, you MUST classify it as Partial Match. Do NOT upgrade it to Strong Match.
3. EVIDENCE MUST BE REAL: Extract actual phrases/tools from resume. BAD: "Extracted from profile", "Related ecosystem tools". GOOD: "Worked with Django and REST API concepts", "Used Docker and Kubernetes for deployment".
4. SUBSTITUTION IS MANDATORY: If Partial Match exists -> ALWAYS include: Required Skill, Candidate Skill (MUST BE SPECIFIC TOOLS), Transferability, Learning Curve, Explanation.
5. ACTION PLAN MUST BE PRACTICAL: Each suggestion must include: Exact tech stack, Real deployment or project.
6. HIRE SIGNAL RULE: Score > 80 -> Strong Hire. Score 60-80 -> Potential Hire. Score < 60 -> Needs Improvement.
</s>
<|user|>
Analyze this candidate.
Resume: {safe_resume}
Job Description: {safe_jd}
Pre-processed Base Score: {current['score']}%

IMPORTANT: You are given Preprocessed Skill Groups:
- strong_matches: {current['strong_skills']}
- partial_matches: {current['partial_skills']}
- missing_skills: {current['missing_skills']}

These skills are already normalized and grouped by the engine. Do NOT treat them as raw keywords. Evaluate candidate potential and adaptability.

Format required (STRICT JSON ONLY):
{{
  "refined_match_summary": "...",
  "match_score": {current['score']},
  "confidence_score": "High | Medium | Low",
  "hire_signal": "Strong Hire | Potential Hire | Needs Improvement | Not Ready",
  "strong_matches": [{{"skill": "...", "level": "Beginner | Intermediate | Advanced", "reason": "...", "evidence": "Specific evidence from resume"}}],
  "partial_matches": [{{"skill": "...", "reason": "...", "evidence": "Specific evidence from resume"}}],
  "critical_gaps": [{{"skill": "...", "classification": "Explicit Gap | Weak Match", "explanation": "...", "evidence": "..."}}],
  "substitutable_skills": [{{"required": "...", "candidate": "...", "transferability": "High | Medium | Low", "learning_curve": "...", "explanation": "..."}}],
  "inferred_skills": [{{"skill": "...", "derived_from": "...", "reason": "..."}}],
  "recruiter_insights": ["..."],
  "action_plan": [{{"type": "Project | Resume | Skill", "title": "...", "description": "...", "impact": "..."}}]
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
            
        # Fallback ensuring clean group-level response
        partial_matches = []
        for s in current["partial_skills"]:
            evidence_str = ", ".join(current["evidence_map"].get(s, ["foundational concepts"]))
            partial_matches.append({"skill": s.replace('_', ' ').title(), "evidence": f"Candidate possesses exposure via '{evidence_str}'", "reason": f"Demonstrates core competency without full ecosystem scope via {evidence_str}"})
            
        critical_gaps = []
        for s in current["missing_skills"]:
            critical_gaps.append({"skill": s.replace('_', ' ').title(), "classification": "Explicit Gap", "explanation": "This ecosystem capability is completely missing from the candidate's core stack.", "evidence": "No related tools or abstract domains matched"})
            
        substitutions = []
        for s in current["partial_skills"]:
             candidate_skill = ", ".join(current["evidence_map"].get(s, ["adjacent tools"]))
             substitutions.append({
                 "required": s.replace('_', ' ').title(), 
                 "candidate": candidate_skill, 
                 "transferability": "High", 
                 "learning_curve": "Minimal upskilling required; core concepts align.", 
                 "explanation": f"Candidate possesses adjacent capability which translates easily to the {s.replace('_', ' ').title()} requirement."
             })
             
        action_plan = []
        for s in current["missing_skills"]:
            action_plan.append({"type": "Project", "title": f"Productionize {s.replace('_', ' ').title()}", "description": f"Build and deploy a scalable architecture prototype leveraging {s.replace('_', ' ').title()} to prove production readiness.", "impact": "Directly bridges a core JD architectural requirement"})
        if not action_plan and current["partial_skills"]:
            action_plan.append({"type": "Project", "title": f"Deepen {current['partial_skills'][0].replace('_', ' ').title()} expertise", "description": "Deploy a comprehensive project utilizing native stack components over foundational abstractions.", "impact": "Converts partial foundational experience into mastery."})
            
        # Ensure 3 items mathematically
        generic_plans = [
             {"type": "Resume", "title": "Highlight System Design", "description": "Quantify architectural decisions rather than just listing adjacent tools.", "impact": "Proves senior-level awareness."},
             {"type": "Project", "title": "End-to-End Orchestration", "description": "Construct an automated CI/CD pipeline unifying microservices.", "impact": "Validates enterprise readiness."},
             {"type": "Skill", "title": "Domain Driven Design", "description": "Implement strict DDD boundaries in a side API project.", "impact": "Elevates abstract engineering capabilities."}
        ]
        gp_idx = 0
        while len(action_plan) < 3 and gp_idx < len(generic_plans):
             action_plan.append(generic_plans[gp_idx])
             gp_idx += 1
            
        strong_matches = []
        for s in current["strong_skills"]:
            evidence_str = ", ".join(current["evidence_map"].get(s, [s]))
            strong_matches.append({"skill": s.replace('_', ' ').title(), "level": "Intermediate", "reason": "Demonstrated capability in this required domain group.", "evidence": f"Experience aligned via '{evidence_str}'."})

        return {
            "refined_match_summary": current["explanation"],
            "match_score": current['score'],
            "confidence_score": "Medium",
            "hire_signal": "Strong Hire" if current['score'] > 80 else "Potential Hire" if current['score'] >= 60 else "Needs Improvement",
            "strong_matches": strong_matches,
            "partial_matches": partial_matches,
            "critical_gaps": critical_gaps,
            "substitutable_skills": substitutions,
            "inferred_skills": [],
            "recruiter_insights": ["The candidate requires more targeted ecosystem exposure to clear the screening phase."],
            "action_plan": action_plan
        }

    def get_match_level(self, score: float) -> str:
        if score >= 80: return "Exceptional"
        if score >= 60: return "Strong"
        if score >= 40: return "Moderate"
        return "Developing"

    def generate_suggestions(self, strong_skills: List[str], missing_skills: List[str], partial_skills: List[str]) -> List[str]:
        suggestions = []
        
        # 1. Address Missing Gaps to standout
        if missing_skills:
            top_missing = [s.replace('_', ' ').title() for s in missing_skills[:3]]
            suggestions.append(f"CRITICAL GAP: The JD heavily emphasizes {', '.join(top_missing)}. If you have even partial experience with these domains, add a dedicated bullet point detailing a project where you utilized them.")
        elif partial_skills:
            suggestions.append("YOUR ADVANTAGE: You have strong alignment with the core requirements. Focus on building and deploying a deeper project targeting your partial match areas.")
        else:
            suggestions.append("YOUR ADVANTAGE: Your skill stack completely aligns with the JD's semantic requirements! Focus entirely on quantifying your impact.")

        # 2. Leverage Existing Strengths
        if strong_skills:
            top_strength = strong_skills[0].replace('_', ' ').title()
            suggestions.append(f"SHOWCASE EXPERTISE: You demonstrated a strong foundation in '{top_strength}'. Don't just list it—prove it. Add metrics to measure scale and impact.")
        
        # 3. Actionable Portfolio tip
        if "cloud" in missing_skills or "devops" in missing_skills:
            suggestions.append("PORTFOLIO TIP: The recruiter is looking for deployment experience. Link a live codebase or open-source contribution deployed on a public cloud.")
        elif missing_skills:
            suggestions.append(f"STAND OUT: Build and deploy a rapid weekend prototype combining your existing skills with {missing_skills[0].replace('_', ' ').title()}, and hyperlink it in your resume header.")
        else:
            suggestions.append("STAND OUT: You are a top-tier match. Ensure your LinkedIn profile is equally optimized.")

        return suggestions

