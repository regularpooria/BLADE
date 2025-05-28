from scripts.bugsinpy_utils import *
import os


def test_get_folders():
    results = get_projects()

    assert type(results) is list


def test_get_bugs():
    results = get_bugs("pandas")

    assert type(results) is list


def test_get_project_github():
    url = get_project_github("pandas")

    assert url == "https://github.com/pandas-dev/pandas"


def test_clone_project():
    clone_project("youtube-dl")

    assert os.path.isdir("tmp/youtube-dl")


def test_get_bug_info():
    info = get_bug_info("youtube-dl", 1)

    assert info == {
        "python_version": "3.7.0",
        "buggy_commit_id": "99036a1298089068dcf80c0985bfcc3f8c24f281",
        "fixed_commit_id": "1cc47c667419e0eadc0a6989256ab7b276852adf",
        "test_file": "test/test_utils.py",
    }


def test_fail():
    clone_project("fastapi")
    info = get_bug_info("fastapi", 2)
    checkout_to_commit("fastapi", info["buggy_commit_id"])
    install_dependencies("fastapi", 2)
    run_setup("fastapi", 2)

    try:
        run_test("fastapi", 2)
        assert False
    except Exception as e:
        # Throws an error, which is to be expected since we're loading the buggy commit
        print(e)
        assert True


# def test_pass():
#     clone_project("fastapi")
#     info = get_bug_info("fastapi", 2)
#     checkout_to_commit("fastapi", info["fixed_commit_id"])
#     install_dependencies("fastapi", 2)
#     run_setup("fastapi", 2)

#     run_test("fastapi", 2)
