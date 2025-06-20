from scripts.embedding import (
    model,
    index_embeddings,
    code_prompt,
    BATCH_SIZE,
    embed,
    compute_masked_embedding,
)
import numpy
import faiss
import os
import json


files = os.listdir("tmp/ast/chunks")

for ast_file in files:

    with open(f"tmp/ast/chunks/{ast_file}", "r", encoding="utf-8") as f:
        print(f"tmp/ast/chunks/{ast_file}")
        chunks = json.loads(f.read())

        # Embedding each text
        texts = [chunk["code"] for chunk in chunks]
        if BATCH_SIZE:
            embeddings = embed(texts, batch_size=BATCH_SIZE, show_progress_bar=True)
        else:
            embeddings = embed(texts, show_progress_bar=True)

        os.makedirs("tmp/ast/embeddings/", exist_ok=True)
        project_name = ast_file.replace("code_chunks_", "").replace(".json", "")
        numpy.save(f"tmp/ast/embeddings/embedding_{project_name}.npy", embeddings)
        index = index_embeddings(embeddings)
        faiss.write_index(index, f"tmp/ast/embeddings/index_{project_name}.faiss")
