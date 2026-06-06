class RecommendationEngine:
    def recommend(self, exhibitions, preferences=None, top_k:int=5):
        prefs={p.lower() for p in (preferences or [])}; scored=[]
        for exhibition in exhibitions:
            score=exhibition.popularity_score + (2.0 if exhibition.category.lower() in prefs else 0.0); scored.append((score, exhibition))
        return sorted(scored, key=lambda item:item[0], reverse=True)[:top_k]
