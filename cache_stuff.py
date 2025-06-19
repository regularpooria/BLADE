from scripts.bugsinpy_utils import (
    get_projects,
    clone_project,
    get_bug_info,
    checkout_to_commit,
)

projects = get_projects()
for project in projects:
    clone_project(project)
    info = get_bug_info(project, 1)
    checkout_to_commit(project, info["buggy_commit_id"])

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("mchochlov/codebert-base-cd-ft")

model.save("instructor_base_local")
