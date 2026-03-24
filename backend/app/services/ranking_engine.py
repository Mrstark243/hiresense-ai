from typing import List, Dict

class RankingEngine:
    @staticmethod
    def rank_candidates(candidates: List[Dict]) -> List[Dict]:
        """Ranks candidates based on their match score."""
        # Sort by score descending
        ranked = sorted(candidates, key=lambda x: x['score'], reverse=True)
        
        # Add ranking reasoning
        for i, candidate in enumerate(ranked):
            candidate['rank'] = i + 1
            if i == 0:
                candidate['ranking_reason'] = "Top candidate due to highest overall match and skill overlap."
            else:
                diff = ranked[0]['score'] - candidate['score']
                candidate['ranking_reason'] = f"Ranked #{i+1}, showing {diff:.1f}% less match than the top candidate."
        
        return ranked
