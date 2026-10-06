**전체 스크립트 목록**

원본 74개 위치에서 고유 스크립트 75개를 정리했다. 원본 경로는 `Liver_bio_project/` 기준이며 저장소 경로는 이 `git/` 폴더 기준이다. 파일 수정일은 분석 실행일 또는 최종본 판정이 아니다.

주 분석 `scripts/` 16개는 복사 이후 경로/실행 준비를 보완했다. `supporting/` 11개와 `archive/` 43개는 초기 복사 상태의 참고 자료다. 원본 매핑은 초기 복사 이력이고 현재 복사본 해시는 [release_manifest.tsv](release_manifest.tsv)에 있다.

**scripts/**

| 정리된 파일 | 내용 | 원본 수정일 | 원본 위치 |
| --- | --- | --- | --- |
| [scripts/bulk/hyu/HYU_SLC7A5_fibrosis_expression.Rmd](../scripts/bulk/hyu/HYU_SLC7A5_fibrosis_expression.Rmd) | HYU bulk SLC7A5 발현과 질환/섬유화 단계의 연관성 | 2026-05-04 | `03_bulkRNAseq/04_Script/HYU_SLC7A5_fibrosis_expression.Rmd` |
| [scripts/bulk/hyu/HYU_independent_bulk_validation.Rmd](../scripts/bulk/hyu/HYU_independent_bulk_validation.Rmd) | siSLC7A5 KD 후보 유전자의 HYU 독립 bulk 코호트 검증·섬유화 연관성 | 2026-05-04 | `03_bulkRNAseq/04_Script/HYU_independent_bulk_validation.Rmd` |
| [scripts/bulk/knockdown/Liver_siSLC_bulk_DESeq2.Rmd](../scripts/bulk/knockdown/Liver_siSLC_bulk_DESeq2.Rmd) | siSLC7A5/LPS bulk DESeq2 기본 분석 | 2026-05-13 | `02_SLC7A5_mono_Journal/04_bulkRNAseq/Liver_siSLC_bulk_DESeq2.Rmd` |
| [scripts/bulk/knockdown/Liver_siSLC_bulk_DESeq2_nosiCon1.Rmd](../scripts/bulk/knockdown/Liver_siSLC_bulk_DESeq2_nosiCon1.Rmd) | siCon_1 제외 재분석; LPS 증가/KD 감소 유전자 교집합 | 2026-08-12 | `02_SLC7A5_mono_Journal/04_bulkRNAseq/Liver_siSLC_bulk_DESeq2_nosiCon1.Rmd` |
| [scripts/bulk/knockdown/Supplementary_Figure_S3_shared_NFKB_targets.Rmd](../scripts/bulk/knockdown/Supplementary_Figure_S3_shared_NFKB_targets.Rmd) | scRNA SLC7A5-high signature와 bulk LPS/KD의 공통 NFKB target 분석 | 2026-06-21 | `02_SLC7A5_mono_Journal/04_bulkRNAseq/Supplementary_Figure_S3_shared_NFKB_targets.Rmd` |
| [scripts/bulk/knockdown/additional/Liver_siSLC_bulk_DESeq2_additional.Rmd](../scripts/bulk/knockdown/additional/Liver_siSLC_bulk_DESeq2_additional.Rmd) | 추가 bulk 입력 자료 분석 | 2026-05-28 | `02_SLC7A5_mono_Journal/04_bulkRNAseq/additional/Liver_siSLC_bulk_DESeq2_additional.Rmd` |
| [scripts/pbmc/SLC_pbmc.ipynb](../scripts/pbmc/SLC_pbmc.ipynb) | PBMC 재클러스터링·단핵구 표지/시그니처 분석 | 2026-05-07 | `02_SLC7A5_mono_Journal/02_Analysis/pbmc/SLC_pbmc.ipynb` |
| [scripts/scrna/manuscript/Figure1.ipynb](../scripts/scrna/manuscript/Figure1.ipynb) | scRNA 전체 세포/골수계 구성, SLC7A5 발현, 상·하위 20% DEG/GSEA, 분할 가능성 QC | 2026-08-18 | `02_SLC7A5_mono_Journal/03_Script/Journal_script/Figure1.ipynb` |
| [scripts/scrna/manuscript/Figure2.ipynb](../scripts/scrna/manuscript/Figure2.ipynb) | Monocyte/Macrophage 세부 주석; Classical vs Special(SLC7A5-high) 비교·GSEA | 2026-06-22 | `02_SLC7A5_mono_Journal/03_Script/Journal_script/Figure2.ipynb` |
| [scripts/scrna/manuscript/Figure3-1.ipynb](../scripts/scrna/manuscript/Figure3-1.ipynb) | pySCENIC: Classical/Special monocyte TF·regulon·AUC·target 분석 | 2026-05-10 | `02_SLC7A5_mono_Journal/03_Script/Journal_script/Figure3-1.ipynb` |
| [scripts/scrna/manuscript/Figure3-2.ipynb](../scripts/scrna/manuscript/Figure3-2.ipynb) | CellPhoneDB method3: Special_monocyte의 Healthy/MASLD 세포 간 상호작용 | 2026-04-23 | `02_SLC7A5_mono_Journal/03_Script/Journal_script/Figure3-2.ipynb` |
| [scripts/scrna/manuscript/Figure3-3.ipynb](../scripts/scrna/manuscript/Figure3-3.ipynb) | TLR4/TNF receptor 발현 및 TNF-NFKB·mTORC1·MyD88 경로 점수 | 2026-05-13 | `02_SLC7A5_mono_Journal/03_Script/Journal_script/Figure3-3.ipynb` |
| [scripts/scrna/manuscript/Suppl_Figure2_analysis.ipynb](../scripts/scrna/manuscript/Suppl_Figure2_analysis.ipynb) | SLC7A5/CCR2/CD14/FCGR3A 및 염증 마커 보조 비교 | 2026-05-11 | `02_SLC7A5_mono_Journal/03_Script/Journal_script/Suppl_Figure2_analysis.ipynb` |
| [scripts/snrna/gsea/Nucseq_GSEA_SLC7A5Fig1.ipynb](../scripts/snrna/gsea/Nucseq_GSEA_SLC7A5Fig1.ipynb) | snRNA 세포 유형별 SLC7A5 양성/음성 DEG·GSEA | 2026-04-13 | `04_Nucseq_analysis/03_script/Nucseq_GSEA_SLC7A5Fig1.ipynb` |
| [scripts/snrna/manuscript/Figure1_Nucseq.ipynb](../scripts/snrna/manuscript/Figure1_Nucseq.ipynb) | snRNA SLC7A5 발현, Macrophage 상·하위 20% DEG/GSEA, 대사·영양결핍 GSEA/ORA | 2026-07-21 | `02_SLC7A5_mono_Journal/03_Script/Journal_script/Figure1_Nucseq.ipynb` |
| [scripts/utils/make_suppl_table.py](../scripts/utils/make_suppl_table.py) | Monocyte/Macrophage DEG 보조 Excel table 생성 | 2026-04-08 | `02_SLC7A5_mono_Journal/05_Figure/monomacDEG/make_suppl_table.py` |

**supporting/**

| 정리된 파일 | 내용 | 원본 수정일 | 원본 위치 |
| --- | --- | --- | --- |
| [supporting/bulk/hyu/Liver_HYU_bulkanalysis.Rmd](../supporting/bulk/hyu/Liver_HYU_bulkanalysis.Rmd) | HYU bulk 데이터 공통 분석/준비 | 2026-02-27 | `03_bulkRNAseq/04_Script/Liver_HYU_bulkanalysis.Rmd` |
| [supporting/cross_modality/Bulk_vs_NucSeq_overlap_analysis.ipynb](../supporting/cross_modality/Bulk_vs_NucSeq_overlap_analysis.ipynb) | bulk/snRNA 유전자 중첩 보조 분석 | 2026-03-26 | `04_Nucseq_analysis/03_script/Bulk_vs_NucSeq_overlap_analysis.ipynb` |
| [supporting/snrna/age/Liver_Nucseq_age_bin_analysis.ipynb](../supporting/snrna/age/Liver_Nucseq_age_bin_analysis.ipynb) | 연령 구간별 분석 안에 SLC7A5 지정 유전자 발현/상관분석 포함 | 2026-03-26 | `04_Nucseq_analysis/03_script/Liver_Nucseq_age_bin_analysis.ipynb` |
| [supporting/snrna/age/NucSeq_Fisher_Z_age_correlation_comparison.ipynb](../supporting/snrna/age/NucSeq_Fisher_Z_age_correlation_comparison.ipynb) | Healthy/MASLD 세포 유형별 연령 상관 비교 | 2026-03-26 | `04_Nucseq_analysis/03_script/NucSeq_Fisher_Z_age_correlation_comparison.ipynb` |
| [supporting/snrna/integration/inhouse/Liver_MASLD_integrated_analysis.ipynb](../supporting/snrna/integration/inhouse/Liver_MASLD_integrated_analysis.ipynb) | 공개/자체 snRNA 통합, SLC7A5 및 myeloid 관련 분석 | 2026-03-03 | `04_Nucseq_analysis/03_script/Liver_MASLD_integrated_analysis.ipynb` |
| [supporting/snrna/integration/public_geo/01_SCVI_ref_cellannnotation.ipynb](../supporting/snrna/integration/public_geo/01_SCVI_ref_cellannnotation.ipynb) | 공개 snRNA reference 세포 유형 주석 | 2025-12-16 | `50_Public_GEO_analysis/analysis/01_MergeNucseq/01_SCVI_ref_cellannnotation.ipynb` |
| [supporting/snrna/integration/public_geo/Liver_Bio_Nucseq_analysis_0121.ipynb](../supporting/snrna/integration/public_geo/Liver_Bio_Nucseq_analysis_0121.ipynb) | 공개/자체 snRNA 통합, monocyte subset·질환 단계·SLC7A5 분석 | 2026-07-13 | `50_Public_GEO_analysis/analysis/Liver_Bio_Nucseq_analysis_0121.ipynb` |
| [supporting/snrna/integration/public_geo/Liver_MASLD_integrated_analysis.ipynb](../supporting/snrna/integration/public_geo/Liver_MASLD_integrated_analysis.ipynb) | 공개/자체 snRNA 통합 및 SLC7A5/myeloid 탐색 | 2026-02-24 | `50_Public_GEO_analysis/analysis/Liver_MASLD_integrated_analysis.ipynb` |
| [supporting/snrna/other_celltypes/Liver_bio_Nucseq_Hepatocyte.ipynb](../supporting/snrna/other_celltypes/Liver_bio_Nucseq_Hepatocyte.ipynb) | 다른 세포 유형: Hepatocyte SLC7A5 발현 탐색 | 2026-01-08 | `50_Public_GEO_analysis/analysis/Liver_bio_Nucseq_Hepatocyte.ipynb` |
| [supporting/snrna/other_celltypes/Nuc_stellete.ipynb](../supporting/snrna/other_celltypes/Nuc_stellete.ipynb) | 다른 세포 유형: Stellate SLC7A5 발현 탐색 | 2026-01-06 | `50_Public_GEO_analysis/analysis/Nuc_stellete.ipynb` |
| [supporting/spatial/Spatial_1.ipynb](../supporting/spatial/Spatial_1.ipynb) | 범위 밖 보조: 공간전사체에서 SLC7A5 발현 확인 | 2025-08-28 | `MASLD_collaboration/Spatial_data/Spatial_1.ipynb` |

**archive/**

| 정리된 파일 | 내용 | 원본 수정일 | 원본 위치 |
| --- | --- | --- | --- |
| [archive/bulk/knockdown/Liver_siSLC7A5_bulkanalysis.Rmd](../archive/bulk/knockdown/Liver_siSLC7A5_bulkanalysis.Rmd) | 기존 siSLC7A5 bulk 탐색·발현 분석 | 2026-02-27 | `02_SLC7A5_mono_Journal/04_bulkRNAseq/Liver_siSLC7A5_bulkanalysis.Rmd` |
| [archive/bulk/knockdown/bulk_DESeq2.Rmd](../archive/bulk/knockdown/bulk_DESeq2.Rmd) | 기존 DESeq2 분석본; 03_bulkRNAseq 내 두 파일과 소스 동일 | 2026-03-03 | `02_SLC7A5_mono_Journal/04_bulkRNAseq/bulk_DESeq2.Rmd`<br>`03_bulkRNAseq/04_Script/Liver_siSLC_bulk_DESeq2.Rmd`<br>`03_bulkRNAseq/04_Script/bulk_DESeq2.Rmd` |
| [archive/cellchat/cellchat_reanalysis_step3.Rmd](../archive/cellchat/cellchat_reanalysis_step3.Rmd) | LSEC/혈소판/Monocyte CellChat 연관 작업 | 2025-07-14 | `MASLD_collaboration/analysis_notbook/cellchat_analysis/SJLee_work/cellchat_reanalysis_step3.Rmd` |
| [archive/initial_clustering/Cell_clustering.ipynb](../archive/initial_clustering/Cell_clustering.ipynb) | 초기 패키지 import만 있는 작업 초안 | 2025-11-21 | `02_SLC7A5_mono_Journal/SL7A5_monocyte_Journal/Script/Cell_clustering.ipynb` |
| [archive/initial_clustering/Nuc_clustering.ipynb](../archive/initial_clustering/Nuc_clustering.ipynb) | 이전 분석/탐색 작업본 | 2025-11-26 | `02_SLC7A5_mono_Journal/SL7A5_monocyte_Journal/Script/Nuc_clustering.ipynb` |
| [archive/journal/Cell_SLC7A5_mono_analysis02.ipynb](../archive/journal/Cell_SLC7A5_mono_analysis02.ipynb) | 이전 분석/탐색 작업본 | 2026-04-02 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/Cell_SLC7A5_mono_analysis02.ipynb` |
| [archive/journal/Cell_clustering.ipynb](../archive/journal/Cell_clustering.ipynb) | 이전 분석/탐색 작업본 | 2025-11-26 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/Cell_clustering.ipynb` |
| [archive/journal/Figure1E_Hallmark_GSEA_from_Figure1.ipynb](../archive/journal/Figure1E_Hallmark_GSEA_from_Figure1.ipynb) | 이전 분석/탐색 작업본 | 2026-05-29 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/Figure1E_Hallmark_GSEA_from_Figure1.ipynb` |
| [archive/journal/Figure1_Nucseq_SLC7A5_pos_neg_analysis.ipynb](../archive/journal/Figure1_Nucseq_SLC7A5_pos_neg_analysis.ipynb) | 이전 분석/탐색 작업본 | 2026-05-29 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/Figure1_Nucseq_SLC7A5_pos_neg_analysis.ipynb` |
| [archive/journal/LAT1_pathway.ipynb](../archive/journal/LAT1_pathway.ipynb) | 이전 분석/탐색 작업본 | 2026-02-16 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/LAT1_pathway.ipynb` |
| [archive/journal/Nuc_clustering.ipynb](../archive/journal/Nuc_clustering.ipynb) | 이전 분석/탐색 작업본 | 2025-11-25 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/Nuc_clustering.ipynb` |
| [archive/journal/Nuc_monoMAC_analysis.ipynb](../archive/journal/Nuc_monoMAC_analysis.ipynb) | 이전 분석/탐색 작업본 | 2026-01-06 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/Nuc_monoMAC_analysis.ipynb` |
| [archive/journal/Nucseq_preprocessing.ipynb](../archive/journal/Nucseq_preprocessing.ipynb) | 이전 분석/탐색 작업본 | 2025-11-25 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/Nucseq_preprocessing.ipynb` |
| [archive/journal/cellseq_cellphoneDB.ipynb](../archive/journal/cellseq_cellphoneDB.ipynb) | 이전 분석/탐색 작업본 | 2026-04-13 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/cellseq_cellphoneDB.ipynb` |
| [archive/journal/cellseq_cellphoneDB_method3_percell.ipynb](../archive/journal/cellseq_cellphoneDB_method3_percell.ipynb) | 이전 분석/탐색 작업본 | 2026-04-10 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/cellseq_cellphoneDB_method3_percell.ipynb` |
| [archive/journal/journal_SLC7A5_scrna_script_001.ipynb](../archive/journal/journal_SLC7A5_scrna_script_001.ipynb) | 이전 분석/탐색 작업본 | 2026-04-03 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/journal_SLC7A5_scrna_script_001.ipynb` |
| [archive/journal/scRNA_analysis-01.ipynb](../archive/journal/scRNA_analysis-01.ipynb) | 이전 분석/탐색 작업본 | 2026-04-08 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/scRNA_analysis-01.ipynb` |
| [archive/journal/scRNA_analysis-02.ipynb](../archive/journal/scRNA_analysis-02.ipynb) | 이전 분석/탐색 작업본 | 2026-04-02 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/scRNA_analysis-02.ipynb` |
| [archive/journal/scRNA_analysis-03.ipynb](../archive/journal/scRNA_analysis-03.ipynb) | 이전 분석/탐색 작업본 | 2026-03-19 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/scRNA_analysis-03.ipynb` |
| [archive/journal/scRNA_analysis-04.ipynb](../archive/journal/scRNA_analysis-04.ipynb) | 이전 분석/탐색 작업본 | 2026-03-30 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/scRNA_analysis-04.ipynb` |
| [archive/journal/scRNA_analysis_merged.ipynb](../archive/journal/scRNA_analysis_merged.ipynb) | 이전 분석/탐색 작업본 | 2026-03-30 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/scRNA_analysis_merged.ipynb` |
| [archive/journal/scRNA_mono_analysis.ipynb](../archive/journal/scRNA_mono_analysis.ipynb) | 이전 분석/탐색 작업본 | 2026-01-13 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/scRNA_mono_analysis.ipynb` |
| [archive/journal/scRNA_mono_analysis_v260114.ipynb](../archive/journal/scRNA_mono_analysis_v260114.ipynb) | 이전 분석/탐색 작업본 | 2026-05-29 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/scRNA_mono_analysis_v260114.ipynb` |
| [archive/journal/scRNA_pipeline.ipynb](../archive/journal/scRNA_pipeline.ipynb) | 이전 분석/탐색 작업본 | 2026-03-03 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/scRNA_pipeline.ipynb` |
| [archive/journal/scRNA_stellete_analysis01.ipynb](../archive/journal/scRNA_stellete_analysis01.ipynb) | 이전 분석/탐색 작업본 | 2026-03-16 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/scRNA_stellete_analysis01.ipynb` |
| [archive/journal/siSLC7A5_bulk_deconv.ipynb](../archive/journal/siSLC7A5_bulk_deconv.ipynb) | scRNA 단핵구 참조와 bulk TPM을 이용한 deconvolution 작업본 | 2026-02-12 | `02_SLC7A5_mono_Journal/03_Script/99_Archive/siSLC7A5_bulk_deconv.ipynb` |
| [archive/multiomics/main/MASLD_multiomics_analysis_merging.ipynb](../archive/multiomics/main/MASLD_multiomics_analysis_merging.ipynb) | 이전 분석/탐색 작업본 | 2025-10-27 | `MASLD_collaboration/multiomics_analysis/analysis_script/MASLD_multiomics_analysis_merging.ipynb` |
| [archive/multiomics/main/multiomics_macrophage_analysis.ipynb](../archive/multiomics/main/multiomics_macrophage_analysis.ipynb) | 기존 macrophage 다중 데이터 분석·SLC7A5 | 2025-10-28 | `MASLD_collaboration/multiomics_analysis/analysis_script/multiomics_macrophage_analysis.ipynb` |
| [archive/multiomics/mp_analysis/MASLD_multi_analysis.ipynb](../archive/multiomics/mp_analysis/MASLD_multi_analysis.ipynb) | 이전 분석/탐색 작업본 | 2025-07-15 | `MASLD_collaboration/MP_analysis/multiomics_analysis/MASLD_multi_analysis.ipynb` |
| [archive/multiomics/mp_analysis/analysis_script/MASLD_multiomics_analysis.ipynb](../archive/multiomics/mp_analysis/analysis_script/MASLD_multiomics_analysis.ipynb) | 이전 분석/탐색 작업본 | 2026-08-18 | `MASLD_collaboration/MP_analysis/multiomics_analysis/analysis_script/MASLD_multiomics_analysis.ipynb` |
| [archive/multiomics/mp_analysis/analysis_script/multiomics_macrophage_analysis.ipynb](../archive/multiomics/mp_analysis/analysis_script/multiomics_macrophage_analysis.ipynb) | MP_analysis 내 macrophage 다중 데이터 작업본 | 2025-07-17 | `MASLD_collaboration/MP_analysis/multiomics_analysis/analysis_script/multiomics_macrophage_analysis.ipynb` |
| [archive/multiomics/mp_analysis/celltypist.ipynb](../archive/multiomics/mp_analysis/celltypist.ipynb) | 이전 분석/탐색 작업본 | 2025-08-12 | `MASLD_collaboration/MP_analysis/multiomics_analysis/celltypist.ipynb` |
| [archive/reference_templates/bulkRNAseq_pipeline.Rmd](../archive/reference_templates/bulkRNAseq_pipeline.Rmd) | 원 폴더에 함께 보관된 mouse lung/spleen bulk 참고 코드; SLC7A5 논문 주 분석과 구분 | 2026-04-02 | `02_SLC7A5_mono_Journal/04_bulkRNAseq/bulkRNAseq_pipeline.Rmd` |
| [archive/scrna/MASLD_monoMAC_Cellchat.Rmd](../archive/scrna/MASLD_monoMAC_Cellchat.Rmd) | Monocyte/Macrophage CellChat 분석 | 2025-09-10 | `MASLD_collaboration/multiomics_analysis/scRNA_v1/MASLD_monoMAC_Cellchat.Rmd` |
| [archive/scrna/SLC7A5_scanalysis.ipynb](../archive/scrna/SLC7A5_scanalysis.ipynb) | 기존 scRNA SLC7A5 발현/양성·음성 탐색 | 2025-10-28 | `MASLD_collaboration/multiomics_analysis/scRNA_v1/SLC7A5_scanalysis.ipynb` |
| [archive/scrna/preprocessing/sc_MASLD_analysis.ipynb](../archive/scrna/preprocessing/sc_MASLD_analysis.ipynb) | 이전 분석/탐색 작업본 | 2025-07-25 | `MASLD_collaboration/analysis_notbook/nuc_big_analysis/sc_MASLD_analysis.ipynb` |
| [archive/scrna/reference/scRNAseq_Liver_Nature_2019.Rmd](../archive/scrna/reference/scRNAseq_Liver_Nature_2019.Rmd) | 기존 scRNA 단핵구·SLC7A5 분석 R 코드(3개 위치에 동일 소스) | 2025-11-20 | `Cellseq/scRNAseq_Liver_Nature_2019.Rmd`<br>`MASLD_collaboration/MP_analysis/MP_MASLD_paper/scripts/scRNAseq_Liver_Nature_2019.Rmd`<br>`MASLD_collaboration/pre_work/pre_work/scRNAseq_Liver_Nature_2019.Rmd` |
| [archive/scrna/scRNA_mono_analysis.ipynb](../archive/scrna/scRNA_mono_analysis.ipynb) | 기존 scRNA 단핵구 subcluster·SLC7A5·DEG·경로 분석 | 2025-12-02 | `MASLD_collaboration/multiomics_analysis/scRNA_v1/scRNA_mono_analysis.ipynb` |
| [archive/snrna/MASLD_nuc_MP.Rmd](../archive/snrna/MASLD_nuc_MP.Rmd) | 기존 snRNA MP/대식세포 SLC7A5 발현 분석 | 2025-05-28 | `MASLD_collaboration/MASLD_nuc_MP.Rmd` |
| [archive/snrna/Untitled.ipynb](../archive/snrna/Untitled.ipynb) | 기존 snRNA 탐색 노트북; 원래 파일명 보존 | 2026-03-30 | `MASLD_collaboration/multiomics_analysis/snRNA_v1/Untitled.ipynb` |
| [archive/snrna/preprocessing/MASLD_nucseq_analysis.ipynb](../archive/snrna/preprocessing/MASLD_nucseq_analysis.ipynb) | 기존 snRNA myeloid subset 및 SLC7A5 탐색 | 2025-07-16 | `MASLD_collaboration/analysis_notbook/script/MASLD_nucseq_analysis.ipynb` |
| [archive/snrna/preprocessing/Nucseq_prefiltering.ipynb](../archive/snrna/preprocessing/Nucseq_prefiltering.ipynb) | 이전 분석/탐색 작업본 | 2025-08-13 | `MASLD_collaboration/analysis_notbook/script/Nucseq_prefiltering.ipynb` |
| [archive/snrna/sn_MASLD_mono.ipynb](../archive/snrna/sn_MASLD_mono.ipynb) | 기존 snRNA 단핵구/SLC7A5 분석 | 2025-08-14 | `MASLD_collaboration/MP_analysis/sn_analysis/sn_MASLD_mono.ipynb` |

**범위와 제외 항목**

scRNA/snRNA/bulk의 Monocyte·SLC7A5 관련 코드와 기존 관련 작업을 포함했다. 공간전사체/다른 세포 유형은 `supporting/`, 이전 초안·참고 템플릿은 `archive/`에 두었다. Jupyter 자동저장본, 데이터 객체, DEG/결과 표, 그림은 복사하지 않았다.

| 복사하지 않은 다른 주제 코드 | 이유 |
| --- | --- |
| `05_LSEC_Journal/03_Script/scRNA_Endo.ipynb` | LSEC 분석: 공통 입력/단핵구 표지 언급에 해당 |
| `99_Archive/Script/KLHL11_analysis.ipynb` | 실제 분석 대상은 KLHL11이며 SLC7A5 주석/경로만 재사용 |

**내용이 동일한 원본의 통합**

| 복사본 | 동일한 원본 위치 수 |
| --- | --- |
| [archive/bulk/knockdown/bulk_DESeq2.Rmd](../archive/bulk/knockdown/bulk_DESeq2.Rmd) | 3 |
| [archive/scrna/reference/scRNAseq_Liver_Nature_2019.Rmd](../archive/scrna/reference/scRNAseq_Liver_Nature_2019.Rmd) | 3 |

전체 원본의 SHA-256, 복사본 해시, 코드 내용 해시, 복사 방법은 [source_manifest.tsv](source_manifest.tsv)에 기록했다. `.Rmd`/`.py`는 바이트가 같은 복사본이다. `.ipynb`는 코드/Markdown 셀의 타입·순서·source를 그대로 두고 출력·실행 횟수·실행 메타데이터를 비웠다.

## 2026-10-06 추가/갱신

| 정리된 파일 | 내용 | 원본 |
| --- | --- | --- |
| [Figure2.ipynb](../scripts/scrna/manuscript/Figure2.ipynb) | donor별 permutation Mann–Whitney U + BH 구성 비교 | Journal_script/Figure2.ipynb |
| [HwangBJ_analysis.ipynb](../scripts/hwangbj/HwangBJ_analysis.ipynb) | HwangBJ 주 분석 또는 실행 보조 | Journal_script/HwangBJ_analysis.ipynb |
| [HwangBJ_export_counts.R](../scripts/hwangbj/HwangBJ_export_counts.R) | HwangBJ 주 분석 또는 실행 보조 | Journal_script/HwangBJ_export_counts.R |
| [HwangBJ_condition_analysis.py](../scripts/hwangbj/HwangBJ_condition_analysis.py) | HwangBJ 주 분석 또는 실행 보조 | Journal_script/HwangBJ_condition_analysis.py |
| [HwangBJ_build_report.py](../scripts/hwangbj/HwangBJ_build_report.py) | HwangBJ 주 분석 또는 실행 보조 | Journal_script/HwangBJ_build_report.py |
| [HwangBJ_stage_analysis.py](../supporting/hwangbj/HwangBJ_stage_analysis.py) | 과거 stage 탐색 보조; 현재 노트북에서 미사용 | Journal_script/HwangBJ_stage_analysis.py |
