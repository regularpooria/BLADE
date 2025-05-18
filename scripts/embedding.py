import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def load_dataset(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
        return data


def prepare_input(bug, strategy="full"):
    if strategy == "code_only":
        return bug["buggy_code"]
    elif strategy == "error_info":
        return f"{bug['symptom']} {bug['stack_trace']}"
    else:
        return f"{bug['symptom']} {bug['stack_trace']} {bug['buggy_code']}"


def embed():
    dataset = load_dataset("toy_bugs.json")
    inputs = [prepare_input(bug) for bug in dataset]
    embeddings = model.encode(inputs)
    return embeddings


def index_embeddings(embeddings):
    embeddings_dim = embeddings[0].shape[0]
    index = faiss.IndexFlatL2(embeddings_dim)
    index.add(np.array(embeddings).astype("float32"))
    return index


model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embed()
index = index_embeddings(embeddings)


def search_bug(bug: dict):
    bugs = load_dataset("toy_bugs.json")
    query_text = prepare_input(bug)
    query_vec = model.encode([query_text])

    D, I = index.search(np.array(query_vec).astype("float32"), k=2)

    scores = cosine_similarity(query_vec, np.array(embeddings).astype("float32"))
    top = np.argsort(scores[0])[::-1]
    for i in top[:2]:
        print("Bug ID:", bugs[i]["id"], "Score:", scores[0][i])
        print("Symptom:", bugs[i]["symptom"])
        print("Buggy Code:", bugs[i]["buggy_code"])
