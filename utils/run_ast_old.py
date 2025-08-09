import time
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
import token, tokenize
from io import StringIO
from tqdm import tqdm
from multiprocessing import Pool
import hashlib
import asttokens


def load_gitignore():
    start_time = time.time()
    gitignore_path = os.path.abspath(".gitignore_embedding")
    spec = None
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            spec = pathspec.PathSpec.from_lines("gitwildmatch", f)
    end_time = time.time()
    # print(f"Time taken by load_gitignore: {end_time - start_time:.4f} seconds")
    return spec


def remove_functions_and_classes(source, tree):
    """
    This function takes in source code, parses it with AST, and removes all
    function and class definitions, returning only the root-level code.
    """
    start_time = time.time()
    lines = source.splitlines()  # Split source into lines for easier manipulation

    # Collect line numbers for function and class definitions
    lines_to_remove = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            start_line = node.lineno - 1
            end_line = node.body[-1].lineno if node.body else start_line
            end_line = max(end_line, start_line)
            for i in range(start_line, end_line):
                lines_to_remove.add(i)
            lines_to_remove.add(node.lineno - 1)

    root_code = "\n".join(
        line for i, line in enumerate(lines) if i not in lines_to_remove
    )
    end_time = time.time()
    # print(
    #     f"Time taken by remove_functions_and_classes: {end_time - start_time:.4f} seconds"
    # )

    return root_code


def remove_comments_and_docstrings(source: str) -> str:
    """
    Strip comments and docstrings from a given source code string.
    """
    start_time = time.time()
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

    result = "".join(output)
    end_time = time.time()
    # print(
    #     f"Time taken by remove_comments_and_docstrings: {end_time - start_time:.4f} seconds"
    # )
    return result


def process_file(fpath):
    start_time = time.time()
    all_chunks = []
    try:
        with open(fpath, "r", encoding="utf-8") as f:
            source = f.read()

        atok = asttokens.ASTTokens(source, parse=True)
        tree = atok.tree
        root_code = remove_functions_and_classes(source, tree)
        if root_code:
            all_chunks.append({"file": fpath, "name": "root", "code": root_code})

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                snippet = atok.get_text(node)
                all_chunks.append({"file": fpath, "name": node.name, "code": snippet})

    except Exception as e:
        print(f"⚠️ Error processing {fpath}: {e}")

    end_time = time.time()
    return all_chunks


def get_python_files(repo_path):
    spec = load_gitignore()
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
    return python_files


def hash_file(path):
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None


def extract_chunks(python_files):
    start_time = time.time()
    all_chunks = []
    with Pool() as pool:
        results = list(
            tqdm(
                pool.imap(process_file, python_files),
                total=len(python_files),
                desc="Processing files",
                unit="file",
            )
        )
    for result in results:
        all_chunks.extend(result)

    end_time = time.time()
    # print(
    #     f"Time taken by extract_chunks for {repo_path}: {end_time - start_time:.4f} seconds"
    # )
    return all_chunks
