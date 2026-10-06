# 분석별 입력 목록

이 문서는 `config/analyses.json`과 `config/inputs.json`의 공개용 색인이다. 입력 ID별 경로/다운로드 정보의 기준은 해당 JSON 파일이다. 선행 단계는 입력이 이미 있으면 생략할 수 있는 생성 관계를 뜻한다.

| 분석 ID | 코드 | 필수 입력 ID | 선택 입력 ID | 선행 분석 |
| --- | --- | --- | --- | --- |
| `figure1` | [Figure1.ipynb](../scripts/scrna/manuscript/Figure1.ipynb) | `scrna_monomac_seed` | — |  |
| `figure2` | [Figure2.ipynb](../scripts/scrna/manuscript/Figure2.ipynb) | `scrna_mono_seed` | — |  |
| `figure3_regulons` | [Figure3-1.ipynb](../scripts/scrna/manuscript/Figure3-1.ipynb) | `scrna_mono_final`, `scenic_adjacencies`, `scenic_motifs`, `scenic_auc` | — | figure2 |
| `figure3_cellphone` | [Figure3-2.ipynb](../scripts/scrna/manuscript/Figure3-2.ipynb) | `scrna_monomac`, `scrna_mono_seed`, `scrna_raw`, `cpdb_database` | — | figure1 |
| `figure3_signaling` | [Figure3-3.ipynb](../scripts/scrna/manuscript/Figure3-3.ipynb) | `scrna_mono_final` | — | figure2 |
| `suppl_figure2` | [Suppl_Figure2_analysis.ipynb](../scripts/scrna/manuscript/Suppl_Figure2_analysis.ipynb) | `scrna_mono_final` | — | figure2 |
| `figure1_nucseq` | [Figure1_Nucseq.ipynb](../scripts/snrna/manuscript/Figure1_Nucseq.ipynb) | `snrna_stage`, `snrna_shared`, `snrna_gse210077` | — |  |
| `nucseq_gsea` | [Nucseq_GSEA_SLC7A5Fig1.ipynb](../scripts/snrna/gsea/Nucseq_GSEA_SLC7A5Fig1.ipynb) | `snrna_stage` | — |  |
| `pbmc` | [SLC_pbmc.ipynb](../scripts/pbmc/SLC_pbmc.ipynb) | `pbmc_annotated` | — |  |
| `bulk_full` | [Liver_siSLC_bulk_DESeq2.Rmd](../scripts/bulk/knockdown/Liver_siSLC_bulk_DESeq2.Rmd) | `bulk_counts`, `bulk_tpm` | — |  |
| `bulk_nosi` | [Liver_siSLC_bulk_DESeq2_nosiCon1.Rmd](../scripts/bulk/knockdown/Liver_siSLC_bulk_DESeq2_nosiCon1.Rmd) | `bulk_counts`, `bulk_tpm` | — |  |
| `bulk_additional` | [Liver_siSLC_bulk_DESeq2_additional.Rmd](../scripts/bulk/knockdown/additional/Liver_siSLC_bulk_DESeq2_additional.Rmd) | `bulk_additional_genes`, `bulk_additional_transcripts` | — |  |
| `nfkb_shared` | [Supplementary_Figure_S3_shared_NFKB_targets.Rmd](../scripts/bulk/knockdown/Supplementary_Figure_S3_shared_NFKB_targets.Rmd) | `bulk_tpm`, `bulk_nosi_lps_deg`, `bulk_nosi_kd_deg`, `scrna_myeloid_deg` | `scrna_myeloid_gsea` | bulk_nosi, figure1 |
| `hyu_validation` | [HYU_independent_bulk_validation.Rmd](../scripts/bulk/hyu/HYU_independent_bulk_validation.Rmd) | `hyu_metadata`, `hyu_fpkm`, `hyu_candidate_kd`, `hyu_candidate_lps` | — |  |
| `hyu_fibrosis` | [HYU_SLC7A5_fibrosis_expression.Rmd](../scripts/bulk/hyu/HYU_SLC7A5_fibrosis_expression.Rmd) | `hyu_metadata`, `hyu_fpkm` | — |  |
| `monomac_table` | [make_suppl_table.py](../scripts/utils/make_suppl_table.py) | `monomac_marker_deg` | — |  |
| `hwangbj` | [HwangBJ_analysis.ipynb](../scripts/hwangbj/HwangBJ_analysis.ipynb) | `hwangbj_liver_nuclei_counts`, `hwangbj_liver_nuclei_metadata`, `hwangbj_pbmc_counts`, `hwangbj_pbmc_metadata`, `hwangbj_reference_mono5`, `hwangbj_reference_all`, `hwangbj_reference_classical` | `hwangbj_legacy_masl_myeloid` |  |

## 입력 파일

경로는 `data_root` 기준이다. `generated: true` 항목은 이번 저장소에서 생성한 결과를 우선 사용하며 입력별 override가 있으면 이를 따른다. pySCENIC 참조 4종은 Docker 단계를 새로 계산할 때만 필요하다.

| 입력 ID | 상대경로 | 설명 | 생성 결과 사용 | accession |
| --- | --- | --- | --- | --- |
| `scrna_monomac_seed` | `MASLD_collaboration/multiomics_analysis/scRNA_v1/scRNA_monoMAC_detail.h5ad` | Figure1 시작용 scRNA 세부 주석 객체 | 아니오 | 미확정 |
| `scrna_monomac` | `02_SLC7A5_mono_Journal/03_Script/Journal_script/scRNA_monoMAC_detail.h5ad` | Figure1 저장 객체 / Figure3-2 입력 | 예 | 미확정 |
| `scrna_mono_seed` | `MASLD_collaboration/multiomics_analysis/scRNA_v1/scRNA_adata_mono_cellannot.h5ad` | Figure2 시작용 단핵구 객체 | 아니오 | 미확정 |
| `scrna_mono_final` | `02_SLC7A5_mono_Journal/01_Data/scRNA_adata_mono_cellannot_final.h5ad` | Figure2 최종 단핵구 객체 | 예 | 미확정 |
| `scrna_raw` | `MASLD_collaboration/multiomics_analysis/scRNA_v1/scRNA_raw.h5ad` | CellPhoneDB 전체 raw counts | 아니오 | 미확정 |
| `snrna_stage` | `50_Public_GEO_analysis/analysis/Data/Liver_DB_nuc_stage.h5ad` | 질환 단계가 결합된 snRNA 객체 | 예 | 미확정 |
| `snrna_shared` | `external/MASLD_NUC_DB_total.h5ad` | Figure1_Nucseq의 외부 공유 snRNA 객체 | 아니오 | 미확정 |
| `snrna_gse210077` | `50_Public_GEO_analysis/analysis/01_MergeNucseq/GSE210077_Raw.h5ad` | GSE210077에서 만든 원본 AnnData | 아니오 | GSE210077 |
| `pbmc_annotated` | `02_SLC7A5_mono_Journal/01_Data/PBMC_v2_annotation.h5ad` | PBMC 주석 객체 | 아니오 | 미확정 |
| `cpdb_database` | `external/cellphonedb/v5.0.0/cellphonedb.zip` | CellPhoneDB v5 데이터베이스 | 아니오 | 미확정 |
| `scenic_adjacencies` | `02_SLC7A5_mono_Journal/02_Analysis/pySCENIC/data/cell_mono_SCENIC.adjacencies.tsv` | pySCENIC adjacencies | 예 | 미확정 |
| `scenic_motifs` | `02_SLC7A5_mono_Journal/02_Analysis/pySCENIC/data/cell_mono_SCENIC.motifs.csv` | pySCENIC motifs | 예 | 미확정 |
| `scenic_auc` | `02_SLC7A5_mono_Journal/02_Analysis/pySCENIC/data/cell_mono_SCENIC.auc.csv` | pySCENIC auc | 예 | 미확정 |
| `scenic_tfs` | `external/pyscenic/reference/allTFs_hg38.txt` | pySCENIC 외부 참조: allTFs_hg38.txt | 아니오 | 미확정 |
| `scenic_rankings_10kb` | `external/pyscenic/reference/hg38_10kbp_up_10kbp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather` | pySCENIC 외부 참조: hg38_10kbp_up_10kbp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather | 아니오 | 미확정 |
| `scenic_rankings_500bp` | `external/pyscenic/reference/hg38_500bp_up_100bp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather` | pySCENIC 외부 참조: hg38_500bp_up_100bp_down_full_tx_v10_clust.genes_vs_motifs.rankings.feather | 아니오 | 미확정 |
| `scenic_annotations` | `external/pyscenic/reference/motifs-v9-nr.hgnc-m0.001-o0.0.tbl` | pySCENIC 외부 참조: motifs-v9-nr.hgnc-m0.001-o0.0.tbl | 아니오 | 미확정 |
| `bulk_counts` | `02_SLC7A5_mono_Journal/04_bulkRNAseq/salmon.merged.gene_counts_length_scaled.tsv` | Salmon length-scaled gene counts | 아니오 | 미확정 |
| `bulk_tpm` | `02_SLC7A5_mono_Journal/04_bulkRNAseq/salmon.merged.gene_tpm.tsv` | Salmon gene TPM | 아니오 | 미확정 |
| `bulk_additional_genes` | `02_SLC7A5_mono_Journal/04_bulkRNAseq/additional/genes.expression.xlsx` | 추가 gene expression 입력 | 아니오 | 미확정 |
| `bulk_additional_transcripts` | `02_SLC7A5_mono_Journal/04_bulkRNAseq/additional/transcripts.expression.xlsx` | 추가 transcript expression 입력 | 아니오 | 미확정 |
| `bulk_nosi_lps_deg` | `02_SLC7A5_mono_Journal/04_bulkRNAseq/DEG_siConLPS_vs_siCon_nosiCon1.csv` | siCon_1 제외 LPS DEG | 예 | 미확정 |
| `bulk_nosi_kd_deg` | `02_SLC7A5_mono_Journal/04_bulkRNAseq/DEG_siSLCLPS5_vs_siConLPS_nosiCon1.csv` | siCon_1 제외 KD DEG | 예 | 미확정 |
| `scrna_myeloid_deg` | `02_SLC7A5_mono_Journal/02_Analysis/Fig1E_SLC7A5_top20_bottom20_DEG_GSEA/DEG_Myeloid_SLC7A5_top20_high_vs_bottom20_low.csv` | Figure1 Myeloid 상/하위 20% DEG | 예 | 미확정 |
| `scrna_myeloid_gsea` | `02_SLC7A5_mono_Journal/02_Analysis/Fig1E_Myeloid_SLC7A5_top20_bottom20_GSEA/GSEA_Myeloid_focused_best_terms_for_pdf.csv` | 선택적 NF-kB leading-edge 자료 | 예 | 미확정 |
| `hyu_metadata` | `03_bulkRNAseq/01_Data/HYU_bulk_meta.csv` | HYU 비식별 분석 metadata; 공개 범위 확인 필요 | 아니오 | 미확정 |
| `hyu_fpkm` | `03_bulkRNAseq/01_Data/HYU_FPKM.xlsx` | HYU FPKM 입력; 접근 조건 확인 필요 | 아니오 | 미확정 |
| `hyu_candidate_lps` | `03_bulkRNAseq/04_Script/DEG_siConLPS_vs_siCon.csv` | HYU 후보 선택에 실제 사용된 기존 LPS DEG | 아니오 | 미확정 |
| `hyu_candidate_kd` | `03_bulkRNAseq/04_Script/DEG_siSLCLPS5_vs_siConLPS.csv` | HYU 후보 선택에 실제 사용된 기존 KD DEG | 아니오 | 미확정 |
| `monomac_marker_deg` | `02_SLC7A5_mono_Journal/05_Figure/monomacDEG/scRNA_monomac_monocluster_DEG.csv` | 보조 marker 표 입력 | 아니오 | 미확정 |
| `hwangbj_liver_nuclei_counts` | `50_Public_GEO_analysis/HwangBJ/liver_nuclei_counts_matrix.rds` | HwangBJ liver_nuclei counts; donor IDs and Condition retained | 아니오 | 미확정 |
| `hwangbj_liver_nuclei_metadata` | `50_Public_GEO_analysis/HwangBJ/liver_nuclei_metadata.rds` | HwangBJ liver_nuclei metadata; donor IDs and Condition retained | 아니오 | 미확정 |
| `hwangbj_pbmc_counts` | `50_Public_GEO_analysis/HwangBJ/pbmc_counts_matrix.rds` | HwangBJ pbmc counts; donor IDs and Condition retained | 아니오 | 미확정 |
| `hwangbj_pbmc_metadata` | `50_Public_GEO_analysis/HwangBJ/pbmc_metadata.rds` | HwangBJ pbmc metadata; donor IDs and Condition retained | 아니오 | 미확정 |
| `hwangbj_reference_mono5` | `02_SLC7A5_mono_Journal/01_Data/scmono5_DEG.csv` | Primary scRNA SLC7A5-high vs rest reference DEG | 아니오 | 미확정 |
| `hwangbj_reference_all` | `02_SLC7A5_mono_Journal/02_Analysis/MASLD_mono_DEG_allclusters.csv` | Primary reference detection fractions and logFC cross-check | 아니오 | 미확정 |
| `hwangbj_reference_classical` | `02_SLC7A5_mono_Journal/05_Figure/DEG_Special_monocyte_vs_Classical_monocyte.csv` | Secondary scRNA SLC7A5-high vs Classical reference DEG | 아니오 | 미확정 |
| `hwangbj_legacy_masl_myeloid` | `02_SLC7A5_mono_Journal/02_Analysis/HwangBJ/pbmc/harmony/MASL1_4_myeloid_reference_annotated.h5ad` | Optional historical MASL-only annotation for barcode correspondence | 아니오 | 미확정 |

공개 다운로드 위치가 정해지지 않은 항목은 `config/inputs.json`의 `download_url`을 비워 두었다. 기존 로컬 파일의 존재는 외부 연구자가 다운로드할 수 있음을 의미하지 않는다.

HwangBJ RDS 구조는 노트북의 변환/로딩 셀에서 확인한다. 임상 stage는 donor ID에서 추정하지 않는다. [실행 안내](hwangbj.md)를 참고한다.
