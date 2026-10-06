# 실행 환경

주 분석 17개에 필요한 직접 의존성과 현재 컴퓨터에서 관측한 버전을 기록했다. **설치 목록/관측 기록이며, 새 환경에서 전체 Figure를 실행해 검증한 lock 파일은 아니다.** 과거/보조 스크립트에는 추가 패키지가 필요할 수 있다.

## Python

[python-observed.json](../environment/python-observed.json)은 기존 `general_env`의 Python 3.10.16 및 직접 의존성 25개 버전 기록이다. Scanpy 1.10.3, AnnData 0.11.1, NumPy 1.26.4, pandas 2.2.2, gseapy 1.1.4 등이 관측되었다. 분석별 패키지 대응은 [python-packages.json](../environment/python-packages.json)에 있다.

새 환경을 만드는 후보 설정:

```bash
cd environment
conda env create -f python.yml
cd ..
conda activate slc7a5-manuscript
python tools/check_environment.py
```

기존 Python 3.10 환경을 따로 준비했다면 `python -m pip install -r environment/requirements-python.txt`를 사용할 수 있다. 새 설치의 의존성 해결과 전체 분석은 이번 작업에서 수행하지 않았다. `check_environment.py`는 배포 패키지의 설치 버전을 확인하며 실제 import 성공이나 결과 일치를 뜻하지 않는다.

입력/소스 점검만 필요하면 `environment/requirements-checks.txt`의 nbformat/h5py로 검사 도구를 실행할 수 있다. 경로 동작 테스트는 Python 표준 라이브러리만 사용한다.

## R

[패키지 목록](../environment/r-packages.tsv)에 CRAN/Bioconductor 구분과 분석 ID를 기록했다. 공통 도구에는 jsonlite, R Markdown 보고서에는 knitr/rmarkdown과 Pandoc가 필요하다. bulk는 DESeq2/clusterProfiler/msigdbr 등, HYU는 limma 등 해당 코드의 패키지가 필요하다.

```bash
Rscript tools/check_r_packages.R
# 별도 R 환경에서 누락 패키지를 설치하려는 경우:
Rscript environment/install_R.R
Rscript tools/render_rmd.R bulk_nosi
```

설치 도구는 누락된 패키지만 설치하며 버전을 고정하지 않는다. 현재 환경 전체를 변경하는 명령은 이번 작업에서 실행하지 않았다. 논문 최종 검증 환경에서 `sessionInfo()`와 환경 잠금 정보를 기록해야 한다. `render_rmd.R`는 정상 종료 시 보고서 옆에 `sessionInfo.txt`를 저장한다.

기존 `R_only`(R 4.4.2)에서 23개 중 15개, `R_base`(R 4.4.1)에서 17개 패키지가 확인되었다. 두 환경 모두 DESeq2, clusterProfiler, EnhancedVolcano 등 일부 주 분석 의존성이 없다. [R_only 관측](../environment/r-observed-R_only.tsv), [R_base 관측](../environment/r-observed-R_base.tsv)에 설치 버전과 `MISSING`을 표시했다. R 문법/경로 검증은 R 4.4.2에서 통과했지만 bulk 전체 실행 검증은 하지 않았다.

## 외부 도구·참조 데이터

- pySCENIC: 기존 코드의 `aertslab/pyscenic:0.12.1` 컨테이너를 사용하도록 분리했다. Docker와 TF 목록, ranking feather 2종, motif annotation이 필요하다. 이미지 태그는 코드 설정이며 이번 작업에서 pull/계산하거나 digest를 검증하지 않았다.
- CellPhoneDB: 관측된 패키지는 5.0.1이다. 참조 데이터 zip은 입력 ID `cpdb_database`로 지정한다. DB 파일명/버전과 배포 checksum을 공개 자료에 함께 기록한다.
- GSEA/ORA 및 일부 경로 점수: 코드에서 gseapy/MSigDB/Enrichr 또는 온라인 gene set 다운로드를 사용한다. 원 분석의 gene set 이름은 유지했으며, 최종 재현 검증 시 사용한 gene set 버전/다운로드 날짜 또는 원본 GMT 파일을 보관해야 한다.
- CellTypist/PBMC: 코드가 요구하는 모델/참조 자료도 패키지와 별도로 준비한다. 설치 패키지 존재만으로 해당 모델의 준비 상태가 확인되지는 않는다.

분석 실행 전에 필요한 입력은 [데이터 안내](data_requirements.md), 검증 범위는 [validation.md](validation.md)를 확인한다.

## HwangBJ 추가 환경 (2026-10-06)

현재 Python 환경에 harmonypy **0.0.10**이 설치되어 있어야 하며, Rscript/Matrix가 추가로 필요하다. 직접 의존성 목록에 harmonypy와 원본 실행의 scikit-learn 1.1.3을 추가했다. 기존 다른 환경의 패키지를 자동으로 로드하는 fallback은 배포 사본에서 제거했다. `SLC7A5_RSCRIPT` 또는 PATH로 R 실행 파일을 지정한다.

이번 runtime 점검에는 원본 scRNA 환경과 임시 디렉터리에 분리한 기존 harmonypy 0.0.10 소스를 사용했다. 기존 scRNA 환경에는 harmonypy가 설치되어 있지 않으며 general_env의 scikit-learn import도 오류가 있어, 해당 기존 환경을 곧바로 검증된 설치 환경으로 간주하지 않는다. 전체 새 환경 설치나 전체 Harmony 결과 재계산 검증은 수행하지 않았다. [HwangBJ 안내](hwangbj.md)를 참고한다.
