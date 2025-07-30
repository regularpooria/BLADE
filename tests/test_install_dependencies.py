from scripts.bugsinpy_utils import *
import subprocess
import os

custom_paths = {"pandas": "requirements-dev.txt"}


def test_install_dependencies():
    projects = get_projects()
    for project in projects:
        bugs = get_bugs(project)

        clone_project(project)
        if project in custom_paths:
            requirements_path = f"tmp/{project}/{custom_paths[project]}"
        else:
            requirements_path = f"tmp/{project}/requirements.txt"

        if os.path.exists(requirements_path):
            env_path = f"tmp/venvs/{project}_venv"

            # Install the requirements using pip inside the env
            subprocess.run(
                [f"{env_path}/bin/pip", "install", "-r", requirements_path],
                stdout=subprocess.DEVNULL,
            )

            print(f"Dependencies installed for project {project} in {env_path}")
            assert True
        else:
            print(f"No requirements.txt found")

    assert True


def test_youtubedl():
    bugs = get_bugs("youtube-dl")
    env = os.environ.copy()
    env["PATH"] = f"tmp/venvs/youtube-dl_venv/bin:" + env["PATH"]

    for bug in bugs:
        info = get_bug_info("youtube-dl", bug)
        checkout_to_commit("youtube-dl", info["buggy_commit_id"])
        file = os.path.abspath(f"BugsInPy/projects/youtube-dl/bugs/{bug}/run_test.sh")

        result = subprocess.run(["bash", file], env=env, cwd="tmp/youtube-dl")

        if result.returncode != 0:
            # Good, the buggy one failed
            # raise RuntimeError(f"❌ Error output from code:\n{stderr}")
            pass
        else:
            # Bad, the buggy one passed
            print(f"BUG ID: {bug}")
            assert False

        checkout_to_commit("youtube-dl", info["fixed_commit_id"])

        result = subprocess.run(["bash", file], env=env, cwd="tmp/youtube-dl")

        if result.returncode != 0:
            # Bad, the fixed one failed
            # raise RuntimeError(f"❌ Error output from code:\n{stderr}")
            assert False
        else:
            # Good, the fixed one passed
            pass
