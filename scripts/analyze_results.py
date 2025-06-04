from scripts.bugsinpy_utils import get_bugs, parse_changed_files
import os
import json

results_folder = os.path.abspath("tmp/ast/results")
results_files = os.listdir(results_folder)

results = {
    "bugs_skipped": [],  # [{project_name, bug_id, reason}]
    "bugs_failed": [],  # [{project_name, bug_id, detected_files: list, actual_file}]
    "bugs_passed": [],  # [{project_name, bug_id, detected_files: list, actual_files}]
    "success_rate": 0,  # out of 100 (including bugs skipped)
    "success_rate_no_skip": 0,  # out of 100 (excluding bugs skipped)
    "success_projects": {},  # {project_name, success_rate, success_rate_no_skip}
}

success_projects_tmp = {}
count = 0
maximum_bugs = 0
for project in results_files:
    project_name = project.replace("bug_results_", "").replace(".json", "")
    bugs = get_bugs(project_name)
    maximum_bugs += len(bugs)
    success_projects_tmp[project_name] = {
        "skipped": 0,
        "failed": 0,
        "passed": 0,
    }

    with open(f"{results_folder}/{project}", "r", encoding="utf-8") as result_file:
        data = json.loads(result_file.read())
        for bug in bugs:
            changed_files = [
                x.split("/")[-1] for x in parse_changed_files(project_name, bug)
            ]
            filtered_data = list(filter(lambda x: x["index"] == bug, data))
            if len(filtered_data) == 0:
                results["bugs_skipped"].append(
                    {
                        "project_name": project_name,
                        "bug_id": bug,
                        "reason": "The program was unable to find a trace in the bug report",
                    }
                )
                success_projects_tmp[project_name]["skipped"] += 1

                continue

            filtered_data = filtered_data[0]  # there can only exist one so
            files_predicted = [
                obj["file"].split("/")[-1] for obj in filtered_data["errors"]
            ]

            flag = 0
            for changed_file in changed_files:
                if changed_file not in files_predicted:
                    flag += 1

            if flag >= len(changed_files) / 2:
                results["bugs_failed"].append(
                    {
                        "project_name": project_name,
                        "bug_id": bug,
                        "detected_files": files_predicted,
                        "actual_files": changed_files,
                    }
                )
                success_projects_tmp[project_name]["failed"] += 1

            else:
                results["bugs_passed"].append(
                    {
                        "project_name": project_name,
                        "bug_id": bug,
                        "detected_files": files_predicted,
                        "actual_files": changed_files,
                    }
                )
                success_projects_tmp[project_name]["passed"] += 1

    bugs_counted = (
        success_projects_tmp[project_name]["passed"]
        + success_projects_tmp[project_name]["skipped"]
        + success_projects_tmp[project_name]["failed"]
    )

    if len(bugs) != bugs_counted:
        print(f"Bugs length {len(bugs)}")
        print(f"Bugs counted {bugs_counted}")
        raise RuntimeError("The number of bugs input is not the same as output")

    results["success_projects"][project_name] = {
        "success_rate": success_projects_tmp[project_name]["passed"] / bugs_counted,
        "success_rate_no_skip": success_projects_tmp[project_name]["passed"]
        / (bugs_counted - success_projects_tmp[project_name]["skipped"]),
    }
print(success_projects_tmp)

results["success_rate"] = len(results["bugs_passed"]) / (
    len(results["bugs_failed"])
    + len(results["bugs_passed"])
    + len(results["bugs_skipped"])
)
results["success_rate_no_skip"] = len(results["bugs_passed"]) / (
    len(results["bugs_failed"]) + len(results["bugs_passed"])
)
with open(os.path.abspath("results.json"), "w", encoding="utf-8") as file:
    file.write(json.dumps(results, indent=2))
