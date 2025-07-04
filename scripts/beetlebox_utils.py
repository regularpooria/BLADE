import os, json
from datasets import load_from_disk, load_dataset
import subprocess
from scripts.processor import DynamicCodeSplitter, CommentCleaner
from scripts.repository import Repository
import pathspec
from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures import ProcessPoolExecutor
import multiprocessing


DATASET_PATH = "beetlebox_dataset"
ds = load_dataset("bug-localization/BeetleBox", split="test")


def load_gitignore(repo_path):
    """
    Load .gitignore from the cloned repo if it exists,
    else fall back to .gitignore_embedding if available.
    """
    gitignore_repo = os.path.join(repo_path, ".gitignore")
    gitignore_fallback = ".gitignore_embedding"

    if os.path.exists(gitignore_repo):
        with open(gitignore_repo, "r") as f:
            return pathspec.PathSpec.from_lines("gitwildmatch", f)
    elif os.path.exists(gitignore_fallback):
        with open(gitignore_fallback, "r") as f:
            return pathspec.PathSpec.from_lines("gitwildmatch", f)
    else:
        return None  # No spec means include everything


def clone_repo(repo_url, commit_sha, destination):
    if not os.path.exists(destination):
        subprocess.run(["git", "clone", repo_url, destination], check=True)
    subprocess.run(["git", "checkout", commit_sha], cwd=destination, check=True)


def process_files_batch(file_paths, destination, tree_sitter_language):
    import warnings

    warnings.filterwarnings("ignore", category=FutureWarning, module="tree_sitter")
    # If these are in the same file, you don't need to import
    cleaner = CommentCleaner(language=tree_sitter_language)
    splitter = DynamicCodeSplitter(
        language=tree_sitter_language, general_cost=50, max_window_size=30
    )
    batch_chunks = []
    for file_path in file_paths:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            cleaned = cleaner.remove_comments_from_code(code)
            chunks = splitter.split_text(cleaned)
            for chunk in chunks:
                batch_chunks.append(
                    {
                        "file": os.path.relpath(file_path, destination),
                        "chunk": chunk,
                    }
                )
        except Exception as e:
            print(f"  ⚠️ Error processing {file_path}: {e}")
    return batch_chunks


def prepare_dataset():
    N_CORES = multiprocessing.cpu_count()

    for project in ds:
        all_chunks = []

        repo_name = project["repo_name"]
        before_sha = project["before_fix_sha"]
        language = project["language"]
        print(f"\nProcessing: {repo_name} @ {before_sha}")
        output_dir = f"beetlebox_dataset/{repo_name.replace('/', '_')}/{before_sha}"

        if os.path.exists(os.path.join(output_dir, "chunks.json")):
            print(f"EXISTS: {repo_name} @ {before_sha}")
            continue

        repo_url = f"https://github.com/{repo_name}.git"
        destination = f"./tmp/{repo_name.replace('/', '_')}"
        try:
            if not os.path.exists(destination):
                subprocess.run(["git", "clone", repo_url, destination], check=True)
            subprocess.run(["git", "checkout", before_sha], cwd=destination, check=True)
        except subprocess.CalledProcessError:
            print(f"⚠️ Failed to clone or checkout: {repo_url} {before_sha}")
            continue

        tree_sitter_language = "cpp" if language == "c++" else language
        extensions = Repository.extension_dict.get(language, [])

        # --- INLINE gitignore logic here ---
        gitignore_repo = os.path.join(destination, ".gitignore")
        gitignore_fallback = ".gitignore_embedding"
        ignore_spec = None
        if os.path.exists(gitignore_repo):
            with open(gitignore_repo, "r") as f:
                ignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", f)
        elif os.path.exists(gitignore_fallback):
            with open(gitignore_fallback, "r") as f:
                ignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", f)
        # -----------------------------------
        all_files = []
        for root, _, files in os.walk(destination):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext in extensions:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, destination).replace(
                        os.sep, "/"
                    )
                    if ignore_spec and ignore_spec.match_file(rel_path):
                        continue
                    all_files.append(file_path)

        # Split files into N nearly equal chunks for parallel processing
        def chunkify(lst, n):
            k, m = divmod(len(lst), n)
            return [
                lst[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)]
                for i in range(n)
                if lst[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)]
            ]

        batches = chunkify(all_files, N_CORES)

        # Multiprocess chunking
        all_chunks = []
        with ProcessPoolExecutor(max_workers=N_CORES) as executor:
            futures = []
            for batch in batches:
                futures.append(
                    executor.submit(
                        process_files_batch, batch, destination, tree_sitter_language
                    )
                )
            for future in as_completed(futures):
                all_chunks.extend(future.result())

        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, "chunks.json"), "w", encoding="utf-8") as f:
            json.dump(all_chunks, f, indent=2)

        print(f"✔️ Saved {len(all_chunks)} chunks to {output_dir}/chunks.json")


def get_projects():
    return {
        "OpenRefine_OpenRefine": "OpenRefine_OpenRefine",
        "apache_tomcat": "apache_tomcat",
        "eclipse-jdt_eclipse_jdt_ui": "eclipse-jdt_eclipse_jdt_ui",
        "eclipse_org_aspectj": "eclipse_org_aspectj",
        "google_guava": "google_guava",
        "nats-io_nats-server": "nats-io_nats-server",
        "SeleniumHQ_selenium": "SeleniumHQ_selenium",
        "bitcoin_bitcoin": "bitcoin_bitcoin",
        "eclipse-platform_eclipse_platform_swt": "eclipse-platform_eclipse_platform_swt",
        "electron_electron": "electron_electron",
        "langchain-ai_langchain": "langchain-ai_langchain",
        "onnx_onnx": "onnx_onnx",
        "ansible_ansible": "ansible_ansible",
        "ccxt_ccxt": "ccxt_ccxt",
        "eclipse-platform_eclipse_platform_ui": "eclipse-platform_eclipse_platform_ui",
        "facebook_react": "facebook_react",
        "liquibase_liquibase": "liquibase_liquibase",
        "protocolbuffers_protobuf": "protocolbuffers_protobuf",
        "apache_dubbo": "apache_dubbo",
        "cryptomator_cryptomator": "cryptomator_cryptomator",
        "eclipse_birt": "eclipse_birt",
        "fastify_fastify": "fastify_fastify",
        "mozilla_pdf.js": "mozilla_pdf.js",
        "sveltejs_svelte": "sveltejs_svelte",
    }


def update_issue_ids(data, issue_map):
    issue_id_to_hash = {v: k for k, v in issue_map.items()}

    def map_row(batch):
        new_ids = []
        for issue_id in batch["issue_id"]:
            commit_hash = issue_id_to_hash.get(issue_id)
            if commit_hash:
                new_ids.append(commit_hash)
            else:
                # Keep original for now, will filter later
                new_ids.append(None)
                print(f"Warning: No commit hash found for issue id {issue_id}")
        batch["issue_id"] = new_ids
        return batch

    issues_dataset = data["issues"]
    updated_issues = issues_dataset.map(map_row, batched=True)

    # Now filter out the rows that got None
    updated_issues = updated_issues.filter(lambda x: x["issue_id"] is not None)

    data["issues"] = updated_issues
    return data


# def load_project(project):
#     project_path = get_projects()[project]

#     data = load_from_disk(f"{DATASET_PATH}/BeetleBox_Test_Dataset/{project_path}")
#     with open(
#         f"{DATASET_PATH}/BeetleBox_Test_Dataset/{project_path}/version_issue_map_{project_path}.json",
#         "r",
#         encoding="utf-8",
#     ) as f:
#         issue_map = json.loads(f.read())
#     update_issue_ids(data, issue_map)

#     return data


def load_project(project: str):
    if "_" in project:
        project = project.replace("_", "/")
    filtered_ds = ds.filter(lambda example: example["repo_name"] == project)

    return filtered_ds


if __name__ == "__main__":
    prepare_dataset()
