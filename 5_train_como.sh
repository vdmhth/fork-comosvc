#!/bin/bash
#SBATCH --job-name=comosvc_como
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=8
#SBATCH --time=14-00:00:00
#SBATCH --output=logs/slurm_como_%j.log
#SBATCH --error=logs/slurm_como_%j.err
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/config.sh"

CONDA_BASE=$(conda info --base)
source "${CONDA_BASE}/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV_NAME"

log() { echo "[$(date '+%H:%M:%S')] $1"; }

cd "$REPO_DIR"
log "REPO_DIR: $REPO_DIR"

TEACHER_CKPT="${TEACHER_CKPT:-${REPO_DIR}/logs/teacher/model_800000.pt}"
if [ ! -f "$TEACHER_CKPT" ]; then
    log "WARNING: khong thay $TEACHER_CKPT"
    LATEST=$(ls -v "${REPO_DIR}/logs/teacher/"model_*.pt 2>/dev/null | tail -1)
    if [ -z "$LATEST" ]; then
        log "ERROR: khong co teacher ckpt nao trong logs/teacher/"
        exit 1
    fi
    log "Dung tam ckpt moi nhat: $LATEST"
    TEACHER_CKPT="$LATEST"
fi
log "Teacher checkpoint: $TEACHER_CKPT"
python train.py -t -c "$COMO_CONFIG" -p "$TEACHER_CKPT"
log "Checkpoint: ${REPO_DIR}/logs/como/"