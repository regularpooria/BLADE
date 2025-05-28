from scripts.run_snippet import run_code


def test_run_code():
    code = "print('Hello, World!')"
    result = run_code(code)
    print("Output:", result)
    assert result == "Hello, World!"


# def test_rejection():
#     code = """import os
# os.system('rm -rf /')"""
#     try:
#         result = run_code(code)
#     except Exception as e:
#         print("Caught exception:", e)
#         assert True
#     else:
#         assert False, "Expected an exception but none was raised"
