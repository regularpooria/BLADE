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


def test_all_errors():
    projects = get_projects()
    os.makedirs(os.path.abspath(f"tmp/ast/results"), exist_ok=True)

    for project in projects:
        bugs = get_bugs(project)
        code_chunks = json.loads(
            open(f"tmp/ast/chunks/code_chunks_{project}.json", "r").read()
        )
        embedding = np.load(f"tmp/ast/embeddings/embedding_{project}.npy")
        index = faiss.read_index(f"tmp/ast/embeddings/index_{project}.faiss")
        bug_result_path = os.path.abspath(f"tmp/ast/results/bug_results_{project}.txt")
        with open(bug_result_path, "w", encoding="utf-8") as f:
            for bug in bugs:
                errors = [
                    bug if len(bug) > 0 else get_raw_traceback(project, bug)
                    for bug in extract_python_tracebacks(project, bug)
                ]
                if len(errors) == 0:
                    continue
                embedding = model.encode(errors, prompt=bug_prompt)

                D, I = index.search(np.array(embedding).astype("float32"), k=3)
                for idx, error in enumerate(errors):
                    f.write(f"Results for bug: {project}/{bug}/{idx}\n")
                    for i in I[idx]:
                        result = code_chunks[i]
                        f.write(f"File: {result['file']}\n")
                        f.write(f"Function: {result['name']}\n")
                        f.write(
                            result["code"][:300] + "...\n\n"
                        )  # Preview first 300 characters
                    f.write("=" * 60 + "\n\n")  # Separator

    assert True
