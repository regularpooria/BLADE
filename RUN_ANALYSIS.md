## Run analysis: file-level and function-level

This guide explains how to run the analysis in two modes:
- File-level retrieval: predict which files contain the bug
- Function-level retrieval: predict which changed functions were involved

It also describes inputs/outputs, metrics, and tips for running locally or on clusters.

> Quick start: Run the analysis notebook on Colab: [Open in Colab](https://colab.research.google.com/drive/1deoI_khicWoG-90Jn_cka9JlYjlEtnJg?usp=sharing)

### Prerequisites
- Chunks and embeddings generated for all projects/bugs:
  - `dataset/{project}/{bug}/code_chunks.json`
  - `dataset/{project}/{bug}/embedding.npy`
  - If not yet generated, see `CHUNK_EMBEDDING.md` (driven by `generate_dataset_from_bugsinpy.ipynb`).
- Installed dependencies: `pip install -r requirements.txt`
- Optional `.env` for configuration:
  ```env
  MODEL_NAME=regularpooria/blaze_code_embedding
  BATCH_SIZE=128
  ```

### Common configuration
- K (top-K): controls how many candidates to evaluate. Default in notebooks: `K = 60`.
- MODEL_NAME and BATCH_SIZE: read by `scripts/embedding.py` from env or defaults.

### Option A — File-level analysis
You can run this via the script or the notebook.

- Using the notebook: `run_analysis_file.ipynb`
-   What it does:
  - For each project/bug, loads `code_chunks.json` and `embedding.npy`
  - Embeds extracted error tracebacks in batch
  - Builds a FAISS index per bug and retrieves top-K code chunks
  - Writes per-project results to `tmp/ast/results/bug_results_{project}.json`
  - Aggregates metrics and writes `results_{K}.json` (for K in {5,10,15,20})
  - Sections:
    - Setup: imports, `K` definition, folder creation
    - Inference: batch-embeds errors, retrieves top-K per bug, writes `bug_results_{project}.json`
    - Aggregation: computes MAP, MRR, overall and per-project success rates -> writes `results_{K}.json`

Outputs and formats:
- `tmp/ast/results/bug_results_{project}.json` (list per project):
  ```json
  { "index": 42, "files": [ {"file": "pkg/module.py", "function": "foo"}, ... ] }
  ```
- `results_{K}.json` (aggregated):
  - keys: `K`, `model_name`, `MAP`, `MRR`, `searches_passed`, `searches_failed`, `success_rate`, `success_projects`

### Option B — Function-level analysis
This evaluates whether the top-K predictions include the actual changed functions.

- Using the notebook: `run_analysis_function.ipynb`
  - Steps mirror file-level analysis, but compares predicted function names against the set of changed functions for each bug
  - Uses `scripts.bugsinpy_utils.parse_changed_function_names_2` to infer which functions changed from diffs
  - Writes `tmp/ast/results/bug_results_{project}.json` and aggregated `results_{K}.json` (K in {1,5,10} by default)

Notes:
- The function-level notebook sets `model_name` to a static string and (as written) does not compute MAP/MRR; it reports success rates only.
- To run it end-to-end, ensure `embed` and `index_embeddings` are imported (uncomment the import cell):
  ```python
  from scripts.embedding import model, MODEL_NAME, BATCH_SIZE, embed, index_embeddings
  ```
- To avoid overwriting file-level `results_{K}.json`, rename outputs or run in a clean workspace.

### Interpreting metrics
- File-level
  - Success if the true changed file name appears in the top-K predicted file list
  - Reports mean average precision (MAP) and mean reciprocal rank (MRR) across evaluated bugs
- Function-level
  - Success if all changed functions appear in the top-K predicted function list
  - Reports success rates per project and overall

### Where results are written
- Per-project retrievals: `tmp/ast/results/bug_results_{project}.json`
- Aggregated metrics: `results_{K}.json` in repo root

### Reporting
- For simple printing of success rates from an aggregated file-level results JSON, you can use:
  ```bash
  python generate_report.py
  ```
  Adjust the script or adapt for function-level outputs as needed.

### Troubleshooting
- Missing embeddings: Make sure `embedding.npy` exists for each `{project, bug}` (run chunking/embedding first)
- Model download on clusters: Pre-download and set `HF_HOME`/`TRANSFORMERS_CACHE` to a shared path; jobs do not have Internet
- Function-level notebook error `embed is not defined`: Import from `scripts.embedding` as shown above
