FOLDER_NAME = "BugsInPy"

import os
import subprocess
from scripts.run_snippet import run_command_in_folder, run_command_in_venv, make_venv
import re, json
import ast
import builtins

builtin_names = set(dir(builtins))


def parse_string(string: str):
    output = {}
    string = string.strip()
    strings = string.split("\n")
    for string in strings:
        data = string.strip().split("=")
        output[data[0].strip()] = data[1].replace('"', "")

    return output


def parse_changed_files(project, bug_id):
    with open(
        f"{FOLDER_NAME}/projects/{project}/bugs/{bug_id}/bug_patch.txt"
    ) as diff_file:
        diff_text = diff_file.read()
        try:
            changed_files = json.loads(diff_text)
        except:
            changed_files = []

            for line in diff_text.splitlines():
                if line.startswith("diff --git"):
                    # Extract file name from b/ path
                    match = re.match(r"diff --git a/.* b/(.*)", line)
                    if match:
                        changed_files.append(match.group(1))

        return changed_files


def parse_changed_function_names(project, bug_id):
    with open(
        f"{FOLDER_NAME}/projects/{project}/bugs/{bug_id}/bug_patch.txt"
    ) as diff_file:
        diff_text = diff_file.read()
        function_names = re.findall(
            r"^@@.*\b(?:def|class)\s+(\w+)\s*\(", diff_text, flags=re.MULTILINE
        )
        return list(set(function_names))


def parse_imports(source_code):
    tree = ast.parse(source_code)
    imports = {}

    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            module = node.module  # e.g. youtube_dl.utils
            for alias in node.names:
                imports[alias.asname or alias.name] = f"{module}.{alias.name}"
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports[alias.asname or alias.name] = alias.name
    return imports


def resolve_module_to_path(module_name, project_root):
    parts = module_name.split(".")
    if len(parts) > 1:
        parts = parts[:-1]
    rel_path = os.path.join(*parts) + ".py"
    abs_path = os.path.join(project_root, rel_path)
    abs_path = os.path.normpath(abs_path)
    if os.path.isfile(abs_path):
        return rel_path
    init_rel_path = os.path.join(*parts, "__init__.py")
    abs_init_path = os.path.join(project_root, init_rel_path)
    abs_init_path = os.path.normpath(abs_init_path)
    if os.path.isfile(abs_init_path):
        return init_rel_path
    return None


def extract_called_functions(source_code):
    """Parses the code and extracts names of called functions, excluding built-ins."""
    tree = ast.parse(source_code)
    called_funcs = set()

    class FuncCallVisitor(ast.NodeVisitor):
        def visit_Call(self, node):
            # Case: foo()
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            # Case: self.foo(), obj.foo(), module.foo()
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            else:
                func_name = None

            if func_name and func_name not in builtin_names:
                called_funcs.add(func_name)

            self.generic_visit(node)

    FuncCallVisitor().visit(tree)
    return called_funcs


def get_defined_functions(source_code):
    """Return a set of all function names defined in this file (top-level + methods)."""
    tree = ast.parse(source_code)
    names = set()

    class DefVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            names.add(node.name)

        def visit_ClassDef(self, node):
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    names.add(item.name)
            self.generic_visit(node)

    DefVisitor().visit(tree)
    return names


def extract_function_source(source_code, function_name):
    """Extracts the full source of a function or method with a given name."""
    tree = ast.parse(source_code)

    class FunctionFinder(ast.NodeVisitor):
        def __init__(self):
            self.source = None

        def visit_FunctionDef(self, node):
            if self.source is None and node.name == function_name:
                self.source = ast.get_source_segment(source_code, node)

        def visit_ClassDef(self, node):
            self.generic_visit(node)

    finder = FunctionFinder()
    finder.visit(tree)
    return finder.source


def grab_chunks(project, bug_id):
    with open(
        f"dataset/{project}/{bug_id}/code_chunks.json", "r", encoding="utf-8"
    ) as f:
        return json.loads(f.read())


def grab_chunk(project, bug_id, function_name):
    chunks = grab_chunks(project, bug_id)
    for chunk in chunks:
        if chunk["name"] == function_name:
            return chunk

    return None


def get_projects():
    return [
        "matplotlib",
        "pandas",
        "youtube-dl",
        "luigi",
        "black",
        "scrapy",
        "thefuck",
        "keras",
        "ansible",
    ]


def get_project_github(project):
    with open(f"{FOLDER_NAME}/projects/{project}/project.info") as info_file:
        return parse_string(info_file.read())["github_url"]


def get_bugs(project):
    return os.listdir(f"{FOLDER_NAME}/projects/{project}/bugs")


def clone_project(project):
    github_url = get_project_github(project)
    if not os.path.isdir("tmp"):
        os.mkdir("tmp")

    if not os.path.isdir("tmp/" + project):
        subprocess.run(["git", "-C", "tmp", "clone", "--depth=1", github_url])

    # make_venv(project)


def get_bug_info(project: str, bug_id: int):
    with open(f"{FOLDER_NAME}/projects/{project}/bugs/{bug_id}/bug.info") as info_file:
        return parse_string(info_file.read())


def checkout_to_commit(project, commit, silent=False):
    if not os.path.isdir(f"tmp/{project}"):
        clone_project(project)

    if silent:
        subprocess.run(
            ["git", "checkout", commit],
            cwd=f"tmp/{project}",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        subprocess.run(["git", "checkout", commit], cwd=f"tmp/{project}")


def extract_function_name_from_traceback(traceback: str):
    pattern = r"(?:ERROR|FAIL): (\w+)"
    return re.findall(pattern, traceback)


def test_to_source_code(project, file_path, function_name, seen=None, max_depth=None, _depth=0, sources=None):
    if "tmp" not in project:
        project_root = f"tmp/{project}"
    else:
        project_root = project
    if seen is None:
        seen = set()
    if sources is None:
        sources = {}
    key = (file_path, function_name)
    if key in seen:
        return {}, sources
    seen.add(key)
    with open(os.path.join(project_root, file_path), "r", encoding="utf-8") as f:
        source_code = f.read()
    defined_funcs = get_defined_functions(source_code)
    imports = parse_imports(source_code)
    function_src = extract_function_source(source_code, function_name)
    if not function_src:
        return {function_name: "Function not found"}, sources
    # Save the source code snippet for this function
    sources[key] = function_src
    called_funcs = extract_called_functions(function_src)
    tree = {function_name: {}}
    for func in called_funcs:
        if func in defined_funcs:
            subtree, sources = test_to_source_code(
                project_root, file_path, func, seen, max_depth, _depth, sources
            )
            tree[function_name][func] = subtree
        elif func in imports:
            if max_depth is not None and _depth >= max_depth:
                tree[function_name][func] = "Max depth reached"
                continue
            module_rel_path = resolve_module_to_path(imports[func], project_root)
            if module_rel_path:
                subtree, sources = test_to_source_code(
                    project_root, module_rel_path, func, seen, max_depth, _depth + 1, sources
                )
                tree[function_name][func] = subtree
            else:
                tree[function_name][func] = "Module file not found"
        else:
            tree[function_name][func] = "External or builtin function"
    return tree, sources


def run_setup(project, bug_id):
    file = os.path.abspath(f"{FOLDER_NAME}/projects/{project}/bugs/{bug_id}/setup.sh")

    if os.path.isfile(file):
        run_command_in_venv(
            project,
            ["bash", file],
        )


def install_dependencies(project, bug_id):
    file = os.path.abspath(
        f"{FOLDER_NAME}/projects/{project}/bugs/{bug_id}/requirements.txt"
    )
    if os.path.isfile(file):
        run_command_in_venv(
            project,
            ["pip", "install", "--disable-pip-version-check", "-r", file],
        )


def run_test(project, bug_id):
    file = os.path.abspath(
        f"{FOLDER_NAME}/projects/{project}/bugs/{bug_id}/run_test.sh"
    )
    run_command_in_venv(
        project,
        ["bash", file],
    )


def remove_decorations(trace):
    return "\n".join(
        line
        for line in trace.splitlines()
        if not re.fullmatch(r"[-_=~\s]{5,}", line.strip())
        and not re.fullmatch(r"[-_=~\s]{5,}.*?[-_=~\s]{5,}", line.strip())
    )


def extract_python_tracebacks(project, bug_id):
    file = os.path.abspath(
        f"{FOLDER_NAME}/projects/{project}/bugs/{bug_id}/bug_buggy.txt"
    )

    pattern_pytest = (
        r"=+ (?:FAILURES|ERRORS) =+\n"
        r"(?P<trace>.*?)"
        r"(?=\n[-=]{10,} (Captured|warnings summary|short test summary info|ERRORS|FAILURES|slowest)[^\n]* [-=]{10,}|\Z)"
    )
    pattern_unittest = (
        r"^(FAIL|ERROR): .+?\n"  # Match FAIL or ERROR line
        r"-+\n"  # Separator line
        r"(?:[\s\S]*?)"  # Non-greedy match for traceback
        r"(?=^-{10,}|\Z)"  # Until next dashed line or end
    )

    with open(file, "r") as bug_trace_file:
        unfiltered_trace = bug_trace_file.read()

        matches = list(re.finditer(pattern_pytest, unfiltered_trace, re.DOTALL))
        if matches:
            text = remove_decorations(
                "\n".join(m.group("trace").strip() for m in matches)
            )

            return text

        match = re.search(pattern_unittest, unfiltered_trace, re.MULTILINE | re.DOTALL)
        if match:
            return f"FAIL: {match.group(0).strip()}"

        return None


def get_raw_traceback(project, bug_id):
    file = os.path.abspath(
        f"{FOLDER_NAME}/projects/{project}/bugs/{bug_id}/bug_buggy.txt"
    )

    with open(
        f"{FOLDER_NAME}/projects/{project}/bugs/{bug_id}/bug_buggy.txt", "r"
    ) as file:
        return file.read()
