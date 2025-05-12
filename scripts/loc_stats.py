from os import walk

files = []

for (dirpath, dirnames, filenames) in walk("."):
    for filename in filenames:
        if ".py" in filename and not ".pyc" in filename:
            files.append(dirpath +"/"+ filename)

lines = 0
        
for file in files:
    with open(file, "r") as file_object:
        lines += len(file_object.readlines())
        
print("Files with .py extension:")
print(", ".join(files))
print(f"Total lines: {lines}")