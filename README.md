## BLADE - Bug Localization Assisted Debugging Engine

A research/engineering workspace for experimenting with bug localization on the BugsInPy benchmark using embedding models. It includes utilities to clone/prepare buggy projects, extract error tracebacks, embed text/code with a Hugging Face model, search for likely buggy code chunks, and compute metrics (MAP/MRR, success rates).

### Overall Architecture
Here are some figures that illustrate the overall architecture and different steps of the BLADE pipeline:

- [Overall View](report/overleaf/Figures/OverallView.pdf): This figure (Figure 1 in the report) illustrates the entire Automated Program Repair (APR) pipeline, outlining its four main stages: Input, Bug Localization, Program Repair, and Comparison of Approaches.
- [Embedding Pipeline](report/overleaf/Figures/embed_pipeline.pdf): This figure details the process of converting code and bug reports into numerical representations (embeddings) for similarity-based retrieval, as discussed in the context of model selection and retrieval methods.
- [Step 1: Input Processing](report/overleaf/Figures/Step1_input.drawio.pdf): This figure (Figure 2 in the report) describes the initial phase of input processing, which includes data preparation, code preparation (cloning, filtering, chunking), and bug preparation (traceback extraction).
- [Step 2: Bug Localization](report/overleaf/Figures/Step2_bug_localization.drawio.pdf): This figure (Figure 3 in the report) outlines the bug localization pipeline, showcasing how embedded bug traces are matched against code chunks to identify potential bug locations.
- [Step 3: Automated Program Repair (APR)](report/overleaf/Figures/Step3_APR.drawio.pdf): This figure represents the final stage of the pipeline, where the localized bug information is used to generate and test potential fixes, aiming to automate the program repair process.

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
   git clone https://github.com/regularpooria/bootcamp
   cd bootcamp
   ```
2. Initialize git submodules (required)
   ```bash
   git submodule update --init --recursive
   ```
3. Create and activate a virtual environment
   ```bash
   python3.9 -m venv .venv
   source .venv/bin/activate
   ```
4. Install dependencies
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. Optional: Configure environment variables by creating a `.env` file at the repository root:
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
- **Open in Colab**: [Run analysis quickstart notebook](https://colab.research.google.com/drive/1deoI_khicWoG-90Jn_cka9JlYjlEtnJg?usp=sharing)
- **Open in Colab**: [Chunk embedding quickstart notebook](https://colab.research.google.com/drive/1iOB1wROdt8MDX3zkquNQUuPVGxDJtKdW)
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