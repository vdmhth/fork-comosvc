REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONDA_ENV_NAME="comosvc"

TEACHER_CONFIG="${REPO_DIR}/configs/diffusion.yaml"
COMO_CONFIG="${REPO_DIR}/configs/diffusion.yaml"
CHUNK_FORMAT="rar"

DATA_CHUNK_IDS=(
    "17u0IBwdwZnJU6X0Nh_zEd6a7oz2EnyIZ"
    "1Zjair5o_bP_K6TKV9sTOfvzHabB-Gsbt"
    "1BlPioErdIGdjnXTXy0PTn_gX7pkajVOs"
    "10rDUESLQ5QXSW32MbqlXfEOyb1z6kO1R"
    "1xBBc_Cz4weihvb5O_Q5V4xryUZD3f4Fu"
    "1kztz57Vrrldj_9HaUnuLyws0pt-lwIpr"
)
NUM_CPU_PROCESSES="${SLURM_CPUS_PER_TASK:-8}"
NUM_GPU_PROCESSES=2
GPU_ID=0
