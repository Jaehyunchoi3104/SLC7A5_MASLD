# SLC7A5-high Monocyte in MASLD — Analysis code

MASLD의 SLC7A5-high Monocyte 관련 scRNA-seq, snRNA-seq, PBMC, siSLC7A5 knockdown bulk RNA-seq 및 HYU 코호트 분석 코드다. HwangBJ 간 핵/PBMC donor Harmony 및 MASL–MASH 비교도 포함한다.

주 분석 **17개**는 입력 경로를 공통 설정으로 분리하고, 새 결과가 이 저장소의 `results/`에 저장되도록 보완했다. 저장소 밖 원본은 수정하지 않았다. 정리된 스크립트 75개는 주 분석 17개, HwangBJ 실행 보조 코드 3개, 보조 참고 12개, 과거 참고 43개다.

## 빠른 시작

아래 명령은 이 `git/` 폴더를 현재 작업 디렉터리로 사용한다.

1. [환경 안내](docs/dependencies.md)에 따라 Python 또는 R 환경을 준비한다. Python 설치 후보 파일은 `environment/python.yml`, R 패키지 목록은 `environment/r-packages.tsv`다. 아직 전체 분석으로 검증한 환경 잠금 파일은 아니다.
2. `config/paths.local.json`에서 데이터 루트와 입력별 위치를 설정한다. 현재 작업 컴퓨터의 기존 데이터 위치는 이 로컬 설정에 연결해 두었으며, 이 파일은 Git에 포함되지 않는다. 다른 컴퓨터에서는 [입력 안내](docs/data_requirements.md)를 따라 새로 만든다.
3. 실행할 분석의 입력을 점검한다.

```bash
python tools/check_inputs.py --analysis figure1 --schema
python tools/check_environment.py
```

4. Python 분석은 저장소 안의 노트북을 열어 첫 설정 셀부터 실행한다. R 분석은 다음 도구로 실행하면 HTML과 중간 파일도 `results/`에 저장한다.

```bash
jupyter lab
Rscript tools/check_r_packages.R
Rscript tools/render_rmd.R bulk_nosi
```

보조 표 생성은 `python scripts/utils/make_suppl_table.py`로 실행한다. 전체 노트북은 전처리된 AnnData/기존 결과를 시작점으로 사용하며, FASTQ부터 모든 Figure를 자동 생성하는 단일 파이프라인은 아니다. pySCENIC은 아래 실행 순서를 참고한다.

## 분석과 실행 순서

| 분석 ID | 내용 | 시작 코드 |
| --- | --- | --- |
| `figure1` | scRNA 구성, SLC7A5 상/하위 20% DEG/GSEA | [Figure1](scripts/scrna/manuscript/Figure1.ipynb) |
| `figure2` | Classical/SLC7A5-high Monocyte | [Figure2](scripts/scrna/manuscript/Figure2.ipynb) |
| `figure3_regulons` | TF/regulon/AUC | [Figure3-1](scripts/scrna/manuscript/Figure3-1.ipynb) |
| `figure3_cellphone` | CellPhoneDB | [Figure3-2](scripts/scrna/manuscript/Figure3-2.ipynb) |
| `figure3_signaling` | TLR4/TNF/NFKB/mTORC1 score | [Figure3-3](scripts/scrna/manuscript/Figure3-3.ipynb) |
| `suppl_figure2` | 단핵구 표지/염증 유전자 | [Supplementary Figure2](scripts/scrna/manuscript/Suppl_Figure2_analysis.ipynb) |
| `figure1_nucseq` | snRNA SLC7A5 검증 | [Figure1_Nucseq](scripts/snrna/manuscript/Figure1_Nucseq.ipynb) |
| `nucseq_gsea` | snRNA SLC7A5 양성/음성 GSEA | [Nucseq_GSEA](scripts/snrna/gsea/Nucseq_GSEA_SLC7A5Fig1.ipynb) |
| `pbmc` | PBMC 단핵구 | [SLC_pbmc](scripts/pbmc/SLC_pbmc.ipynb) |
| `hwangbj` | 간 핵 MASL1–4 및 PBMC MASL/MASH donor Harmony·참조 주석·donor 비교 | [HwangBJ_analysis](scripts/hwangbj/HwangBJ_analysis.ipynb) |
| `bulk_full` | siSLC7A5/LPS 전체 샘플 | [DESeq2](scripts/bulk/knockdown/Liver_siSLC_bulk_DESeq2.Rmd) |
| `bulk_nosi` | siCon_1 제외 | [DESeq2_nosiCon1](scripts/bulk/knockdown/Liver_siSLC_bulk_DESeq2_nosiCon1.Rmd) |
| `bulk_additional` | 추가 bulk 입력 | [DESeq2_additional](scripts/bulk/knockdown/additional/Liver_siSLC_bulk_DESeq2_additional.Rmd) |
| `nfkb_shared` | scRNA/bulk 공통 NF-kB target | [Supplementary Figure S3](scripts/bulk/knockdown/Supplementary_Figure_S3_shared_NFKB_targets.Rmd) |
| `hyu_validation` | HYU 독립 코호트 검증 | [HYU_validation](scripts/bulk/hyu/HYU_independent_bulk_validation.Rmd) |
| `hyu_fibrosis` | HYU 섬유화 연관성 | [HYU_fibrosis](scripts/bulk/hyu/HYU_SLC7A5_fibrosis_expression.Rmd) |
| `monomac_table` | 단핵구 marker 보조 표 | [make_suppl_table.py](scripts/utils/make_suppl_table.py) |

Figure1은 CellPhoneDB 입력과 Myeloid DEG를, Figure2는 후속 Monocyte 분석용 객체를 생성한다. Figure3-1/3-3/Supplementary Figure2는 Figure2 결과를 사용한다. 공통 NF-kB 분석에는 `bulk_nosi`와 Figure1 결과가 필요하다. 이미 생성된 동일 입력 스냅샷이 있으면 선행 분석 없이 해당 파일을 사용할 수 있다. HYU의 후보 유전자 입력은 기존 HYU 검증에 사용한 DEG 파일로 지정했으며 다른 bulk 결과로 자동 대체하지 않는다.

Figure3-1에서 pySCENIC을 새로 계산할 때는 loom export 셀까지 실행 → `bash scripts/external/pyscenic.sh grn` → `ctx` → `aucell` → 노트북 후속 셀 순서로 실행한다. 기존 adjacency/motif/AUC를 사용할 때는 Docker 단계를 생략할 수 있다. 참조 데이터 4종은 별도로 필요하다.

분석별 입력·선행 단계는 [analysis_inputs.md](docs/analysis_inputs.md)와 [analyses.json](config/analyses.json)에 있다.

**2026-10-06 통계/코호트 갱신:** Figure2 구성 비교는 donor별 exact permutation Mann–Whitney U와 9개 celltype BH 보정을 사용한다. 기존 pooled Fisher/미보정 P값 별표 셀은 donor별 표와 boxplot으로 대체했다. Healthy CD45 library를 donor별로 합치며 MASLD sample ID의 독립 donor 가정은 임상 metadata와 확인해야 한다. DEG 등의 cell-level 탐색 분석을 donor-level로 전부 변경한 것은 아니다.

HwangBJ는 간 핵 MASL 4명과 PBMC MASL 4명/MASH 4명을 별도로 처리한다. PBMC reference-matched cluster 주석 후 donor별 비율의 평균 차이를 70개 label permutation과 bootstrap CI로 비교한다. 상세 실행·주석 해석은 [HwangBJ 안내](docs/hwangbj.md)를 참고한다.

## 저장소 구조

```text
git/
├── scripts/           # 논문 주 분석 17개 + HwangBJ 보조 코드 + 외부 계산 도구
├── supporting/        # 보조 참고 코드 12개: 경로 보완 대상 아님
├── archive/           # 과거/참고 코드 43개: 경로 보완 대상 아님
├── config/            # 입력 목록, 경로 예시, 분석 목록, bulk 그룹 표
├── slc7a5_paths.py     # Python 입력/출력 경로
├── R/paths.R          # R 입력/출력 경로
├── tools/             # 입력·환경·문법 점검, R Markdown 실행
├── tests/             # 입력 보존·경로·샘플 매핑 검사
├── environment/       # 의존성 목록과 관측한 버전
├── docs/              # 원본 매핑, 변경 이력, 검증 범위
├── data/              # 외부 사용자가 준비하는 입력 위치; Git 제외
└── results/           # 새 결과/보고서; Git 제외
```

`data/`는 데이터가 제공될 때 사용하며 입력 파일은 저장소에 동봉하지 않았다. `supporting/`와 `archive/`에는 원래 개인 경로가 남아 있으므로 주 분석 실행 안내를 그대로 적용하지 않는다.

## 검증과 공개 준비 상태

[검증 기록](docs/validation.md): 주 분석 17개 및 HwangBJ 보조 코드 문법/포맷, Python 경로 테스트 10개, R 경로/샘플 매핑, 기존 입력 및 HwangBJ 신규 입력의 존재·일부 스키마, 실제 보조 Excel 표 생성, 최신 원본 79개 해시를 확인했다. 전체 Figure 재계산이나 논문 수치와의 일치는 아직 검증하지 않았다.

공개 전에 [입력 목록](config/inputs.json)의 미확정 accession/다운로드 위치를 채우고, 논문 최종 환경과 Figure 결과를 확인해야 한다. 논문 DOI·코드 라이선스·코드 보관 DOI는 현재 제공되지 않아 확정하지 않았다. 데이터 공개 파일과 접근 방법은 [데이터 안내](docs/data_requirements.md)를 기준으로 준비한다.

[전체 75개 스크립트](docs/script_index.md) · [초기 원본 매핑](docs/source_manifest.tsv) · [최신 원본 기록](docs/update_source_manifest.tsv) · [보완 후 해시](docs/release_manifest.tsv) · [변경 내역](docs/release_notes.md)

이 폴더는 로컬 준비본이다. 원격 저장소 생성이나 GitHub 업로드는 수행하지 않았다.
