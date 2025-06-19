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
from tqdm import tqdm
from multiprocessing import Pool


def load_gitignore():
    gitignore_path = os.path.abspath(".gitignore_embedding")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            return pathspec.PathSpec.from_lines("gitwildmatch", f)
    return None


def remove_functions_and_classes(source):
    """
    This function takes in source code, parses it with AST, and removes all
    function and class definitions, returning only the root-level code.
    """
    tree = ast.parse(source)
    lines = source.splitlines()  # Split source into lines for easier manipulation

    # Collect line numbers for function and class definitions
    lines_to_remove = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            start_line = node.lineno - 1  # Convert to 0-based index
            end_line = start_line + len(
                node.body
            )  # End line of the function/class body

            # Mark the function or class lines for removal
            for i in range(start_line, end_line):
                lines_to_remove.add(i)

    # Keep only lines that are not part of any function or class
    root_code = "\n".join(
        line for i, line in enumerate(lines) if i not in lines_to_remove
    )
    return root_code


import token, tokenize
from io import StringIO


def remove_comments_and_docstrings(source: str) -> str:
    """
    Strip comments and docstrings from a given source code string.
    """
    source_io = StringIO(source)
    output = []

    prev_toktype = token.INDENT
    last_lineno = -1
    last_col = 0

    tokgen = tokenize.generate_tokens(source_io.readline)
    for toktype, ttext, (slineno, scol), (elineno, ecol), ltext in tokgen:
        if slineno > last_lineno:
            last_col = 0
        if scol > last_col:
            output.append(" " * (scol - last_col))
        if toktype == token.STRING and prev_toktype == token.INDENT:
            # Docstring
            output.append("#--")
        elif toktype == tokenize.COMMENT:
            # Comment
            output.append("##\n")
        else:
            output.append(ttext)
        prev_toktype = toktype
        last_col = ecol
        last_lineno = elineno

    return "".join(output)


def process_file(fpath):
    all_chunks = []
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            source = f.read()

            # Get root-level code by removing functions and classes
            root_code = remove_functions_and_classes(source)

            # Add the root-level code to the chunks
            if root_code:
                all_chunks.append({"file": fpath, "name": "root", "code": root_code})

            # Also add function and class code if needed (optional)
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    snippet = ast.get_source_segment(source, node)
                    all_chunks.append(
                        {"file": fpath, "name": node.name, "code": snippet}
                    )

    except Exception as e:
        pass  # Handle error silently and move on to the next file

    return all_chunks


def extract_chunks(repo_path):
    all_chunks = []
    spec = load_gitignore()

    # Gather all Python files first
    python_files = []
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
                python_files.append(fpath)

    # Use tqdm for a single progress bar over all Python files
    with Pool() as pool:
        results = list(
            tqdm(
                pool.imap(process_file, python_files),
                total=len(python_files),
                desc="Processing files",
                unit="file",
            )
        )

    # Combine results from all processes
    for result in results:
        all_chunks.extend(result)

    return all_chunks


if __name__ == "__main__":
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
