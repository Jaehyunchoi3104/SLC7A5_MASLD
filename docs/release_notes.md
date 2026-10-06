**2026-09-29 — 복사본의 실행 준비 보완**

변경 대상은 이 저장소의 주 분석 16개와 새 공통 도구/문서다. 저장소 밖 원본 스크립트는 변경하지 않았다. `supporting/` 11개와 `archive/` 43개는 기존 복사 상태를 유지하는 참고 자료이며, 공통 경로 설정을 적용한 실행 대상에 포함하지 않는다.

- Python/R 경로 함수를 추가했다. 입력 파일은 지정한 데이터 위치에서 읽고, 명시적 저장 경로와 상대 저장 경로는 저장소 `results/` 안으로 연결했다. 생성 결과가 있으면 후속 분석에서 사용하고, 없으면 기존 입력 스냅샷을 사용한다. 입력별 override가 있으면 해당 설정을 우선한다.
- 9개 노트북, 6개 R Markdown, 1개 Python 도구에 초기 설정을 추가했다. 기존 개인 절대경로를 공통 함수 호출로 바꾸었다. 경로에 쓰인 원 프로젝트의 폴더 구조는 결과 추적을 위해 유지했다.
- bulk 그룹 정보를 `config/bulk_samples.tsv`로 분리했다. 열 순서가 달라도 샘플 이름으로 매칭하고, 알 수 없는 샘플·중복 ID는 오류로 처리한다. 기존 군 이름, 기준군, `siCon_1` 제외 분석은 유지했다.
- 노트북 첫 import 셀의 미사용/중복 import 88개를 제거했다. 별칭이 전체 코드 셀에서 사용되는지를 확인한 범위이며, 분석 함수·유전자 목록·통계 대비·cutoff의 일괄 변경은 하지 않았다.
- Figure3-1의 pySCENIC export 단계는 `adata.copy()`를 사용한다. 기존 객체의 세포 주석과 UMAP을 삭제해 후속 셀에서 사용할 수 없게 되는 문제를 수정했다. adjacency TSV의 첫 로딩에 탭 구분자를 지정했다.
- 노트북에 Python 코드로 들어 있던 Docker 명령 3개를 실행 안내 Markdown으로 바꾸고, `scripts/external/pyscenic.sh`로 분리했다. pySCENIC 계산은 별도 단계다.
- 입력 목록, 실행 전 파일 점검, 환경 버전 기록, R Markdown 실행 도구, 경로 동작 테스트를 추가했다. 입력 데이터는 복사하지 않았다.

초기 복사 당시의 파일 정보는 [source_manifest.tsv](source_manifest.tsv)에 그대로 보존했다. 이 파일의 `copy_sha256`, `copy_bytes`, `code_sha256`는 **초기 복사 시점**의 기록이다. 보완 후의 70개 복사 스크립트 해시는 [release_manifest.tsv](release_manifest.tsv)에 기록한다. 상세 경로 변경 수는 [refactoring_changes.json](refactoring_changes.json), import 정리는 [import_cleanup.json](import_cleanup.json)을 참고한다.

검증 결과와 남은 재현 확인 범위는 [validation.md](validation.md)에 있다. 원격 저장소 생성·업로드, 데이터 공개, 논문 결과와의 수치 비교는 수행하지 않았다.


**2026-10-06 — donor-level Figure2 및 HwangBJ 동기화**

- Figure2에 원본의 library별 celltype stacked bar와 donor별 구성 비교를 반영했다. Healthy CD45 library를 합치고 exact permutation Mann–Whitney U 및 9개 celltype BH q-value를 계산한다. 기존 pooled Fisher 및 미보정 별표 셀은 donor별 표/boxplot으로 대체한다. 원본 분석 노트북은 수정하지 않았다. 기존 Fig2B_proportionbargraph.pdf 출력 이름은 유지하되 donor boxplot을 저장한다.
- HwangBJ 노트북과 sparse RDS 변환, donor MASL/MASH 비교, HTML 보고서 builder를 scripts/hwangbj에 추가했다. 개인 절대경로와 다른 Python 환경의 harmonypy fallback을 제거했다. stage 탐색 함수는 supporting/hwangbj에 보존하며 현재 분석에서 호출하지 않는다.
- RDS 네 개, 참조 DEG 세 개, 선택적 이전 MASL-only 객체를 입력 목록에 등록했다. Rscript는 PATH 또는 SLC7A5_RSCRIPT로 지정한다. 출력과 cache는 저장소 results/에 쓴다.
- 원본 코호트의 marker 기준, Harmony 설정, DEG matching 필터 및 donor 통계 알고리즘을 유지했다. 선택된 cluster 및 유의성에 대한 원본 해석은 docs/hwangbj.md에 기록했다.
- 현재 주 분석 17개, 활성 HwangBJ 보조 코드 3개, 보조 참고 12개, 과거 참고 43개다. 초기 source_manifest.tsv는 보존하고 갱신 원본/신규 원본의 해시는 update_source_manifest.tsv에 기록했다. 원본 검증 도구는 최신 기록을 우선하여 총 79개 원본을 점검한다. release_manifest.tsv는 현재 75개 정리 스크립트의 해시다.
