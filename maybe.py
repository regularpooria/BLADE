from scripts.bugsinpy_utils import *
from scripts.embedding import BATCH_SIZE, embed
import numpy as np
import os, json

projects = get_projects()
embedding_cache = {}
texts_to_embed = []
text_to_indices = {}

# First pass: collect all unique texts and track their usage
for project in projects:
    bugs = get_bugs(project)
    for bug in bugs:
        with open(
            f"dataset/{project}/{bug}/code_chunks.json", "r", encoding="utf-8"
        ) as f:
            chunks = json.load(f)
            texts = [chunk["code"] for chunk in chunks]
            indices = []

            for text in texts:
                if text not in embedding_cache:
                    if text not in text_to_indices:
                        text_to_indices[text] = []
                        texts_to_embed.append(text)
                    text_to_indices[text].append((project, bug))
                else:
                    # Already cached
                    pass

# Second pass: Embed all unique texts in batch
print(f"Embedding {len(texts_to_embed)} unique chunks...")
all_embeddings = embed(texts_to_embed, batch_size=BATCH_SIZE, show_progress_bar=True)

# Populate cache
for i, text in enumerate(texts_to_embed):
    embedding_cache[text] = all_embeddings[i]

# Final pass: write per-bug embedding files
for project in projects:
    bugs = get_bugs(project)
    for bug in bugs:
        with open(
            f"dataset/{project}/{bug}/code_chunks.json", "r", encoding="utf-8"
        ) as f:
            chunks = json.load(f)
            texts = [chunk["code"] for chunk in chunks]
            embeddings = np.array([embedding_cache[text] for text in texts])
            os.makedirs(f"dataset/{project}/{bug}", exist_ok=True)
            np.save(f"dataset/{project}/{bug}/embedding.npy", embeddings)
