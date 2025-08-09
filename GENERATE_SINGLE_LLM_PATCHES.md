## Generate single LLM patches

This guide explains the workflow in `generate_single_llm_patches.ipynb` to produce candidate code fixes (function-level patches) from an LLM using a traceback and relevant code snippets.

### Overview
- Input: a bug's Python traceback and one or more candidate code chunks (functions) likely related to the failure
- Model: OpenAI-compatible endpoint (via OpenRouter) with a DeepSeek reasoning model by default
- Output: extracted function-level patch candidates, including function names and full function bodies, serialized to JSON for later application/evaluation

### Prerequisites
- Python environment with repo requirements installed
- API key environment variable:
  - `OPENROUTER_KEY` set in your environment or `.env`
- Upstream artifacts available:
  - `tmp/ast/results/bug_results_{project}.json` from retrieval (optional, if you use those to select candidate chunks)
  - `dataset/{project}/{bug}/code_chunks.json` to fetch original function code if needed

### Configuration variables (in the notebook)
- `MODEL_NAME`: label used in result filenames; default: `baseline_all_deepseek-r1-0528`
- `SYSTEM_PROMPT`: strict instructions for the LLM to output only complete, corrected function definitions, each inside its own ```python fenced block
- `FIRST_TIME`: toggles whether to seed from prior results or start fresh
- `PREVIOUS_RESULTS_PATH`: path to a previous run to continue context (optional)
- OpenAI client setup:
  ```python
  from openai import OpenAI
  client = OpenAI(api_key=os.environ["OPENROUTER_KEY"], base_url="https://openrouter.ai/api/v1")
  ```

### Prompting and generation
- The conversation is assembled as messages:
  - system: `SYSTEM_PROMPT`
  - user: `Traceback: ...` (raw or extracted Python traceback)
  - user: `Code: ...` (joined candidate functions/snippets)
- Subsequent iterations append another user message `New error: ...` to the same chat if you re-try with feedback
- The API call uses chat completions:
  ```python
  completion = client.chat.completions.create(
      model="deepseek/deepseek-r1-0528",
      messages=previous_chat,
      extra_body={}
  )
  ```

### Extracting function patches from the response
- The notebook uses regex-based parsing to extract fenced code blocks and function definitions:
  - Find ```python ... ``` blocks
  - Inside blocks, extract each full `def name(...): ...` function
  - Record function names and sources
- The parser enforces Python language blocks and ignores non-Python fences

### Result structure and persistence
- Collected results are appended to `llm_results` and written as JSON under `tmp/ast/results/llm/single/`, with a timestamp in the filename, e.g.:
  - `tmp/ast/results/llm/single/{MODEL_NAME}_MM_DD_YYYY__HH_MM_SS.json`
- Each entry typically includes:
  - `project`, `bug_id`
  - `traceback`
  - `chunks` (the input snippets provided to the LLM)
  - `functions` (list of `{name, code}` extracted from the LLM response)

### Practical usage pattern
1. Select a bug and gather inputs
   - Extract traceback via `scripts.bugsinpy_utils.extract_python_tracebacks(project, bug)`
   - Select top-K candidate chunks for that bug (e.g., from retrieval results or filtered `code_chunks.json`)
2. Call `generate_code(trace_back, chunks)`
   - Provides chat messages and returns the model output text
3. Parse patches
   - Use `extract_code(text)` to get `{name, code}` for each function
4. Save results for later evaluation/apply

### Tips and constraints
- Patches must update only the given functions; do not modify tests or introduce new imports per `SYSTEM_PROMPT`
- Use separate ```python fenced blocks for multiple functions
- Long tracebacks/snippets: keep within model context; consider pruning unrelated context
- Reproducibility: store `MODEL_NAME`, prompts, and inputs with outputs

### Extending to application/evaluation
- Apply patches by replacing target function bodies in the buggy commit, then run tests
- For locating the right file/path for a function, correlate function names from LLM output with `code_chunks.json` entries
- Automate evaluation by reusing test runners in `scripts.bugsinpy_utils.py` (`run_test`, `checkout_to_commit`, etc.)

### Security and costs
- API usage depends on the configured provider; control temperature and tokens as needed
- Never log secrets; use environment variables and .env
