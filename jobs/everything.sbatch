#!/bin/bash
#SBATCH --job-name=agentic-ai-tests
#SBATCH --output=slurm_logs/%x_%j.out
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=02:00:00
#SBATCH --mem=10G
#SBATCH --gpus-per-node=1


DATE=$(date +%Y-%m-%d)
echo "Running tests on $DATE"

# Load modules
module load python/3.10
module load StdEnv/2023
module load scipy-stack/2023b
module load cuda/12.2 
module load faiss/1.8.0
module load apptainer/1.3.5

# Activate virtual environment
source .venv/bin/activate
if [ -z "$VIRTUAL_ENV" ]; then
  echo "❌ Virtual environment not activated. Exiting."
  exit 1
fi
EXPORT MODEL_NAME=codesage-small-v2-local
python maybe.py