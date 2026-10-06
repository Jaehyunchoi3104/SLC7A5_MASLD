# SLC7A5-high Monocytes in MASLD — Analysis Code

Analysis code for SLC7A5-high monocytes in metabolic dysfunction-associated steatotic liver disease (MASLD), covering scRNA-seq, snRNA-seq, PBMC, siSLC7A5 knockdown bulk RNA-seq, and the HYU cohort. The repository also includes separate HwangBJ liver nuclei and PBMC analyses with donor Harmony integration and a donor-level MASL–MASH comparison.

The **17 main analyses** use shared input-path configuration and save new outputs under this repository's `results/` directory. Original source files outside the repository were left unchanged when preparing these copies. The 75 organized scripts comprise 17 main analysis scripts, 3 HwangBJ execution helpers, 12 supporting scripts, and 43 archived scripts.

## Quick Start

Run the following commands from the repository root, which is the local `git/` directory.

1. Prepare the Python or R environment using the [environment guide](docs/dependencies.md). The candidate Python environment specification is `environment/python.yml`; R packages are listed in `environment/r-packages.tsv`. These files are dependency specifications, not environment lock files validated by a complete analysis run.
2. Set the data root and input-specific paths in `config/paths.local.json`. This local configuration file is excluded from Git. On a new computer, create it by following the [input-data guide](docs/data_requirements.md).
3. Check the inputs and environment for the analysis you intend to run.

```bash
python tools/check_inputs.py --analysis figure1 --schema
python tools/check_environment.py
```

4. Open Python notebooks inside the repository and execute them from the first setup cell. The R execution helper below also saves HTML reports and intermediate files under `results/`.

```bash
jupyter lab
Rscript tools/check_r_packages.R
Rscript tools/render_rmd.R bulk_nosi
```

To generate the supplementary marker table, run `python scripts/utils/make_suppl_table.py`. Most notebooks start from processed AnnData objects or existing analysis outputs; HwangBJ starts from sparse count matrices and metadata supplied as RDS files. This repository is not a single automated pipeline that generates every figure from FASTQ files. See the execution order below for pySCENIC.

## Analyses and Execution Order

| Analysis ID | Description | Entry point |
| --- | --- | --- |
| `figure1` | scRNA composition and DEG/GSEA for the top and bottom 20% of SLC7A5 expression | [Figure1](scripts/scrna/manuscript/Figure1.ipynb) |
| `figure2` | Classical and SLC7A5-high monocytes, including donor-level composition comparisons | [Figure2](scripts/scrna/manuscript/Figure2.ipynb) |
| `figure3_regulons` | Transcription factors, regulons, and AUC | [Figure3-1](scripts/scrna/manuscript/Figure3-1.ipynb) |
| `figure3_cellphone` | CellPhoneDB | [Figure3-2](scripts/scrna/manuscript/Figure3-2.ipynb) |
| `figure3_signaling` | TLR4/TNF/NFKB/mTORC1 scores | [Figure3-3](scripts/scrna/manuscript/Figure3-3.ipynb) |
| `suppl_figure2` | Monocyte markers and inflammatory genes | [Supplementary Figure2](scripts/scrna/manuscript/Suppl_Figure2_analysis.ipynb) |
| `figure1_nucseq` | snRNA validation of SLC7A5 expression | [Figure1_Nucseq](scripts/snrna/manuscript/Figure1_Nucseq.ipynb) |
| `nucseq_gsea` | GSEA comparing SLC7A5-positive and SLC7A5-negative nuclei | [Nucseq_GSEA](scripts/snrna/gsea/Nucseq_GSEA_SLC7A5Fig1.ipynb) |
| `pbmc` | PBMC monocyte analysis | [SLC_pbmc](scripts/pbmc/SLC_pbmc.ipynb) |
| `hwangbj` | Separate liver nuclei MASL1–4 and PBMC MASL/MASH analyses: donor Harmony, reference annotation, and donor-level comparison | [HwangBJ_analysis](scripts/hwangbj/HwangBJ_analysis.ipynb) |
| `bulk_full` | All siSLC7A5/LPS samples | [DESeq2](scripts/bulk/knockdown/Liver_siSLC_bulk_DESeq2.Rmd) |
| `bulk_nosi` | Bulk analysis excluding siCon_1 | [DESeq2_nosiCon1](scripts/bulk/knockdown/Liver_siSLC_bulk_DESeq2_nosiCon1.Rmd) |
| `bulk_additional` | Additional bulk expression inputs | [DESeq2_additional](scripts/bulk/knockdown/additional/Liver_siSLC_bulk_DESeq2_additional.Rmd) |
| `nfkb_shared` | Shared NF-kB targets between scRNA and bulk analyses | [Supplementary Figure S3](scripts/bulk/knockdown/Supplementary_Figure_S3_shared_NFKB_targets.Rmd) |
| `hyu_validation` | Validation in the independent HYU cohort | [HYU_validation](scripts/bulk/hyu/HYU_independent_bulk_validation.Rmd) |
| `hyu_fibrosis` | Association between SLC7A5 expression and fibrosis in the HYU cohort | [HYU_fibrosis](scripts/bulk/hyu/HYU_SLC7A5_fibrosis_expression.Rmd) |
| `monomac_table` | Supplementary monocyte/macrophage marker table | [make_suppl_table.py](scripts/utils/make_suppl_table.py) |

Figure1 generates CellPhoneDB inputs and myeloid DEG results; Figure2 generates the annotated object used by subsequent monocyte analyses. Figure3-1, Figure3-3, and Supplementary Figure2 use Figure2 outputs. The shared NF-kB analysis requires outputs from `bulk_nosi` and Figure1. Upstream steps may be skipped when the same input snapshots are already available. HYU candidate-gene inputs point to the DEG files used in the original HYU validation and are not automatically replaced by other bulk results.

To recompute pySCENIC in Figure3-1, run the notebook through the loom-export cell, then run the following commands before continuing with the subsequent notebook cells:

```bash
bash scripts/external/pyscenic.sh grn
bash scripts/external/pyscenic.sh ctx
bash scripts/external/pyscenic.sh aucell
```

Docker computation can be skipped when using existing adjacency, motif, and AUC files. Four external reference files are required for recomputation.

Analysis-specific inputs and upstream dependencies are documented in [analysis_inputs.md](docs/analysis_inputs.md) and [analyses.json](config/analyses.json).

### Donor-Level Composition and HwangBJ Analyses

**Updated October 6, 2026:** Figure2 composition comparisons use one frequency per donor, with a two-sided exact permutation test of the Mann–Whitney U statistic and Benjamini–Hochberg (BH) correction across nine cell types. The denominator is the total number of myeloid cells retained for each donor. The previous pooled-cell Fisher tests and significance labels based on unadjusted P values were replaced with donor-level statistics and boxplots. Healthy CD45 libraries are merged by donor. MASLD sample IDs are assumed to identify independent donors; this mapping must be checked against clinical metadata. Other exploratory analyses, including cell-level DEG analyses, have not all been converted to donor-level inference.

HwangBJ liver nuclei from four MASL donors and PBMC from four MASL and four MASH donors are processed separately. Following provisional reference-matched cluster annotation, the PBMC analysis compares donor-level high-cluster frequencies among monocytes using an exact permutation test of the mean difference across 70 label allocations and a donor bootstrap confidence interval. See the [HwangBJ guide](docs/hwangbj.md) for execution instructions and interpretation of the annotation.

## Repository Structure

```text
git/
├── scripts/           # 17 main analyses, HwangBJ helpers, and external tools
├── supporting/        # 12 supporting scripts; shared path refactoring not applied
├── archive/           # 43 historical/reference scripts; path refactoring not applied
├── config/            # Input catalog, path examples, analyses, and bulk sample groups
├── slc7a5_paths.py     # Python input/output path helpers
├── R/paths.R          # R input/output path helpers
├── tools/             # Input, environment, and syntax checks; R Markdown execution
├── tests/             # Input preservation, path isolation, and sample-mapping tests
├── environment/       # Dependency specifications and observed package versions
├── docs/              # Source mappings, release history, and validation scope
├── data/              # User-supplied inputs; excluded from Git
└── results/           # Generated outputs and reports; excluded from Git
```

Input datasets are not bundled with the repository. The `data/` directory can be used when preparing external inputs. Scripts in `supporting/` and `archive/` may retain original personal paths and are not covered by the main-analysis execution instructions.

## Validation and Reproducibility Status

The [validation record](docs/validation.md) documents source-format and syntax checks for the 17 main analyses and HwangBJ helpers, 10 Python path tests, R path isolation and sample mapping, input availability and selected schema checks, supplementary Excel table generation, and hash verification against 79 current original-source snapshots. Selected Figure2 and HwangBJ donor-level statistical outputs were reproduced from saved inputs and matched the original results. A complete rerun of all figures, including the full HwangBJ Harmony analysis, has not been performed for this repository copy.

Before final manuscript release, complete the unresolved accessions and download locations in the [input catalog](config/inputs.json), verify the final analysis environment, and compare the generated figures with the manuscript. The manuscript DOI, code license, and archival code DOI have not yet been specified. Prepare data access instructions according to the [data guide](docs/data_requirements.md).

[All 75 organized scripts](docs/script_index.md) · [Initial source mapping](docs/source_manifest.tsv) · [Updated source snapshots](docs/update_source_manifest.tsv) · [Release hashes](docs/release_manifest.tsv) · [Release notes](docs/release_notes.md)
