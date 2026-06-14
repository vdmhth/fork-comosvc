#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/config.sh"

CONDA_BASE=$(conda info --base)
source "${CONDA_BASE}/etc/profile.d/conda.sh"
conda activate "$CONDA_ENV_NAME"

log() { echo "[$(date '+%H:%M:%S')] $1"; }

log "REPO_DIR: $REPO_DIR"

EXTRACT_BASE="${REPO_DIR}/_chunks"
mkdir -p "$EXTRACT_BASE"
mkdir -p "${REPO_DIR}/dataset_raw"

for FILE_ID in "${DATA_CHUNK_IDS[@]}"; do
    CHUNK_FILE="${EXTRACT_BASE}/${FILE_ID}.${CHUNK_FORMAT}"
    EXTRACT_DIR="${EXTRACT_BASE}/extracted_${FILE_ID}"
    if [ ! -f "$CHUNK_FILE" ]; then
        log "Downloading chunk: $FILE_ID"
        gdown "$FILE_ID" -O "$CHUNK_FILE" --fuzzy
    else
        log "Chunk $FILE_ID already downloaded, skipping."
    fi

    if [ ! -d "$EXTRACT_DIR" ]; then
        log "Extracting chunk: $FILE_ID"
        mkdir -p "$EXTRACT_DIR"
        case "$CHUNK_FORMAT" in
            zip)    unzip -q "$CHUNK_FILE" -d "$EXTRACT_DIR" ;;
            tar)    tar -xf  "$CHUNK_FILE" -C "$EXTRACT_DIR" ;;
            tar.gz) tar -xzf "$CHUNK_FILE" -C "$EXTRACT_DIR" ;;
            rar)    unrar x -y "$CHUNK_FILE" "$EXTRACT_DIR/" ;;
            *)      log "ERROR: Unknown CHUNK_FORMAT: $CHUNK_FORMAT"; exit 1 ;;
        esac
        log "Extracted $FILE_ID"
    else
        log "Chunk $FILE_ID already extracted, skipping."
    fi
done
DATA_RAW_DIR="${REPO_DIR}/dataset_raw"
mkdir -p "$DATA_RAW_DIR"

for FILE_ID in "${DATA_CHUNK_IDS[@]}"; do
    EXTRACT_DIR="${EXTRACT_BASE}/extracted_${FILE_ID}"
    log "Sorting chunk: $FILE_ID"
    python3 "${REPO_DIR}/sort_singer.py" \
        --extract_dir     "$EXTRACT_DIR" \
        --dataset_raw_dir "$DATA_RAW_DIR"
done
log "=== Cleaning up temporary files ==="
rm -rf "$EXTRACT_BASE"