from scripts.bugsinpy_utils import *

# bugs = get_bugs("youtube-dl")
# bugs = ["36"]
# for bug in bugs:

#     bug_info = get_bug_info("youtube-dl", bug)
#     checkout_to_commit("youtube-dl", bug_info["buggy_commit_id"], silent=True)
#     base_line = parse_changed_function_names("youtube-dl", bug)
#     a1 = parse_changed_function_names_2("youtube-dl", bug)
#     print(grab_chunk("youtube-dl", bug, list(a1.keys())[0]))
#     # input()


# project_name = "youtube-dl"
# bug = "1"

# trace_back = get_raw_traceback(project_name, bug)
# bug_info = get_bug_info(project_name, bug)
# buggy_commit_id = bug_info["buggy_commit_id"]
# checkout_to_commit(project_name, buggy_commit_id, silent=True)
# changed_file = parse_changed_files(project_name, bug)
# function_names = parse_changed_function_names(project_name, bug)
# test_functions = extract_function_name_from_traceback(trace_back)
# chunks = {}

# for test_function in test_functions:
#     tree, sources = test_to_source_code(
#         project_name, bug_info["test_file"], test_function, max_depth=0
#     )
#     for (file_path, func_name), src in sources.items():
#         chunks[func_name] = src
# print(chunks.keys())


project_name = "youtube-dl"
bugs = get_bugs(project_name)
for bug in bugs:
    trace_back = get_raw_traceback(project_name, bug)
    bug_info = get_bug_info(project_name, bug)
    buggy_commit_id = bug_info["buggy_commit_id"]
    checkout_to_commit(project_name, buggy_commit_id, silent=True)
    changed_file = parse_changed_files(project_name, bug)
    test_functions = extract_function_name_from_traceback(trace_back)
    a1 = parse_changed_function_names_2("youtube-dl", bug)

    chunks_1 = {}
    chunks_2 = {}
    for test_function in test_functions:
        tree, sources = test_to_source_code(
            project_name, bug_info["test_file"], test_function
        )
        for (file_path, func_name), src in sources.items():
            chunks_1[func_name] = src

        tree, sources = test_to_source_code_2(
            project_name, bug_info["test_file"], test_function
        )
        for (file_path, func_name), src in sources.items():
            chunks_2[func_name] = src
    print(f"----- BUG {bug} -----")
    print(chunks_1.keys())
    print(chunks_2.keys())
    print(a1)
