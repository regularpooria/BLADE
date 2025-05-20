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

        if stderr:
            raise RuntimeError(f"❌ Error output from code:\n{stderr}")

        return stdout
    finally:
        os.remove(host_path)


if __name__ == "__main__":
    code = "print('Hello, World!')"
    result = run_code(code)
    print("Output:", result)
    assert result == "Hello, World!"
