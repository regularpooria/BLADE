from scripts.bugsinpy_utils import (
    get_projects,
    clone_project,
    get_bug_info,
    checkout_to_commit,
)

projects = get_projects()
for project in projects:
    clone_project(project)
    info = get_bug_info(project, 1)
    checkout_to_commit(project, info["buggy_commit_id"])

import os
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModel
import torch

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME") or "regularpooria/blaze_code_embedding"
CACHE_DIR = "models/blaze"

# Download and save tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
tokenizer.save_pretrained(CACHE_DIR)

# Download and save model
model = AutoModel.from_pretrained(MODEL_NAME, trust_remote_code=True)
model.save_pretrained(CACHE_DIR)
