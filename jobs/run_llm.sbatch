#!/bin/bash
#SBATCH --job-name=llm-extract-traces
#SBATCH --output=slurm_logs/%x_%j.out
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=02:00:00
#SBATCH --mem=15G
#SBATCH --gpus-per-node=1


DATE=$(date +%Y-%m-%d)
echo "Running tests on $DATE"

# Load modules
module load python/3.10
module load StdEnv/2023
module load scipy-stack/2023b
module load cuda/12.2 
# Activate virtual environment
source .venv/bin/activate
if [ -z "$VIRTUAL_ENV" ]; then
  echo "❌ Virtual environment not activated. Exiting."
  exit 1
fi
export OLLAMA_MODELS=/home/pooriar/projects/def-mariam/pooriar/ollama/models
python parse_traceback_llms.py