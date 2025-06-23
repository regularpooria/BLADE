import ollama


def generate(prompt):
    response = ollama.chat(
        model="phi4-mini:3.8b",
        messages=[
            {
                "role": "system",
                "content": """You are an expert programmer helping debug Python errors.

    You are given a traceback, which may include system/library/internal calls. Your task is to:
    - Only return the lines relevant to debugging the error (i.e., exclude system, standard library, and internal framework calls).
    - Keep lines that are inside the user's project code or directly contributed to the crash.
    - Keep the final error message.

    Only return these important lines — no explanations or extra commentary.""",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response["message"]["content"]


print(
    generate(
        """Traceback (most recent call last):
File "/usr/lib/python3.10/runpy.py", line 196, in _run_module_as_main
return _run_code(code, main_globals, None,
File "/usr/lib/python3.10/runpy.py", line 86, in _run_code
exec(code, run_globals)
File "main.py", line 12, in <module>
my_function()
File "utils/math.py", line 44, in my_function
return 1 / 0
ZeroDivisionError: division by zero"""
    )
)

import json
from scripts.bugsinpy_utils import *

projects = get_projects()
all_tracebacks = []

for project in projects:
    bugs = get_bugs(project)
    for bug in bugs:
        changed_files = parse_changed_files(project, bug)
        if len(changed_files) > 1:
            continue

        raw_error = get_raw_traceback(project, bug)
        if len(raw_error) > 10000:
            raw_error = raw_error[:10000]
        filtered_error = generate(raw_error)
        print(
            f"Project: {project}, Bug: {bug}. Before: {len(raw_error)} After: {len(filtered_error)}"
        )

        all_tracebacks.append(
            {"project": project, "bug_id": bug, "filtered_traceback": filtered_error}
        )

# Save to a single JSON file
with open("filtered_tracebacks.json", "w") as f:
    json.dump(all_tracebacks, f, indent=2)
