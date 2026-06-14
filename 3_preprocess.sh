#!/bin/bash
#SBATCH --job-name=comosvc_prep
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a100:1
#SBATCH --mem=64G
#SBATCH --cpus-per-task=8
#SBATCH --time=1-00:00:00
#SBATCH --output=logs/slurm_prep_%j.log
#SBATCH --error=logs/slurm_prep_%j.err

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/config.sh"

CONDA_BASE=$(conda info --base)
source "${CONDA_BASE}/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV_NAME"

log() { echo "[$(date '+%H:%M:%S')] $1"; }

cd "$REPO_DIR"
log "REPO_DIR: $REPO_DIR"

log " Resample to 24000Hz"
python preprocessing1_resample.py -n "$NUM_CPU_PROCESSES"

log " Split train/val/test (80/10/10 per singer) ==="
python preprocessing2_flist.py
log " Tao val_small + verify split"
python make_val_small_and_verify.py

log "Extract features (ContentVec + pitch)"
python preprocessing3_feature.py -c "$TEACHER_CONFIG" -n "${NUM_GPU_PROCESSES:-2}"
rm -rf "${REPO_DIR}/dataset_raw"
log "Done preprocess."
