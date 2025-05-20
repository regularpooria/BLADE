#!/bin/bash
#SBATCH --job-name=agentic-ai-tests
#SBATCH --output=slurm_logs/%x_%j.out
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00
#SBATCH --mem-per-cpu=1G

export IS_CLUSTER="true"

DATE=$(date +%Y-%m-%d)
echo "Running tests on $DATE"

# Load modules
module load podman/4.9.5
module load cuda/12.2
module load faiss/1.8.0

# Activate virtual environment
source .venv/bin/activate
if [ -z "$VIRTUAL_ENV" ]; then
  echo "❌ Virtual environment not activated. Exiting."
  exit 1
fi

# --- Podman paths ---
export PODMAN_TMP_BASE="/tmp/pooria-podman"
export XDG_RUNTIME_DIR="$PODMAN_TMP_BASE/runtime"
export PODMAN_ROOT="$PODMAN_TMP_BASE/root"
export PODMAN_RUNROOT="$PODMAN_TMP_BASE/run"

mkdir -p "$XDG_RUNTIME_DIR" "$PODMAN_ROOT" "$PODMAN_RUNROOT"
chmod 700 "$XDG_RUNTIME_DIR"

SOCKET_PATH="$PWD/podman.sock"
export PODMAN_SOCKET_PATH="$SOCKET_PATH"


# --- Check if Podman socket is already live ---
check_podman_alive() {
  python3 - <<EOF
import os
from podman import PodmanClient

sock = os.path.abspath("podman.sock")
try:
    if os.path.exists(sock):
        client = PodmanClient(base_url=f'unix://{sock}')
        client.ping()
        exit(0)
    else:
        exit(1)
except:
    exit(1)
EOF
}


PODMAN_STARTED=0

if check_podman_alive; then
  echo "✅ Podman already running at $SOCKET_PATH"
else
  echo "🔧 Starting Podman at $SOCKET_PATH"
  nohup podman \
    --root="$PODMAN_ROOT" \
    --runroot="$PODMAN_RUNROOT" \
    system service --time=0 "unix://$SOCKET_PATH" \
    > podman_socket.log 2>&1 &
  PODMAN_PID=$!
  PODMAN_STARTED=1
  echo "🟢 Podman service started (PID $PODMAN_PID)"
  sleep 2
fi


pytest
EXIT_CODE=$?

# --- Cleanup ---
if [ "$PODMAN_STARTED" -eq 1 ]; then
  echo "🛑 Stopping Podman service (PID $PODMAN_PID)"
  kill $PODMAN_PID
fi

exit $EXIT_CODE