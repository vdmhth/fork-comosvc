#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
log() { echo "[$(date '+%H:%M:%S')] === $1 ==="; }
 
mkdir -p "${SCRIPT_DIR}/logs"
 
log "Setup environment + pretrained checkpoints (can internet)"
bash "${SCRIPT_DIR}/1_setup.sh"
log "Download & reorganize data (can internet)"
bash "${SCRIPT_DIR}/2_download_data.sh"
 
log "SETUP + DOWNLOAD DONE"