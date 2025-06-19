from scripts.embedding import search_bug, model, bug_prompt
from scripts.bugsinpy_utils import *

import faiss
import numpy as np
import json, os


# def test_search_bug():
#     query_bug = {
#         "symptom": "Operations on NoneType",
#         "stack_trace": "TypeError: 'NoneType' object is not subscriptable",
#         "buggy_code": "a = lista[1] - lista[0]",
#     }
#     search_bug(query_bug)


# def test_actual_error():
#     clone_project("fastapi")
#     info = get_bug_info("fastapi", 2)
#     checkout_to_commit("fastapi", info["buggy_commit_id"])
#     install_dependencies("fastapi", 2)
#     run_setup("fastapi", 2)

#     code_chunks = json.loads(
#         open("tmp/ast/chunks/code_chunks_fastapi.json", "r").read()
#     )
#     embedding = np.load("tmp/ast/embeddings/embedding_fastapi.npy")
#     index = faiss.read_index("tmp/ast/embeddings/index_fastapi.faiss")

#     try:
#         run_test("fastapi", 2)
#         assert False
#     except Exception as e:
#         # Throws an error, which is to be expected since we're loading the buggy commit
#         embedding = model.encode([str(e)])

#         D, I = index.search(np.array(embedding).astype("float32"), k=3)
#         for i in I[0]:
#             result = code_chunks[i]
#             print("File:", result["file"])
#             print("Function:", result["name"])
#             print(result["code"][:300], "...\n")  # Preview first 300 characters

#         assert True


# def test_actual_error():
#     available_projects = ["fastapi", "httpie", "youtube-dl"]

#     code_chunks = json.loads(
#         open("tmp/ast/chunks/code_chunks_fastapi.json", "r").read()
#     )
#     embedding = np.load("tmp/ast/embeddings/embedding_fastapi.npy")
#     index = faiss.read_index("tmp/ast/embeddings/index_fastapi.faiss")

#     try:
#         run_test("fastapi", 2)
#         assert False
#     except Exception as e:
#         # Throws an error, which is to be expected since we're loading the buggy commit
#         embedding = model.encode([str(e)])

#         D, I = index.search(np.array(embedding).astype("float32"), k=3)
#         for i in I[0]:
#             result = code_chunks[i]
#             print("File:", result["file"])
#             print("Function:", result["name"])
#             print(result["code"][:300], "...\n")  # Preview first 300 characters

#         assert True


def test_error_extraction():
    print("\nEND\n".join(extract_python_tracebacks("youtube-dl", 1)))

    assert True
