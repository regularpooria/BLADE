import json

# from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import torch
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoModel, AutoTokenizer
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm
from dotenv import load_dotenv
import os

load_dotenv()


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


# def embed():
#     dataset = load_dataset("toy_bugs.json")
#     inputs = [prepare_input(bug) for bug in dataset]
#     embeddings = model.encode(inputs)
#     return embeddings


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
MODEL_NAME = os.getenv("MODEL_NAME") or "blaze"
# model = SentenceTransformer(MODEL_NAME, trust_remote_code=True, device=device)
# model.half()
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
model = AutoModel.from_pretrained(MODEL_NAME, trust_remote_code=True)
torch.no_grad()

BATCH_SIZE = int(os.getenv("BATCH_SIZE", 128))
# model.max_seq_length = 1024
# embeddings = embed()
# index = index_embeddings(embeddings)


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


def compute_masked_embedding(
    embedding: torch.Tensor, attention_mask: torch.Tensor
) -> torch.Tensor:
    input_mask_expanded = (
        attention_mask.unsqueeze(-1).expand(embedding.size()).to(embedding.dtype)
    )
    sum_embeddings = torch.sum(embedding * input_mask_expanded, dim=1)
    sum_mask = input_mask_expanded.sum(dim=1)
    sum_mask = torch.clamp(sum_mask, min=1e-9)
    embedding = sum_embeddings / sum_mask
    return embedding


def embed(strings, batch_size=8, show_progress_bar=True):
    model.eval()
    embeddings = []

    dataloader = DataLoader(strings, batch_size=batch_size)
    if show_progress_bar:
        dataloader = tqdm(dataloader, desc="Embedding")

    for batch in dataloader:
        # Tokenize batch of strings
        tokenized = tokenizer(
            batch, return_tensors="pt", padding=True, truncation=True, max_length=1024
        )

        with torch.no_grad():
            output = model(**tokenized)

        # Compute masked embedding for each sample in batch
        batch_embeddings = compute_masked_embedding(
            output.last_hidden_state, tokenized["attention_mask"]
        )
        embeddings.extend(batch_embeddings)

    return embeddings  # List of [hidden_dim] vectors
