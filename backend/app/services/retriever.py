import faiss
import numpy as np

class VectorStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.chunks = []

    def add_chunks(self, chunks: list, embeddings: np.ndarray):
        """Adds chunks and their embeddings to the index."""
        if len(chunks) == 0:
            return
        self.index.add(embeddings.astype('float32'))
        self.chunks.extend(chunks)

    def search(self, query_embedding: np.ndarray, k: int = 5):
        """Searches for top-k similar chunks."""
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.chunks):
                results.append({
                    "chunk": self.chunks[idx],
                    "score": float(1 / (1 + distances[0][i]))  # Normalize distance to 0-1
                })
        return results

    def reset(self):
        """Resets the vector store."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = []
