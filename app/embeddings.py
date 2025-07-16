import faiss
import numpy as np
import os
import pickle

EMBEDDING_DIM = 384
INDEX_FILE = "vector_store.faiss"
ID_MAP_FILE = "vector_id_map.pkl"

vector_id_map = []

def create_index():
    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    return index

def normalize(vector: np.ndarray):
    return vector / np.linalg.norm(vector)

def add_to_index(index, embedding: np.ndarray, article_id: str):
    vec = normalize(embedding).astype("float32").reshape(1, -1)
    index.add(vec)
    vector_id_map.append(article_id)


def search_index(index, query_embedding: np.ndarray, top_k=5):
    vec = normalize(query_embedding).astype("float32").reshape(1, -1)
    scores, indices = index.search(vec, top_k)
    return indices[0], scores[0] 


def save_index(index):
    faiss.write_index(index, INDEX_FILE)
    with open(ID_MAP_FILE, "wb") as f:
        pickle.dump(vector_id_map, f)


def load_index():
    if not os.path.exists(INDEX_FILE):
        return create_index(), []

    index = faiss.read_index(INDEX_FILE)
    with open(ID_MAP_FILE, "rb") as f:
        id_map = pickle.load(f)
    global vector_id_map
    vector_id_map = id_map
    return index, id_map