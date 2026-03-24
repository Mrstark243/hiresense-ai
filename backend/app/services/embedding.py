from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingService:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, texts: list) -> np.ndarray:
        """Generates embeddings for a list of texts."""
        if not texts:
            return np.array([])
        return self.model.encode(texts, convert_to_numpy=True)

    def generate_single_embedding(self, text: str) -> np.ndarray:
        """Generates an embedding for a single text."""
        return self.model.encode([text], convert_to_numpy=True)
