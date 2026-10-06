# HwangBJ 분석 실행 안내

주 분석은 [HwangBJ_analysis.ipynb](../scripts/hwangbj/HwangBJ_analysis.ipynb)이며 분석 ID는 `hwangbj`다. 저장소 안에서 노트북을 열어 **첫 설정 셀부터 순서대로 실행**한다. 간 핵과 PBMC를 각각 분석하며 합쳐서 Harmony를 수행하지 않는다.

## 입력과 환경

- RDS 네 개: `hwangbj_liver_nuclei_counts`, `hwangbj_liver_nuclei_metadata`, `hwangbj_pbmc_counts`, `hwangbj_pbmc_metadata`. 각 counts/metadata 쌍은 같은 barcode를 가져야 한다. 개별 위치는 `config/paths.local.json`의 `input_overrides`로 지정할 수 있다.
- 참조 DEG 세 개: `hwangbj_reference_mono5` (primary vs rest), `hwangbj_reference_all` (검출률 및 효과값 확인), `hwangbj_reference_classical` (secondary vs Classical). 원본 분석에 사용한 동일 파일 스냅샷을 준비한다.
- `hwangbj_legacy_masl_myeloid`는 이전 MASL-only 주석과의 barcode 대응을 확인하는 **선택 입력**이다. 없으면 대응 단계만 생략한다.
- Scanpy, AnnData, NumPy, pandas, SciPy, matplotlib, seaborn, igraph와 **harmonypy 0.0.10**이 필요하다. 다른 Python 환경에서 harmonypy를 자동으로 가져오지 않는다. 패키지 목록은 `environment/requirements-python.txt`를 참고한다. 전체 새 환경 설치/lock 검증은 아직 수행하지 않았다.
- RDS sparse 변환에는 R의 **Matrix**와 Rscript가 필요하다. `Rscript`를 PATH에 넣거나 `SLC7A5_RSCRIPT`에 실행 파일을 지정한다. 변환 코드에는 네 입력 경로가 명시적으로 전달되므로 metadata와 counts의 위치가 달라도 된다.

```bash
python tools/check_inputs.py --analysis hwangbj --schema
# PATH에 Rscript가 없는 경우 실제 설치 위치로 지정:
export SLC7A5_RSCRIPT=/path/to/Rscript
jupyter lab
```

RDS의 barcode, donor 및 Condition 검증은 변환/로딩 셀에서 수행한다. `check_inputs.py --schema` 자체는 RDS를 읽어 생물학적 내용을 확인하지 않는다.

## 분석과 통계 단위

간 핵은 MASL1–4만 선택한다. PBMC는 MASL1–4와 MASH1–4를 모두 선택한다. donor ID의 숫자는 질환 stage가 아니다. 각 검체에서 QC → donor별 HVG → PCA → donor Harmony → neighbors/UMAP/Leiden을 수행하고, marker 기반 myeloid 후보를 분리한 뒤 myeloid에서 PCA/Harmony를 다시 실행한다. Harmony representation으로 이웃을 계산하며 raw UMI는 보존한다.

PBMC는 donor × cluster raw UMI pseudobulk의 cluster-vs-rest 효과를 donor별로 구한 후 동일 가중 평균한다. 이를 기존 scRNA SLC7A5-high DEG의 signed logFC와 Spearman correlation으로 비교한다. matching에서는 SLC7A5와 MT-/RPS/RPL 유전자를 제외한다. monocyte marker 지지가 있고 primary vs-rest 참조와 양의 상관이 가장 높은 cluster를 잠정적으로 `SLC7A5_high_monocyte`라 주석하며, MASL/MASH 빈도 차이를 보고 cluster를 선택하지 않는다.

질환군 비교의 관측 단위는 **독립 donor**다. donor별 high cluster / 전체 monocyte 비율을 MASL 4명과 MASH 4명 사이에서 비교한다. 평균 차이의 양측 exact label permutation (70개 배치)과 donor bootstrap 95% CI를 사용한다. 주 비교가 하나이므로 BH 보정을 적용하지 않는다. **Figure2의 donor-level Mann–Whitney U + 9개 celltype BH 보정과는 서로 다른 분석**이다.

원본 실행에서는 통합 PBMC cluster 1이 선택되었으나 primary 상관은 약 0.182이며 secondary vs-Classical 참조 최상위는 cluster 0이었다. 잠정적 참조 주석으로 해석한다. MASL 평균 33.32%, MASH 40.27%, 평균 차이 +6.95 percentage points, 95% CI −3.21~16.27, P=0.257로 유의한 증가를 확인하지 못했다. 이 숫자는 원본 실행 기록이며 이번 Git 사본의 전체 Harmony 재실행 결과는 아니다.

간 핵에서는 현재 marker 기준으로 monocyte 후보가 없어 high 정의 및 질환군 비교를 수행하지 않았다. 간 핵 MASH 분석은 이 노트북 범위에 포함하지 않는다. pseudobulk counts 저장이 DESeq2 기반 donor-level DEG 검정 수행을 뜻하지 않는다.

## 출력 및 보조 코드

출력과 sparse cache는 저장소 `results/02_SLC7A5_mono_Journal/` 아래에 기록한다.

- `02_Analysis/HwangBJ/liver_nuclei/harmony/`: 간 핵 분석.
- `02_Analysis/HwangBJ/pbmc/harmony_MASL_MASH/`: PBMC 분석; `reference_matching/`, `condition_comparison/` 포함.
- `05_Figure/HwangBJ/`: 각 분석의 PDF/PNG.
- [HwangBJ_export_counts.R](../scripts/hwangbj/HwangBJ_export_counts.R): RDS → sparse binary cache.
- [HwangBJ_condition_analysis.py](../scripts/hwangbj/HwangBJ_condition_analysis.py): donor permutation, bootstrap, 시각화.
- [HwangBJ_build_report.py](../scripts/hwangbj/HwangBJ_build_report.py): 저장된 결과에서 한국어 HTML 보고서 생성. 분석 후 `python scripts/hwangbj/HwangBJ_build_report.py`로 실행한다. 보고서는 원본 코호트의 결과 설명을 포함하므로 입력이나 분류 기준이 바뀌면 문구를 검토한다.

기존 결과 스냅샷으로 보고서만 생성하려면 `--analysis-root /path/to/02_Analysis/HwangBJ --figure-root /path/to/05_Figure/HwangBJ`를 지정한다. 이 경로는 읽기만 하고 새 보고서와 metadata inventory는 저장소 `results/`에 쓴다. 이전 MASL-only 결과/대응 표가 없으면 해당 역사 비교는 생략한다.

[HwangBJ_stage_analysis.py](../supporting/hwangbj/HwangBJ_stage_analysis.py)는 이전 stage 탐색용 보조 코드다. 현재 MASL/MASH 노트북에서는 호출하지 않는다. 임상 stage metadata 없이 donor 이름으로 stage를 추정하면 안 되며, 과거 cluster 3 표기를 통합 cluster 1에 적용해서도 안 된다.
