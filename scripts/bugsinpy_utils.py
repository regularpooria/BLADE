FOLDER_NAME = "BugsInPy"

import os
import subprocess
from scripts.run_snippet import run_command_in_folder, run_command_in_venv, make_venv
import re


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
        changed_files = []

        for line in diff_text.splitlines():
            if line.startswith("diff --git"):
                # Extract file name from b/ path
                match = re.match(r"diff --git a/.* b/(.*)", line)
                if match:
                    changed_files.append(match.group(1))

        return changed_files


def get_projects():
    return [
        x
        for x in os.listdir(f"{FOLDER_NAME}/projects")
        if x not in ["bugsinpy-index.csv"]
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
        subprocess.run(["git", "-C", "tmp", "clone", github_url])

    # make_venv(project)


def get_bug_info(project: str, bug_id: int):
    with open(f"{FOLDER_NAME}/projects/{project}/bugs/{bug_id}/bug.info") as info_file:
        return parse_string(info_file.read())


def checkout_to_commit(project, commit):
    if not os.path.isdir(f"tmp/{project}"):
        clone_project(project)

    subprocess.run(["git", "checkout", commit], cwd=f"tmp/{project}")


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


def extract_python_tracebacks(project, bug_id):
    file = os.path.abspath(
        f"{FOLDER_NAME}/projects/{project}/bugs/{bug_id}/bug_buggy.txt"
    )
    error_patterns = [
        re.compile(r"Traceback \(most recent call last\):"),
        re.compile(r"^E\s+[\w.]+(?:Error|Exception|Warning):"),  # pytest summary
        re.compile(r"^[\w.]+(?:Error|Exception|Warning):.*"),  # standard one-liner
    ]
    pytest_arrow = re.compile(r"^\s*>")  # line where test fails (starts with >)
    file_lineno = re.compile(r"^[^\s].+:\d+:")  # lines like file.py:123:

    with open(file, "r") as bug_trace_file:
        unfiltered_trace = bug_trace_file.readlines()
        errors = []
        used = set()
        context = 2
        idx = 0

        while idx < len(unfiltered_trace):
            line = unfiltered_trace[idx].strip()

            for pat in error_patterns:
                if pat.match(line):
                    if "Traceback" in line:
                        start = max(0, idx - context)
                        block = [unfiltered_trace[start] if start != idx else line]
                        idx += 1
                        while idx < len(unfiltered_trace):
                            block.append(unfiltered_trace[idx])
                            if any(
                                p.match(unfiltered_trace[idx].strip())
                                for p in error_patterns[1:]
                            ):
                                idx += 1
                                break
                            if unfiltered_trace[idx].strip() == "":
                                idx += 1
                                break
                            idx += 1
                        block_text = "".join(block).strip()
                    else:
                        start = max(0, idx - context)
                        end = min(len(unfiltered_trace), idx + context + 1)
                        block_text = "".join(unfiltered_trace[start:end]).strip()
                        idx += 1
                    if block_text not in used:
                        errors.append(block_text)
                        used.add(block_text)
                    break

            else:
                # NEW: support pytest-style errors starting with >
                if pytest_arrow.match(line):
                    start = max(0, idx - context)
                    block = unfiltered_trace[start:idx]
                    while idx < len(unfiltered_trace):
                        block.append(unfiltered_trace[idx])
                        if any(
                            p.match(unfiltered_trace[idx].strip())
                            for p in error_patterns[1:]
                        ):
                            idx += 1
                            break
                        idx += 1
                    block_text = "".join(block).strip()
                    if block_text not in used:
                        errors.append(block_text)
                        used.add(block_text)
                else:
                    idx += 1

        return errors


def get_raw_traceback(project, bug_id):
    file = os.path.abspath(
        f"{FOLDER_NAME}/projects/{project}/bugs/{bug_id}/bug_buggy.txt"
    )

    with open(
        f"{FOLDER_NAME}/projects/{project}/bugs/{bug_id}/bug_buggy.txt", "r"
    ) as file:
        return file.read()
