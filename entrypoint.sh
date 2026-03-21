#!/usr/bin/env bash
set -euo pipefail

: "${MODEL_PATH:?MODEL_PATH is required}"
: "${MMPROJ_PATH:?MMPROJ_PATH is required}"
: "${PORT:=8000}"
: "${CTX_SIZE:=8192}"
: "${N_GPU_LAYERS:=999}"
: "${THREADS:=8}"
: "${BATCH_SIZE:=1024}"
: "${UBATCH_SIZE:=512}"
: "${ENABLE_THINKING:=false}"

CHAT_TEMPLATE_KWARGS="{\"enable_thinking\":${ENABLE_THINKING}}"

exec /app/llama-server \
  --model "${MODEL_PATH}" \
  --mmproj "${MMPROJ_PATH}" \
  --host 0.0.0.0 \
  --port "${PORT}" \
  --ctx-size "${CTX_SIZE}" \
  --threads "${THREADS}" \
  --batch-size "${BATCH_SIZE}" \
  --ubatch-size "${UBATCH_SIZE}" \
  --n-gpu-layers "${N_GPU_LAYERS}" \
  --chat-template-kwargs "${CHAT_TEMPLATE_KWARGS}"