## Bootcamp Project

A research/engineering workspace for experimenting with bug localization on the BugsInPy benchmark using embedding models. It includes utilities to clone/prepare buggy projects, extract error tracebacks, embed text/code with a Hugging Face model, search for likely buggy code chunks, and compute metrics (MAP/MRR, success rates).

### Contents
- **Core code**:
  - `scripts/embedding.py`: Embedding utilities powered by `transformers`/`torch` and FAISS.
  - `scripts/bugsinpy_utils.py`: Helpers to clone projects, parse diffs/tracebacks, and run setup/tests.
  - See `RUN_ANALYSIS.md` for running file/function analysis.
- **Data**:
  - `BugsInPy/`: The BugsInPy dataset/projects layout used by the pipeline.
  - `dataset/`: Generated `code_chunks.json` and `embedding.npy` per project/bug.
  - `tmp/`: Working directory for cloned repos, venvs, and intermediate files.
- **Cluster docs**: See `cluster_how_to/` (overview: `cluster_how_to/cluster_readme.md`).
 - **How chunking and embedding works**: See `CHUNK_EMBEDDING.md` (driven by `generate_dataset_from_bugsinpy.ipynb`).
 - **How to run analysis (file + function)**: See `RUN_ANALYSIS.md` for both modes.
 - **Generate single LLM patches**: See `GENERATE_SINGLE_LLM_PATCHES.md` to produce candidate function fixes from an LLM.

### Prerequisites
- **Python**: 3.9 (recommended; aligns with the provided `Dockerfile`).
- **OS**: Linux/macOS/WSL2. GPU is optional but accelerates embedding.
- **pip/venv**: Make sure you can create virtual environments.

### Local setup
1. Clone the repository
   ```bash
   git clone <your-fork-or-repo-url>
   cd bootcamp
   ```
2. Create and activate a virtual environment
   ```bash
   python3.9 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Optional: Configure environment variables by creating a `.env` file at the repository root:
   ```env
   # Hugging Face model used for embeddings (default is below)
   MODEL_NAME=regularpooria/blaze_code_embedding
   # Batch size for embedding
   BATCH_SIZE=128
   # Optional: set Hugging Face cache to avoid re-downloading
   # HF_HOME=./models/hf-cache
   # TRANSFORMERS_CACHE=./models/hf-cache
   ```

### Quickstart
- See `RUN_ANALYSIS.md` for step‑by‑step instructions to run file‑level and function‑level analyses (via notebooks and scripts described there).

- **Run tests**:
  ```bash
  pytest
  ```

### Running on the research clusters
Start here:
- `cluster_how_to/cluster_readme.md` — overview and sequence

Deep dives:
- `cluster_how_to/login.md` — access, SSH keys, Duo
- `cluster_how_to/folders.md` — where to keep code/data
- `cluster_how_to/clone.md` — cloning, venvs, and installing dependencies efficiently
- `cluster_how_to/limitations.md` — important constraints (no Docker in jobs, no Internet, caching)

Key cluster notes:
- Jobs have **no Internet access**; prepare/copy caches (e.g., Hugging Face) on the login node.
- Prefer `module load` for system packages; use `pip --no-index` where possible per DRA docs.
- Use Python virtual environments per project.
- For containerized execution on clusters, use **Apptainer** (see the docs above).


### License
See `LICENSE`.
