#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
cd -- "$repo_dir"
python_exe="${SLC7A5_PYTHON:-python3}"
stage="${1:-}"
case "$stage" in grn|ctx|aucell) ;; *) echo 'Usage: bash scripts/external/pyscenic.sh {grn|ctx|aucell}' >&2; exit 2;; esac
export PYTHONPATH="$repo_dir${PYTHONPATH:+:$PYTHONPATH}"
out_dir="$($python_exe -c 'from slc7a5_paths import output_dir; print(output_dir("02_SLC7A5_mono_Journal/02_Analysis/pySCENIC/data"))')"
workers="${SLC7A5_SCENIC_WORKERS:-20}"
image='aertslab/pyscenic:0.12.1'
test -f "$out_dir/scRNA_adata_final.loom" || { echo 'Export the loom from Figure3-1 first.' >&2; exit 1; }
docker_args=(run --rm --user "$(id -u):$(id -g)" -v "$out_dir:/data" -w /data)

if [[ "$stage" == grn ]]; then
    tfs="$($python_exe -c 'from slc7a5_paths import dataset_path; print(dataset_path("scenic_tfs"))')"
    docker "${docker_args[@]}" -v "$tfs:/ref/tfs.txt:ro" "$image" pyscenic grn /data/scRNA_adata_final.loom /ref/tfs.txt -o /data/cell_mono_SCENIC.adjacencies.tsv --num_workers "$workers"
elif [[ "$stage" == ctx ]]; then
    ranks1="$($python_exe -c 'from slc7a5_paths import dataset_path; print(dataset_path("scenic_rankings_10kb"))')"
    ranks2="$($python_exe -c 'from slc7a5_paths import dataset_path; print(dataset_path("scenic_rankings_500bp"))')"
    annotations="$($python_exe -c 'from slc7a5_paths import dataset_path; print(dataset_path("scenic_annotations"))')"
    docker "${docker_args[@]}" -v "$ranks1:/ref/rankings_10kb.feather:ro" -v "$ranks2:/ref/rankings_500bp.feather:ro" -v "$annotations:/ref/annotations.tbl:ro" "$image" pyscenic ctx /data/cell_mono_SCENIC.adjacencies.tsv /ref/rankings_10kb.feather /ref/rankings_500bp.feather --annotations_fname /ref/annotations.tbl --expression_mtx_fname /data/scRNA_adata_final.loom -o /data/cell_mono_SCENIC.motifs.csv --num_workers "$workers"
else
    docker "${docker_args[@]}" "$image" pyscenic aucell /data/scRNA_adata_final.loom /data/cell_mono_SCENIC.motifs.csv -o /data/cell_mono_SCENIC.auc.csv --num_workers "$workers"
fi
