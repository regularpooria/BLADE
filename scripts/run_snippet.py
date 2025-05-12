import subprocess, logging

def run_code(code):
    with open("/tmp/temp_code.py", "w") as f:
        f.write(code)
    result = subprocess.run([
        "docker", "run", "--rm", "-v", "/tmp:/sandbox", "bootcamp-env",
        "python", "/sandbox/temp_code.py"
    ], capture_output=True, timeout=10)
    logging.info("Output:%s", result.stdout.decode())
    logging.error("Errors:%s", result.stderr.decode())