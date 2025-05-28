# import subprocess, logging

# def run_code(code):
#     with open("/tmp/temp_code.py", "w") as f:
#         f.write(code)
#     result = subprocess.run([
#         "docker", "run", "--rm", "-v", "/tmp:/sandbox", "bootcamp-env",
#         "python", "/sandbox/temp_code.py"
#     ], capture_output=True, timeout=10)
#     logging.info("Output:%s", result.stdout.decode())
#     logging.error("Errors:%s", result.stderr.decode())
import os
import subprocess
import tempfile

IMAGE_PATH = "images/python.sif"


def run_code(code):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as f:
        f.write(code)
        host_path = f.name
    container_path = "/tmp/temp_code.py"

    try:
        result = subprocess.run(
            [
                "apptainer",
                "exec",
                "--bind",
                f"{host_path}:{container_path}",
                IMAGE_PATH,
                "python3",
                container_path,
            ],
            capture_output=True,
            text=True,
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode != 0:
            raise RuntimeError(f"❌ Error output from code:\n{stderr}")

        return stdout
    finally:
        os.remove(host_path)


def make_venv(project):
    project_path = os.path.abspath(f"tmp/{project}")
    if os.path.isdir(os.path.join(project_path, "venv")):
        return

    subprocess.run(
        [
            "apptainer",
            "exec",
            "--home",
            project_path,
            "--pwd",
            project_path,
            IMAGE_PATH,
            "python3",
            "-m",
            "venv",
            "--system-site-packages",
            "venv",
        ],
        check=True,
    )


def run_command_in_folder(project: str, commands: list):
    project_path = os.path.abspath(f"tmp/{project}")
    result = subprocess.run(
        [
            "apptainer",
            "exec",
            "--env",
            f"PYTHONUSERBASE={project_path}",
            "--home",
            project_path,
            "--pwd",
            project_path,
            IMAGE_PATH,
        ]
        + commands,
        capture_output=True,
        text=True,
    )

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    if result.returncode != 0:
        raise RuntimeError(f"❌ Error output from code:\n{stderr}")

    return stdout


def run_command_in_venv(project: str, commands: list):
    project_path = os.path.abspath(f"tmp/{project}")
    result = subprocess.run(
        f"""apptainer exec --home {project_path} --pwd {project_path} {IMAGE_PATH} \
    bash -c 'source venv/bin/activate && {" ".join(commands)}'""",
        capture_output=True,
        text=True,
        shell=True,
    )

    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    if result.returncode != 0:
        raise RuntimeError(f"❌ Error output from code:\n{stderr}")

    return stdout


if __name__ == "__main__":
    code = "print('Hello, World!')"
    result = run_code(code)
    print("Output:", result)
    assert result == "Hello, World!"
