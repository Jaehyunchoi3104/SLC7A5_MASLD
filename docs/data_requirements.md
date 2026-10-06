# 입력 데이터와 출력 위치

주 분석 코드는 전처리된 AnnData, bulk 발현 행렬, 샘플 메타데이터, DEG 및 외부 참조 DB를 읽는다. 목록은 [config/inputs.json](../config/inputs.json)에 있고, 38개 ID 중 34개는 분석 입력/기존 결과(선택적 과거 HwangBJ 객체 포함), 4개는 pySCENIC 재계산용 참조 자료다. 대용량 데이터는 이 저장소에 복사하지 않았다.

## 현재 컴퓨터와 새 컴퓨터

현재 컴퓨터에서는 Git에서 제외한 `config/paths.local.json`이 기존 데이터 루트를 가리킨다. 기존 입력은 읽고 새 분석 결과는 `git/results/`에 쓴다.

다른 컴퓨터에서 사용할 때는 저장소 루트에서 다음과 같이 설정 파일을 준비한다. 이미 로컬 설정이 있으면 복사 명령 대신 그 파일을 편집한다.

```bash
cp -n config/paths.example.json config/paths.local.json
```

- `data_root`: 입력 목록의 상대경로를 해석할 데이터 루트.
- `input_overrides`: 파일을 다른 폴더에 보관한 경우 입력 ID별 실제 파일 경로. 사용하지 않는 예시 항목은 삭제한다.
- `seed`: 공통 초기 seed. 원 분석에 별도로 설정된 seed/알고리즘 설정은 코드에 유지되어 있으며 이 값 하나로 모든 도구의 결정성이 보장되지는 않는다.

```json
{
  "data_root": "/path/to/study-data",
  "seed": 42,
  "input_overrides": {
    "scrna_monomac_seed": "/path/to/scRNA_monoMAC_detail.h5ad",
    "cpdb_database": "/path/to/cellphonedb.zip"
  }
}
```

`SLC7A5_DATA_ROOT` 환경변수는 `data_root`보다 우선한다. 입력별 `input_overrides`는 그대로 우선하므로, 예시 파일의 임시 경로를 반드시 바꾸거나 삭제한다. 상대 override 경로는 저장소 루트 기준이다. Jupyter를 저장소 밖에서 시작할 경우 `SLC7A5_REPO_ROOT`도 이 저장소 루트로 지정한다.

## 결과와 중간 입력

출력은 `results/<원 프로젝트의 상대경로>`에 저장한다. 상대경로로 저장하는 Python 셀의 작업 폴더는 `results/runs/<analysis_id>/`다. bulk R 코드는 기존 파일 간 연결을 유지하기 위해 `results/02_SLC7A5_mono_Journal/04_bulkRNAseq/` 등 대응 경로를 작업 폴더로 사용한다. R HTML 보고서는 제공한 실행 도구를 쓰면 `results/reports/<analysis_id>/`에 저장된다.

생성 가능한 입력(`generated: true`)의 선택 순서는 **입력별 override → 이번 저장소의 생성 결과 → data_root에 있는 기존 스냅샷**이다. 서로 다른 분석 회차의 결과를 섞지 않으려면 필요한 입력 ID를 override로 특정한다. 경로 도구는 입력을 이동·복사·갱신하지 않는다.

## 입력 파일 점검

```bash
python tools/check_inputs.py --schema
python tools/check_inputs.py --analysis bulk_nosi --analysis nfkb_shared --schema
```

필수 파일이 없거나 검사한 형식이 맞지 않으면 종료 코드 1을 반환한다. `--schema`는 H5AD의 `X/obs/var`, 일부 CSV/TSV 열과 bulk 샘플 이름을 검사하며 발현 행렬 전체를 메모리에 읽지 않는다. 모든 세포 주석·유전자·값·대비의 생물학적 적합성을 검증하는 도구는 아니다. 기본 검사는 기존 pySCENIC 결과 사용을 기준으로 하며, 재계산용 참조 4종은 Docker 실행 단계에서 확인한다.

`config/bulk_samples.tsv`는 원 count 행렬의 9개 샘플과 기존 실험군을 대응시킨 표다. 추가 bulk 및 HYU 임상 메타데이터를 대체하는 표가 아니다. `bulk_nosi`에서의 siCon_1 제외는 해당 R Markdown에 유지되어 있다.

## GitHub에 포함할 자료

코드와 함께 포함한 것은 입력 목록/형식, 경로 설정 예시, bulk 실험군 표, 환경 목록, 실행·검증 안내다. H5AD/FASTQ/BAM 및 전체 결과는 `.gitignore`에서 제외했다. 별도로 배포하는 데이터에는 입력 목록의 파일명과 연결되는 accession 또는 영구 다운로드 주소, 데이터 버전·checksum, 샘플/세포 주석 설명을 기록한다. 임상 자료는 연구에서 공개할 수 있는 메타데이터와 접근 절차를 기준으로 제공한다.

현재 입력 목록의 `download_url: null`, `availability: deposition_or_access_instructions_pending`는 **공개 위치가 아직 확정되지 않았음**을 뜻한다. 파일명으로 확인된 `GSE210077`은 그 개별 입력의 accession이며 전체 통합 데이터의 accession이 아니다. 공개 원자료의 accession만으로 수동 주석된 처리 객체가 자동 재현되는 것은 아니므로, 해당 처리 객체를 배포하거나 생성 과정을 추가해야 한다.

데이터가 논문용으로 공개된 후 `config/inputs.json`의 accession/download_url/availability를 갱신하고, 최종 파일 checksum과 논문 Data availability 문구를 맞춘다. 이 작업에서는 데이터 업로드나 공개 권한 판단을 수행하지 않았다.

2026-10-06: HwangBJ RDS 네 개와 scRNA 참조 DEG 세 개를 필수 입력으로 추가했다. 이전 MASL-only 주석 객체 한 개는 선택 입력이다. 개별 RDS 경로 override와 Rscript 설정은 [HwangBJ 안내](hwangbj.md)를 참고한다.
