#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/config.sh"

log() { echo "[$(date '+%H:%M:%S')] $1"; }

log "REPO_DIR resolved to: $REPO_DIR"
log "=== Setting up Conda environment: $CONDA_ENV_NAME ==="
CONDA_BASE=$(conda info --base)
source "${CONDA_BASE}/etc/profile.d/conda.sh"

if conda env list | grep -q "^${CONDA_ENV_NAME} "; then
    log "Env '$CONDA_ENV_NAME' already exists, skipping."
else
    conda create -n "$CONDA_ENV_NAME" python=3.8 -y
    log "Env '$CONDA_ENV_NAME' created."
fi

conda activate "$CONDA_ENV_NAME"

log "=== Installing system dependencies ==="
if ! command -v unrar >/dev/null 2>&1; then
    log "Installing unrar..."
    if conda install -n "$CONDA_ENV_NAME" -c conda-forge -y unrar >/dev/null 2>&1; then
        log "unrar installed via conda-forge."
    elif sudo apt-get install -y unrar >/dev/null 2>&1 || sudo apt-get install -y unrar-free >/dev/null 2>&1; then
        log "unrar installed via apt."
    else
        log "WARNING: khong cai duoc unrar (khong sudo + conda fail). Lien he admin cluster."
    fi
else
    log "unrar already installed."
fi
pip install "pip<24" "setuptools==59.5.0" wheel -q
pip install "numpy==1.23.5" "cython<3" -q
pip install -r "${REPO_DIR}/requirements.txt" -q
pip install gdown -q
# --- HiFi-GAN Vocoder ---
HIFIGAN_CKPT="${REPO_DIR}/m4singer_hifigan/model_ckpt_steps_1970000.ckpt"
if [ ! -f "$HIFIGAN_CKPT" ]; then
    log "Downloading m4singer_hifigan..."
    gdown "10LD3sq_zmAibl379yTW5M-LXy2l_xk6h" -O /tmp/m4singer_hifigan.zip
    unzip -q -o /tmp/m4singer_hifigan.zip -d "$REPO_DIR"
    rm /tmp/m4singer_hifigan.zip
    if [ ! -f "$HIFIGAN_CKPT" ]; then
        log "ERROR: sau khi giai nen van khong thay $HIFIGAN_CKPT (kiem tra cau truc zip)."
        exit 1
    fi
    log "m4singer_hifigan done."
else
    log "m4singer_hifigan already exists."
fi

# --- ContentVec ---
mkdir -p "${REPO_DIR}/Content"
CONTENTVEC_PATH="${REPO_DIR}/Content/checkpoint_best_legacy_500.pt"
if [ ! -f "$CONTENTVEC_PATH" ]; then
    log "Downloading ContentVec..."
    curl -L "https://ibm.box.com/shared/static/z1wgl1stco8ffooyatzdwsqn2psd9lrr" \
         -o "$CONTENTVEC_PATH" --retry 3 --retry-delay 5
    SZ=$(stat -c%s "$CONTENTVEC_PATH" 2>/dev/null || echo 0)
    if [ "$SZ" -lt 100000000 ]; then
        log "ERROR: ContentVec chi $SZ bytes (qua nho, co the la HTML). Kiem tra lai link box.com."
        rm -f "$CONTENTVEC_PATH"
        exit 1
    fi
    log "ContentVec done ($SZ bytes)."
else
    log "ContentVec already exists."
fi
# --- Pitch Extractor ---
PE_CKPT="${REPO_DIR}/m4singer_pe/model_ckpt_steps_280000.ckpt"
if [ ! -f "$PE_CKPT" ]; then
    log "Downloading m4singer_pe..."
    gdown "19QtXNeqUjY3AjvVycEt3G83lXn2HwbaJ" -O /tmp/m4singer_pe.zip
    unzip -q -o /tmp/m4singer_pe.zip -d "$REPO_DIR"
    rm /tmp/m4singer_pe.zip
    if [ ! -f "$PE_CKPT" ]; then
        log "ERROR: sau khi giai nen van khong thay $PE_CKPT (kiem tra cau truc zip)."
        exit 1
    fi
    log "m4singer_pe done."
else
    log "m4singer_pe already exists."
fi
log "=== Setup done ==="