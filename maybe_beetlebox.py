from scripts.beetlebox_utils import load_project, get_projects, DATASET_PATH

from scripts.embedding import BATCH_SIZE, embed
import numpy as np
import sys
import os, json

projects = get_projects()
embedding_cache = {}
texts_to_embed = []
text_to_indices = {}

# First pass: collect all unique texts and track their usage
for project in projects:
    data = load_project(project)
    issues = data["issues"]
    for issue in issues:
        chunks = data[issue["issue_id"]]
        texts = [chunk["file_chunk"] for chunk in chunks]
        indices = []

        for text in texts:
            if text not in embedding_cache:
                if text not in text_to_indices:
                    text_to_indices[text] = []
                    texts_to_embed.append(text)
                text_to_indices[text].append((project, issue["issue_id"]))
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
    data = load_project(project)
    issues = data["issues"]
    for issue in issues:
        chunks = data[issue["issue_id"]]
        texts = [chunk["file_chunk"] for chunk in chunks]
        embeddings = np.array([embedding_cache[text] for text in texts])
        os.makedirs(
            f"{DATASET_PATH}/embeddings/{project}/{issue['issue_id']}", exist_ok=True
        )
        np.save(
            f"{DATASET_PATH}/embeddings/{project}/{issue['issue_id']}/embedding.npy",
            embeddings,
        )
