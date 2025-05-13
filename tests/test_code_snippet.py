from scripts.run_snippet import run_code

def test_run_code():
    code = "print('Hello, World!')"
    result = run_code(code)
    assert result == "Hello, World!\n"
    
def test_rejection():
    code = """import os
os.system('rm -rf /')"""
    try:
        result = run_code(code)
    except Exception as e:
        assert str(e) == "Unsafe module import: os"
    else:
        assert False, "Expected an exception but none was raised"