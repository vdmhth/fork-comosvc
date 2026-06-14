#!/bin/bash
#SBATCH --job-name=comosvc_teacher
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=8
#SBATCH --time=14-00:00:00
#SBATCH --output=logs/slurm_teacher_%j.log
#SBATCH --error=logs/slurm_teacher_%j.err

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/config.sh"

CONDA_BASE=$(conda info --base)
source "${CONDA_BASE}/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV_NAME"

cd "$REPO_DIR"
log "REPO_DIR: $REPO_DIR"
log "=== Training Teacher Model ==="
python train.py

log "=== Teacher training complete! ==="
log "Checkpoint: ${REPO_DIR}/logs/teacher/"