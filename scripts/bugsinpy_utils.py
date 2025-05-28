FOLDER_NAME = "BugsInPy"

import os
import subprocess
from scripts.run_snippet import run_command_in_folder, run_command_in_venv, make_venv


def parse_string(string: str):
    output = {}
    string = string.strip()
    strings = string.split("\n")
    for string in strings:
        data = string.strip().split("=")
        output[data[0].strip()] = data[1].replace('"', "")

    return output


def get_projects():
    return os.listdir(f"{FOLDER_NAME}/projects")


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

    make_venv(project)


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
