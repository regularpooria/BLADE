from scripts.bugsinpy_utils import *
from scripts.embedding import BATCH_SIZE, model
from run_ast import extract_chunks
import numpy
import os, json

projects = get_projects()
for project in projects:
    bugs = get_bugs(project)
    for bug in bugs:
        with open(
            f"dataset/{project}/{bug}/code_chunks.json", "r", encoding="utf-8"
        ) as f:
            chunks = json.loads(f.read())
            # Embedding each text
            texts = [chunk["code"] for chunk in chunks]
            if BATCH_SIZE:
                embeddings = model.encode(
                    texts, batch_size=BATCH_SIZE, show_progress_bar=True
                )
            else:
                embeddings = model.encode(texts, show_progress_bar=True)

            numpy.save(f"dataset/{project}/{bug}/embedding.npy", embeddings)
