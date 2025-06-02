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
        re.compile(r"^E\s+[\w.]+Error:"),  # pytest single-line error
        re.compile(r"^E\s+[\w.]+Exception:"),  # pytest single-line exception
        re.compile(r"^[\w.]+Error:.*"),  # standard single-line error
        re.compile(r"^[\w.]+Exception:.*"),  # standard single-line exception
    ]
    with open(file, "r") as bug_trace_file:
        unfiltered_trace = bug_trace_file.readlines()
        errors = []
        used = set()
        context = 2
        idx = 0
        while idx < len(unfiltered_trace):
            line = unfiltered_trace[idx]
            for pat in error_patterns:
                if pat.match(line):
                    # If this is a full traceback, grab lines until the exception line
                    if "Traceback" in line:
                        start = max(0, idx - context)
                        block = [unfiltered_trace[start] if start != idx else line]
                        idx += 1
                        while idx < len(unfiltered_trace):
                            block.append(unfiltered_trace[idx])
                            # Stop after the first exception line
                            if (
                                error_patterns[1].match(unfiltered_trace[idx])
                                or error_patterns[2].match(unfiltered_trace[idx])
                                or error_patterns[3].match(unfiltered_trace[idx])
                                or error_patterns[4].match(unfiltered_trace[idx])
                            ):
                                idx += 1
                                break
                            # Optionally, stop at an empty line (for even cleaner output)
                            if unfiltered_trace[idx].strip() == "":
                                idx += 1
                                break
                            idx += 1
                        block_text = "".join(block).strip()
                    else:
                        # For single-line errors, grab a bit of context
                        start = max(0, idx - context)
                        end = min(len(unfiltered_trace), idx + context + 1)
                        block_text = "".join(unfiltered_trace[start:end]).strip()
                        idx += 1
                    if block_text not in used:
                        errors.append(block_text)
                        used.add(block_text)
                    break
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
