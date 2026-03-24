from typing import List, Dict
from .scoring import ScoringEngine

class Analyzer:
    def __init__(self, scoring_engine: ScoringEngine):
        self.scoring_engine = scoring_engine

    def generate_analysis(self, resume_text: str, jd_text: str, top_chunks: List[Dict]) -> Dict:
        """Generates a detailed analysis with recruiter-level reasoning."""
        
        # Calculate scores
        keyword_data = self.scoring_engine.calculate_keyword_score(resume_text, jd_text)
        
        # Average semantic score from top chunks
        avg_semantic = sum([c['score'] for c in top_chunks]) / len(top_chunks) * 100 if top_chunks else 0
        
        final_score = self.scoring_engine.combine_scores(avg_semantic, keyword_data['score'])
        
        # Generate Explanation
        explanation = self._craft_explanation(final_score, keyword_data, top_chunks)
        
        # Generate Suggestions
        suggestions = self._generate_suggestions(keyword_data)

        return {
            "score": final_score,
            "strong_skills": keyword_data['matched_keywords'][:10],
            "missing_skills": keyword_data['missing_keywords'][:10],
            "explanation": explanation,
            "suggestions": suggestions
        }

    def _craft_explanation(self, score: float, keyword_data: Dict, chunks: List[Dict]) -> str:
        """Crafts a professional explanation based on the matching results."""
        if score > 80:
            level = "excellent match"
            tone = "highly recommended for this position."
        elif score > 60:
            level = "good match"
            tone = "a strong contender, though some specific skills could be highlighted further."
        else:
            level = "moderate match"
            tone = "significant gaps in required competencies compared to the job description."

        explanation = f"Candidate is an {level} with a score of {score}%. "
        explanation += f"Our analysis shows a strong overlap in key areas like: {', '.join(keyword_data['matched_keywords'][:5])}. "
        
        if keyword_data['missing_keywords']:
            explanation += f"However, the candidate seems to lack explicit mentions of {', '.join(keyword_data['missing_keywords'][:3])}. "
        
        explanation += f"Overall, the candidate is {tone}"
        return explanation

    def _generate_suggestions(self, keyword_data: Dict) -> List[str]:
        """Generates actionable suggestions for the candidate."""
        suggestions = []
        if keyword_data['missing_keywords']:
            missing = keyword_data['missing_keywords'][:5]
            suggestions.append(f"Consider adding more details about your experience with: {', '.join(missing)}.")
        
        suggestions.append("Quantify your achievements with metrics to show impact.")
        suggestions.append("Ensure your summary highlights your most relevant projects for this specific JD.")
        return suggestions
