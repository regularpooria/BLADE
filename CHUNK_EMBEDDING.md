## Chunking and embedding using generate_dataset_from_bugsinpy.ipynb

This document explains exactly how `generate_dataset_from_bugsinpy.ipynb` produces code chunks and embeds them into vectors for search, using helper modules (`run_ast_old.py`, `scripts/embedding.py`, `scripts/bugsinpy_utils.py`).

> Quick start: You can view and run a working version of the notebook on Colab: [Open in Colab](https://colab.research.google.com/drive/1iOB1wROdt8MDX3zkquNQUuPVGxDJtKdW)

### Outputs per bug
Artifacts are written under `dataset/{project}/{bug}/`:
- `code_chunks.json` — extracted code snippets from the buggy commit
- `embedding.npy` — NumPy array of embeddings for the snippets in `code_chunks.json`, in the same order

These are later consumed by analysis to build FAISS indices and run retrieval.

### Prerequisites
- `BugsInPy/` dataset checked out
- Python env with `requirements.txt` installed
- Optional `.env` at repo root for configuration:
```env
MODEL_NAME=regularpooria/blaze_code_embedding
BATCH_SIZE=128
# Optional caching to avoid repeated downloads on clusters
# HF_HOME=./models/hf-cache
# TRANSFORMERS_CACHE=./models/hf-cache
```

### Step 1 — Clone projects and checkout buggy commits
From `scripts.bugsinpy_utils.py` used in the notebook:
- `get_projects()` lists projects to process
- `clone_project(project)` clones into `tmp/{project}`
- `get_bug_info(project, bug)` returns commit IDs
- `checkout_to_commit(project, info["buggy_commit_id"])` checks out the buggy revision

This prepares the working tree for chunk extraction per bug.

### Step 2 — Extract code chunks
Chunking is implemented in `run_ast_old.py` and driven by the notebook:
- `load_gitignore()` reads `.gitignore_embedding` (if present) to skip files/dirs
- `get_python_files(repo_path)` lists Python files honoring ignore rules
- `process_file(fpath)` parses the file with `asttokens` and extracts:
  - a synthetic `root` chunk (top-level code with defs/classes removed)
  - each `class` and `def` body as separate chunks
- `extract_chunks(python_files)` parallelizes chunk extraction

For each `{project, bug}`, the notebook writes:
- `dataset/{project}/{bug}/code_chunks.json` with entries `{ "file", "name", "code" }`

### Step 3 — De-duplicate texts for efficient embedding
Before embedding, the notebook aggregates all chunk texts across projects/bugs:
- Builds `texts_to_embed` (unique code strings) and a mapping `text_to_indices`
- Avoids re-embedding identical snippets, significantly reducing compute time

### Step 4 — Batch embed unique texts
`scripts/embedding.py` provides the embedding logic:
- Loads `MODEL_NAME` (default `regularpooria/blaze_code_embedding`) via `transformers`
- Uses GPU if available; moves model to half precision (`.half()`) when not on CPU
- Tokenizes to `max_length=1024`, runs a forward pass, and applies masked mean pooling to get one vector per input
- Batch size is controlled by `BATCH_SIZE`

In the notebook:
- `all_embeddings = embed(texts_to_embed, batch_size=BATCH_SIZE, show_progress_bar=True)`
- Fills `embedding_cache[text] = vector` for reuse across bugs

### Step 5 — Write per-bug embeddings aligned with chunks
For each `{project, bug}`:
- Load `code_chunks.json`
- Rebuild the per-chunk embedding list in the same order: `[embedding_cache[chunk["code"]] for chunk in chunks]`
- Save `dataset/{project}/{bug}/embedding.npy`

This preserves strict 1:1 alignment: `code_chunks.json[i]` ↔ `embedding.npy[i]`.

### Optional — Index and search later
Downstream (e.g., in `run_analysis.py`):
- Load embeddings with `np.load(...)`
- Build FAISS L2 index using `scripts.embedding.index_embeddings(embeddings)`
- Search with `index.search(query_vectors, k=K)` where `query_vectors` are embedded tracebacks or queries

### How to run
- Open and execute `generate_dataset_from_bugsinpy.ipynb`
  - First cells perform cloning and chunk extraction
  - Later cells de-duplicate, embed, and write `embedding.npy`
- Ensure dependencies and optional `.env` are in place

### Cluster reminders
- Jobs have no Internet; pre-download models/tokenizers on the login node and set `HF_HOME`/`TRANSFORMERS_CACHE`
- Prefer `module load` for system packages; use `pip --no-index` as applicable
- See: `cluster_how_to/cluster_readme.md`, `login.md`, `folders.md`, `clone.md`, `limitations.md`

### File reference
- Notebook: `generate_dataset_from_bugsinpy.ipynb`
- Chunking: `run_ast_old.py`
- Embedding: `scripts/embedding.py`
- Dataset utilities: `scripts/bugsinpy_utils.py`
