from scripts.bugsinpy_utils import *
from run_ast_old import load_gitignore

projects = get_projects()

dirs = os.listdir("tmp")


def extract_repo_details(repo_path):
    all_chunks = []
    spec = load_gitignore()

    min_lines = None
    max_lines = None
    avg_lines = 0
    sum_lines = 0

    # Gather all Python files first
    python_files = []
    for root, _, files in os.walk(repo_path):
        rel_root = os.path.relpath(root, repo_path)
        if spec and spec.match_file(rel_root):
            continue

        for fname in files:
            rel_path = os.path.normpath(os.path.join(rel_root, fname))
            if spec and spec.match_file(rel_path):
                continue

            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                python_files.append(fpath)

    for python_file in python_files:
        with open(python_file) as f:
            length = len(f.read().split("\n"))
            sum_lines += length
            if not min_lines:
                min_lines = length
            elif min_lines > length:
                min_lines = length

            if not max_lines:
                max_lines = length
            elif max_lines < length:
                max_lines = length

    avg_lines = sum_lines / len(python_files)

    return min_lines, max_lines, avg_lines, len(python_files)


for project in projects:
    clone_project(project)
    info = get_bug_info(project, 1)
    checkout_to_commit(project, info["buggy_commit_id"])

for project in projects:
    # Get the number of bugs
    bugs = get_bugs(project)
    chosen_bugs = []
    for bug in bugs:
        changed_files = parse_changed_files(project, bug)
        if len(changed_files) > 1:
            continue
        info = get_bug_info(project, bug)
        error = get_raw_traceback(project, bug)
        chosen_bugs.append((project, bug, info, error))

    errors = [bug[3] for bug in chosen_bugs]
    errors_length = [len(error.split("\n")) for error in errors]

    minimum = min(errors_length)
    maximum = max(errors_length)
    avg = sum(errors_length) / len(errors)

    # print(f"Details for **{project}**:")
    # print(
    #     f"Bugs: {len(chosen_bugs)}, Avg lines per traceback: {avg}, Maximum: {maximum}, Minimum: {minimum}"
    # )

    min_lines, max_lines, avg_lines, files = extract_repo_details(f"tmp/{project}")

    # print(
    #     f"Files: {files}, Avg lines per file: {avg_lines}, Maximum: {max_lines}, Minimum: {min_lines}"
    # )

    print(
        f"{project} & {len(chosen_bugs)} & {avg:.1f} & {minimum} & {maximum} & {files} & {avg_lines:.1f} & {min_lines} & {max_lines} \\\\"
    )
