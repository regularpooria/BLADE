# import subprocess
# import os
# from scripts.bugsinpy_utils import *

# projects = get_projects()

# # for project in projects:
# #     bugs = get_bugs(project)
# #     for bug in bugs:
# #         tracebacks = extract_python_tracebacks(project, bug)
# #         with open("tmp.txt", "w") as file:
# #             file.write(tracebacks)
# #         file = os.path.abspath(
# #             f"{FOLDER_NAME}/projects/{project}/bugs/{bug}/bug_buggy.txt"
# #         )
# #         subprocess.run(["code", "--reuse-window", "--diff", "tmp.txt", file])
# #         print(project, bug)
# #         input("Continue?")

# project = "keras"
# bug = 24
# tracebacks = extract_python_tracebacks(project, bug)
# with open("tmp.txt", "w") as file:
#     file.write(tracebacks)
# file = os.path.abspath(f"{FOLDER_NAME}/projects/{project}/bugs/{bug}/bug_buggy.txt")
# subprocess.run(["code", "--reuse-window", "--diff", "tmp.txt", file])

# # Open in current VSCode window


from scripts import beetlebox_utils

beetlebox_utils.prepare_dataset()
