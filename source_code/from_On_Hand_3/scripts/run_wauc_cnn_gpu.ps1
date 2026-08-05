# SPDX-License-Identifier: Apache-2.0

# Run WAUC CNN1D hyperparameter search (early-fusion + late-fusion) on a GPU.
#
# Status as of 2026-07-04: the modality ablation (both/HRV-only/ACC-only, all
# early-fusion) and the late-fusion architecture (both modality) have ALL
# already been run to completion on the CPU machine -- see
# PHASE_WAUC_RUN_LOG.md mucs 4 and 4b. Do NOT rerun those here.
#
# What's actually left, and what this script does: a proper hyperparameter
# search for WAUC specifically (Phase 2's HP search only ever covered WESAD).
# A first attempt at this on CPU was abandoned after ~1.5h with zero folds
# completed (see PHASE_WAUC_RUN_LOG.md) -- WAUC's larger window count makes
# LOSO x grid search too slow on CPU. train_cnn_loso() already auto-selects
# CUDA when available (src/on_hand_3/cnn_training.py), so no code changes are
# needed here, only more compute. Because GPU makes this much cheaper, the
# grid below is wider than the CPU attempt: 3 learning rates x 3 kernel
# sizes x 2 architectures (early/late fusion) = 18 search configs total.
#
# What to copy to the GPU machine before running this:
#   1. The whole On_Hand_3 project folder (or at minimum: src/, experiments/,
#      pyproject.toml, tests/, and this scripts/ folder).
#   2. data/processed/wauc_raw_60s.npz (~100MB) -- this is the ONLY WAUC data
#      file needed for CNN training. Do NOT copy the full data/raw/wauc/ tree
#      (~17GB of raw CSVs); it is not required for this step.
#
# Usage (from an elevated or normal PowerShell, from anywhere):
#   powershell -File path\to\On_Hand_3\scripts\run_wauc_cnn_gpu.ps1
#
# After it finishes, copy these folders back to the main machine's artifacts/:
#   artifacts/wauc_cnn1d_hparam_search_early/
#   artifacts/wauc_cnn1d_hparam_search_late/

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

if (-not (Test-Path "data/processed/wauc_raw_60s.npz")) {
    Write-Error "data/processed/wauc_raw_60s.npz not found. Copy it here before running this script (see header comment)."
    exit 1
}

if (-not (Test-Path ".venv_gpu")) {
    python -m venv .venv_gpu
}
& .\.venv_gpu\Scripts\Activate.ps1

pip install --upgrade pip

# Plain `pip install torch` (or installing the project's generic "torch"
# extra) resolves to PyPI's default wheel, which is CPU-ONLY -- it does NOT
# auto-detect your GPU. This bit us once already (RTX 3060 Ti box silently
# ran on CPU for hours). Force the CUDA-enabled build explicitly, then
# install the rest of the project without letting it touch torch again.
pip uninstall -y torch 2>$null
pip install torch --index-url https://download.pytorch.org/whl/cu124
pip install -e ".[dev]"

python -c "import torch; print('torch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE - falling back to CPU, this script will be slow')"
& .\.venv_gpu\Scripts\python.exe -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)"
if ($LASTEXITCODE -ne 0) {
    Write-Warning "torch.cuda.is_available() is False. If this machine truly has an NVIDIA GPU (check with 'nvidia-smi'), the cu124 wheel above may not match your driver/Python version -- see https://pytorch.org/get-started/locally/ for the correct --index-url, install it manually into .venv_gpu, then rerun this script."
}

python -m pytest -q
if ($LASTEXITCODE -ne 0) {
    Write-Error "Test suite failed -- fix before spending GPU time on training."
    exit 1
}

$dataset = "data/processed/wauc_raw_60s.npz"
$grid = @("--learning-rates", "1e-3", "3e-4", "1e-4", "--kernel-sizes", "3", "5", "7")
$common = @("--search-epochs", "20", "--search-patience", "5", "--final-epochs", "40", "--final-patience", "8", "--t3a-stream-seeds", "0", "1", "2", "3", "4")

Write-Output "=== 1/2: HP search, early fusion (concat PPG+ACC channels) ==="
python experiments/03_cnn1d_hparam_search.py --dataset $dataset --output-dir artifacts/wauc_cnn1d_hparam_search_early @grid @common

Write-Output "=== 2/2: HP search, late fusion (separate PPG/ACC branches) ==="
python experiments/03_cnn1d_hparam_search.py --dataset $dataset --output-dir artifacts/wauc_cnn1d_hparam_search_late @grid @common --late-fusion-ppg-channels 1

Write-Output ""
Write-Output "DONE. Copy these folders back to the main machine's artifacts/ directory:"
Write-Output "  artifacts/wauc_cnn1d_hparam_search_early/"
Write-Output "  artifacts/wauc_cnn1d_hparam_search_late/"
Write-Output "Each has search_summary.json (all candidates + winner) and final/ (winner's full-epoch fold_metrics.csv/summary.json)."
