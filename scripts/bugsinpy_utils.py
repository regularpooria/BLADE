FOLDER_NAME = "BugsInPy"

import os
import subprocess
from scripts.run_snippet import run_command_in_folder, run_command_in_venv, make_venv
import re, json


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
