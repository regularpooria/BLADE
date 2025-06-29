from scripts.beetlebox_utils import load_project, get_projects, DATASET_PATH

from scripts.embedding import BATCH_SIZE, embed
import numpy as np
import os, json

projects = os.listdir("beetlebox_dataset")

for project in projects:
    if not os.path.isdir(f"beetlebox_dataset/{project}"):
        continue

    bugs = os.listdir(f"beetlebox_dataset/{project}")

    with open(
        f"beetlebox_dataset/{project}/duplicated_chunks.json", encoding="utf-8"
    ) as f:
        chunks = json.loads(f.read())
        chunks = [chunk["chunk"] for chunk in chunks]

    embeddings = embed(chunks, BATCH_SIZE)
    np.save(f"beetlebox_dataset/{project}/duplicated_embeddings.npy", embeddings)

    for bug in bugs:
        if not os.path.isdir(f"beetlebox_dataset/{project}/{bug}"):
            continue

        with open(
            f"beetlebox_dataset/{project}/{bug}/unique_chunks.json", encoding="utf-8"
        ) as f:
            chunks = json.loads(f.read())
            chunks = [chunk["chunk"] for chunk in chunks]

        embeddings = embed(chunks, BATCH_SIZE)
        np.save(f"beetlebox_dataset/{project}/{bug}/unique_embeddings.npy", embeddings)
