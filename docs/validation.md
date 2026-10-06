# 검증 기록 — 2026-10-06 갱신


## 2026-10-06 Figure2/HwangBJ 갱신 검증

| 항목 | 결과 | 확인 범위 |
| --- | --- | --- |
| 주 분석/보조 코드 문법 | 통과 | 주 분석 17개: notebook 10개, Rmd 6개, Python 1개; 활성 HwangBJ helper 3개도 Python AST/R parse |
| 최신 원본 스냅샷 | 79개 일치 | 초기 manifest + update_source_manifest.tsv; 저장소 밖 원본 변경 없음 |
| 배포 스크립트 해시 | 75개 일치 | release_manifest.tsv 갱신; supporting/archive의 기존 54개 내용 유지 |
| Python/R 경로 검사 | 통과 | 기존 Python 10개, R 입력/출력 분리·샘플 매핑 |
| Figure2 donor 구성 분석 | 원본 수치와 일치 | 실제 저장 AnnData의 obs로 실행: Healthy 5명/MASLD 6명, 9개 celltype P값 및 BH q값; donor boxplot PDF/PNG 생성 |
| Figure2 pooled Fisher | 실행 셀에서 제거 | 기존 표/미보정 별표 셀을 donor별 통계 표와 boxplot으로 대체; 다른 DEG 탐색 셀의 통계 단위는 그대로 |
| HwangBJ 실제 RDS 로딩 | 통과 | Matrix 기반 sparse export 후 AnnData: 간 핵 MASL 10,442 × 30,912; PBMC MASL/MASH 24,492 × 29,857; 네 RDS 입력/metadata 연결 |
| Harmony 실행 연결 | 작은 행렬에서 통과 | 80 cells/2 donors의 Scanpy Harmony representation; 기존 scRNA 환경 + 임시로 분리한 harmonypy 0.0.10; 전체 코호트 재실행 아님 |
| HwangBJ donor 비교 함수 | 원본 수치와 일치 | 기존 8-donor 빈도표로 70개 exact permutation, 평균 차이 및 bootstrap 95% CI 재계산; P=0.2571428571 |
| HwangBJ 과학 분석 코드 | 비경로 셀 유지 | 원본 코드 셀 중 설정/입력/보조 코드 연결 6개만 변경; 나머지 코드 셀 AST 일치 |
| HTML 보고서 builder | 통과 | 원본 저장 결과를 read-only root로 지정해 results/에 HTML 생성; raw metadata 재확인 |

전체 donor Harmony/cluster/reference matching을 Git 사본으로 재실행하거나 모든 Figure를 재계산하지 않았다. HwangBJ 원본 실행의 결과와 이번 경로/부분 runtime 검증을 구분한다. 기존 Python 환경의 패키지 설치 문제 및 새 환경 준비 범위는 [dependencies.md](dependencies.md), HwangBJ 입력/실행은 [hwangbj.md](hwangbj.md)를 참고한다.

현재 로그는 `results/validation/update_2026_10_06_runtime.json`에 있다. `--original-root` 검사는 최신 source snapshot을 우선하며 79개 원본을 점검한다. 아래 2026-09-29 기록은 당시 상태를 설명하는 역사 기록이다.

## 2026-09-29 초기 검증

이번 검증은 **복사본의 실행 준비와 입력 보존**을 확인한다. 모든 Figure의 재계산, 논문 수치 비교, 공개 데이터만으로의 재현 완료를 의미하지 않는다.

| 항목 | 결과 | 확인 범위 |
| --- | --- | --- |
| 원본 스크립트 | 74개 해시 일치 | 초기 원본 SHA-256과 비교; 원본 수정 없음 |
| 보조/보관 복사본 | 54개 해시 일치 | 초기 복사본과 비교; 추가 변경 없음 |
| 주 분석 소스 | 16개 통과 | notebook 9개, R Markdown 6개, Python 1개 |
| Notebook 형식·Python 문법 | 통과 | 출력/실행 횟수 비움, 코드 셀 AST, 개인 절대경로와 입력 ID 점검 |
| R Markdown 문법 | 177개 R chunk 통과 | R 4.4.2 parse 및 중복 chunk label 검사; chunk 실행 아님 |
| 공통 도구 문법 | 통과 | Python 도구 compile, R 파일 5개 parse, pySCENIC shell `bash -n` |
| Python 경로 동작 | 10개 테스트 통과 | 입력 보존, override 우선순위, 누락 입력, 절대/상위 경로 및 symlink 이탈 방지 |
| R 경로·샘플 매핑 | 통과 | 입력/출력 분리, override, 경로 이탈, 샘플 이름별 정렬, 중복/미등록 샘플 오류 |
| 실제 입력 점검 | 필수 오류 0개 | 분석 16개가 참조하는 26종, 총 35회 참조(선택 입력 포함); 존재 및 H5AD/일부 표 구조 |
| Notebook 시작 셀 | 9개 통과 | `general_env`에서 bootstrap + 첫 import 셀 실행; 발현 행렬 로딩/분석은 제외 |
| 보조 표 생성 | 통과 | 실제 marker DEG를 읽어 Excel 생성 후 재열기; 10개 시트, 988,487 bytes |
| 환경 기록 | Python 25개 버전 기록 | R은 일부 패키지 누락; 환경 재설치나 전체 분석 실행 검증 아님 |

## 반복할 수 있는 검사

저장소 루트에서 실행한다. R 실행 파일이 PATH에 없으면 `Rscript`를 해당 환경의 실행 파일 경로로 바꾼다.

```bash
python -m unittest discover -s tests -v
Rscript --vanilla tests/test_paths.R
python tools/validate_repository.py --rscript Rscript
python tools/check_inputs.py --schema
python tools/check_environment.py
Rscript tools/check_r_packages.R
bash -n scripts/external/pyscenic.sh
```

원본이 있는 작업 컴퓨터에서는 `validate_repository.py`에 `--original-root /path/to/Liver_bio_project`를 추가하면 최신 원본 79개 해시도 비교한다. 데이터 없이 실행하는 검사에서는 입력 점검이 실패하는 것이 정상이다. R 패키지 점검은 필요한 패키지가 없으면 종료 코드 1을 반환한다.

현재 컴퓨터의 상세 로그는 Git에서 제외한 `results/validation/`에 있다. 입력 경로를 포함하는 이 로컬 로그는 공개 저장소 파일 목록에서 제외된다. 보조 표 smoke test 출력도 `results/` 안에 있다.

## 남은 재현 확인

- bulk 전체 실행에는 DESeq2 등 누락된 R 패키지를 갖춘 환경이 필요하다. 검사에 사용한 기존 R 환경의 누락 목록은 [환경 안내](dependencies.md)에 기록했다.
- pySCENIC Docker 계산, 전체 CellPhoneDB 계산, 모든 노트북 셀 및 R Markdown 보고서의 완전 실행은 수행하지 않았다. 새 R 실행 도구도 문법 검사까지 수행했으며 실제 전체 render는 아직 검증하지 않았다.
- 입력 검사에서 확인한 AnnData 구조가 모든 세포 주석·유전자 값·수동 annotation의 정확성을 검증하지는 않는다. 입력 데이터와 온라인 gene set/model 버전을 확정한 후 논문 Figure와 주요 표의 수치를 비교해야 한다.
- 배포할 데이터의 accession/다운로드 위치, 최종 환경 lock, 라이선스와 논문/코드 인용 정보는 공개 전에 확정할 항목이다.

초기 원본 정보는 [source_manifest.tsv](source_manifest.tsv), 보완 후 복사본의 현재 해시는 [release_manifest.tsv](release_manifest.tsv), 변경 내용은 [release_notes.md](release_notes.md)에 있다.
