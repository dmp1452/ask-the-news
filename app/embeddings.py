import faiss
import numpy as np
import os
import pickle
from typing import List, Tuple

EMBEDDING_DIM = 384
INDEX_FILE = "vector_store.faiss"
ID_MAP_FILE = "vector_id_map.pkl"

vector_id_map = []
class VectorStore:
    def __init__(self):
        self.index: faiss.IndexFlatIP = self.create_index()
        self.id_map: List[str] = []
        self.load_index_and_map() 
    
    def create_index(self) -> faiss.IndexFlatIP:
        index = faiss.IndexFlatIP(EMBEDDING_DIM)
        return index

    def normalize(self,vector: np.ndarray):
        norm = np.linalg.norm(vector)
        return vector / norm if norm != 0 else vector

    def add_to_index(self, embedding: np.ndarray, article_id: str):
        vec = self.normalize(embedding).astype("float32").reshape(1, -1)
        self.index.add(vec)  # type: ignore
        self.id_map.append(article_id)


    def search_index(self, query_embedding: np.ndarray, top_k=5):
        vec = self.normalize(query_embedding).astype("float32").reshape(1, -1)
        distances, indices = self.index.search(vec, top_k)  # type: ignore
        return indices[0], distances[0] 


    def save_index(self):
        try:
            faiss.write_index(self.index, INDEX_FILE)
            with open(ID_MAP_FILE, "wb") as f:
                pickle.dump(self.id_map, f)
            print(f"Index and ID map saved to {INDEX_FILE} and {ID_MAP_FILE}.")
        except Exception as e:
            print(f"Error saving index: {e}")


    def load_index_and_map(self):
        if os.path.exists(INDEX_FILE) and os.path.exists(ID_MAP_FILE):
            try:
                self.index = faiss.read_index(INDEX_FILE)
                with open(ID_MAP_FILE, "rb") as f:
                    self.id_map = pickle.load(f)
                print(f"Loaded existing index with {len(self.id_map)} embeddings.")
            except Exception as e:
                print(f"Could not load existing index ({e}). Creating a new one.")
                self.index = self.create_index()
                self.id_map = []
        else:
            print("ℹNo existing index found. A new index will be created.")
            self.index = self.create_index()
            self.id_map = []

    def get_index_size(self) -> int:
        return self.index.ntotal
    
    def get_id_map(self) -> List[str]:
        return self.id_map