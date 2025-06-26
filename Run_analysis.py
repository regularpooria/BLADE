#!/usr/bin/env python
# coding: utf-8

# Importing all of the necessary modules

# In[4]:


from scripts.embedding import model, MODEL_NAME, BATCH_SIZE, embed, index_embeddings
from scripts.bugsinpy_utils import *

import faiss
import numpy as np
import json, os


# Making sure the directories exist

# In[2]:


os.makedirs(os.path.abspath(f"tmp/ast/results"), exist_ok=True)
K = 20


# Running each eligible bug through the model and embedding them, after then running cosine similarity to determine which files they think it should be changed

# In[ ]:


projects = get_projects()
for project in projects:
    bugs = get_bugs(project)
    code_chunks_path = f"tmp/ast/chunks/code_chunks_{project}.json"
    embedding_index_path = f"tmp/ast/embeddings/index_{project}.faiss"
    bug_result_path = os.path.abspath(f"tmp/ast/results/bug_results_{project}.json")

    with open(code_chunks_path, "r") as f:
        code_chunks = json.load(f)

    index = faiss.read_index(embedding_index_path)

    filtered_bugs = []
    error_texts = []

    # First pass: filter bugs and collect error traces
    for bug in bugs:
        changed_files = parse_changed_files(project, bug)
        if len(changed_files) > 1:
            continue
        info = get_bug_info(project, bug)
        error = extract_python_tracebacks(project, bug)
        if error:
            filtered_bugs.append(bug)
            error_texts.append(error)

    # Batch encode
    if error_texts:
        error_embeddings = embed(error_texts, batch_size=BATCH_SIZE, show_progress_bar=True)

        output = []
        for bug, emb in zip(filtered_bugs, error_embeddings):
            D, I = index.search(np.array([emb]).astype("float32"), k=K)
            search_results = {"index": bug, "files": []}
            for idx in I[0]:
                result = code_chunks[idx]
                search_results["files"].append(
                    {"file": result["file"], "function": result["name"]}
                )
            output.append(search_results)

        with open(bug_result_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)


# Using that predictions to calculate success rate and show where each search was successful or not.

# In[9]:





# In[6]:


results_folder = os.path.abspath("tmp/ast/results")
results_files = os.listdir(results_folder)
def analyze(k):
    results = {
        "K": k,
        "model_name": MODEL_NAME,
        "searches_failed": [],  # [{project_name, bug_id, detected_files: list, actual_file}]
        "searches_passed": [],  # [{project_name, bug_id, detected_files: list, actual_files}]
        "success_rate": 0,  # out of 100 (including bugs skipped)
        "success_projects": {},  # {project_name, success_rate, success_rate_no_skip}
    }
    success_projects_tmp = {}
    count = 0
    maximum_bugs = 0
    for project in results_files:
        project_name = project.replace("bug_results_", "").replace(".json", "")
        bugs = get_bugs(project_name)
        maximum_bugs += len(bugs)
        success_projects_tmp[project_name] = {
            "failed": 0,
            "passed": 0,
            "total": 0,
        }

        with open(f"{results_folder}/{project}", "r", encoding="utf-8") as result_file:
            data = json.loads(result_file.read())
            for search_result in data:
                changed_file = parse_changed_files(project_name, search_result["index"])[0].split("/")[-1]
                files_predicted = [
                    obj["file"].split("/")[-1] for obj in search_result["files"][:k]
                ]
                if changed_file in files_predicted:
                    results["searches_passed"].append(
                        {
                            "project_name": project_name,
                            "bug_id": search_result["index"],
                            "detected_files": files_predicted,
                            "actual_file": changed_file,
                        }
                    )
                    success_projects_tmp[project_name]["passed"] += 1
                    success_projects_tmp[project_name]["total"] += 1
                else:
                    results["searches_failed"].append(
                        {
                            "project_name": project_name,
                            "bug_id": search_result["index"],
                            "detected_files": files_predicted,
                            "actual_file": changed_file,
                        }
                    )
                    success_projects_tmp[project_name]["failed"] += 1
                    success_projects_tmp[project_name]["total"] += 1
                    


        searches_counted = (
            success_projects_tmp[project_name]["passed"]
            + success_projects_tmp[project_name]["failed"]
        )

        results["success_projects"][project_name] = {
            "success_rate": success_projects_tmp[project_name]["passed"] / searches_counted,
        } | success_projects_tmp[project_name]

    results["success_rate"] = len(results["searches_passed"]) / (len(results["searches_failed"]) + len(results["searches_passed"]))
    with open(os.path.abspath(f"results_{k}.json"), "w", encoding="utf-8") as file:
        file.write(json.dumps(results, indent=2))
        
analyze(5)
analyze(10)
analyze(15)
analyze(20)

