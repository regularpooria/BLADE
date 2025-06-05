import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import torch
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


bug_prompt = (
    "Represent the Python traceback to find the source code responsible for the error."
)
code_prompt = "Represent the code snippet to match it with a possible error traceback."


# model = SentenceTransformer("flax-sentence-embeddings/st-codesearch-distilroberta-base")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer(
    "flax-sentence-embeddings/all_datasets_v4_MiniLM-L12", device=device
)
embeddings = embed()
index = index_embeddings(embeddings)


def search_bug(bug: dict):
    bugs = load_dataset("toy_bugs.json")
    query_text = prepare_input(bug)
    query_vec = model.encode([query_text], prompt=bug_prompt)

    D, I = index.search(np.array(query_vec).astype("float32"), k=2)

    scores = cosine_similarity(query_vec, np.array(embeddings).astype("float32"))
    top = np.argsort(scores[0])[::-1]
    for i in top[:2]:
        print("Bug ID:", bugs[i]["id"], "Score:", scores[0][i])
        print("Symptom:", bugs[i]["symptom"])
        print("Buggy Code:", bugs[i]["buggy_code"])
