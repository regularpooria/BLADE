from scripts.bugsinpy_utils import *


tree, sources = test_to_source_code(
    "youtube-dl", "test/test_utils.py", "test_js_to_json", max_depth=1
)
print("TREE:")
print(tree)
print("\nSOURCES:")
for (file_path, func_name), src in sources.items():
    print(f"\n--- {file_path}::{func_name} ---\n{src}")
