import json

# Load your data
with open("results_10.json", "r") as f:
    data = json.load(f)

# Desired project order
ordered_projects = [
    "youtube-dl",
    "keras",
    "matplotlib",
    "black",
    "thefuck",
    "scrapy",
    "pandas",
    "luigi",
    "ansible",
]

# Print header
print(f"{'Project':<15} {'Passed':>6} {'Failed':>6} {'Total':>6} {'Success Rate':>13}")
print("=" * 50)

# Print each project in order
for project in ordered_projects:
    stats = data["success_projects"][project]
    passed = stats["passed"]
    failed = stats["failed"]
    total = stats["total"]
    rate = stats["success_rate"]
    print(rate)

# Print overall success rate
print("\nOverall Success Rate:", f"{data['success_rate'] * 100:.2f}%")
