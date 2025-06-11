from scripts.bugsinpy_utils import (
    get_projects,
    clone_project,
    checkout_to_commit,
    get_bug_info,
)
import ast
import pathspec
import os
import json
import pathspec


def load_gitignore():
    gitignore_path = os.path.abspath(".gitignore_embedding")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            return pathspec.PathSpec.from_lines("gitwildmatch", f)
    return None


def extract_chunks(repo_path):
    all_chunks = []
    spec = load_gitignore()

    for root, _, files in os.walk(repo_path):
        rel_root = os.path.relpath(root, repo_path)
        if spec and spec.match_file(rel_root):
            continue

        for fname in files:
            rel_path = os.path.normpath(os.path.join(rel_root, fname))
            if spec and spec.match_file(rel_path):
                continue

            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        source = f.read()
                        tree = ast.parse(source)
                        root_code = ""
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                                snippet = ast.get_source_segment(source, node)
                                all_chunks.append(
                                    {"file": fpath, "name": node.name, "code": snippet}
                                )
                            else:
                                snippet = ast.get_source_segment(source, node)
                                root_code += snippet + "\n"

                        if root_code != "":
                            all_chunks.append(
                                {"file": fpath, "name": "root", "code": root_code}
                            )

                except Exception:
                    continue

    return all_chunks


projects = get_projects()
for project in projects:
    clone_project(project)
    info = get_bug_info(project, 1)
    checkout_to_commit(project, info["buggy_commit_id"])


dirs = os.listdir("tmp")
os.makedirs("tmp/ast/chunks", exist_ok=True)
os.makedirs("tmp/ast/embeddings", exist_ok=True)


for directory in dirs:
    if directory == "ast":
        continue

    chunks = extract_chunks(f"tmp/{directory}")
    with open(
        f"tmp/ast/chunks/code_chunks_{directory}.json", "w", encoding="utf-8"
    ) as f:
        json.dump(chunks, f, indent=2)
