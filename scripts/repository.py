from git import Repo
import os

GITHUB_URL = "https://github.com/{}"


class Repository:
    extension_dict = {
        "python": [".py"],
        "java": [".java"],
        "c++": [".cpp", ".cxx", ".cc", ".h"],
        "javascript": [".js", ".ts"],
        "go": [".go"]
    }
    def __init__(self, repo_name: str, destination: str, language: str, commit_sha: str=None):
        self.repo_name = repo_name
        self.destination = destination
        self.commit_sha = commit_sha
        self.language = language
        self.file_list = []

    @staticmethod
    def is_hidden(path):
        path_component = path.split("/")
        for item in path_component:
            if item.startswith('.'):
                return False
        return True

    def get_all_file_content(self):
        repo_path = os.path.abspath(self.destination)
        for item in self.file_list:
            filename, file_extension = os.path.splitext(item)
            if file_extension in self.extension_dict[self.language]:
                with open(item, "r") as f:
                    file_name = os.path.basename(item)
                    relative_path = item.replace(repo_path, "")[1:]
                    try:
                        file_content = f.read()
                        yield relative_path, file_name, file_content
                    except UnicodeDecodeError:
                        print("File reading error")
    def get_file_content(self, path:str, sha:str):
        repo_path = os.path.abspath(self.destination)
        try:
            self.cloned_repo.git.checkout(sha)
            if os.path.exists(os.path.join(repo_path, path)) and not os.path.isdir(os.path.join(repo_path, path)):
                with open(os.path.join(repo_path, path), "r") as f:
                    file_name = os.path.basename(path)
                    try:
                        file_content = f.read()
                        return file_content
                    except UnicodeDecodeError:
                        print(f"File reading error {path}----")
                        return ""
            return ""
        except Exception as ex:
            print(ex)
            return ""

    def clone(self):
        self.cloned_repo = Repo.clone_from(GITHUB_URL.format(self.repo_name), self.destination)
        if self.commit_sha:
            self.cloned_repo.git.checkout(self.commit_sha)
        file_list = [os.path.join(dp, f) for dp, dn, filenames in os.walk(self.cloned_repo.working_dir) for f in filenames]
        self.file_list = list(filter(lambda x: Repository.is_hidden(x), file_list))

if __name__ == "__main__":
    repo = Repository(repo_name="apache/kafka", destination="temp", commit_sha="f3038d5e7326b3104a35797ec19f359c923a5040", language='java')
    repo.clone()
    counter = 0
    for item in repo.get_all_file_content():
        counter += 1
    print(counter)