"""Build an offline Korean HTML report from saved HwangBJ results; no analysis rerun."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from html import escape
from string import Template
import ast
import base64
import hashlib
import json
import os
import shutil
import subprocess

import pandas as pd

import argparse
import sys
_repo = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_repo))
from slc7a5_paths import dataset_path, output_path
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--analysis-root', type=Path, help='Saved 02_Analysis/HwangBJ directory (read only)')
parser.add_argument('--figure-root', type=Path, help='Saved 05_Figure/HwangBJ directory (read only)')
args = parser.parse_args()
PROJECT = Path(output_path('02_SLC7A5_mono_Journal/.report-anchor')).parent
BASE = (args.analysis_root or PROJECT / '02_Analysis/HwangBJ').resolve()
FIGURE_BASE = (args.figure_root or PROJECT / '05_Figure/HwangBJ').resolve()
BASE_OUTPUT = Path(output_path('02_SLC7A5_mono_Journal/02_Analysis/HwangBJ/report_source_metadata_inventory.csv')).parent
RDS_INPUTS = {
    dataset: {role: Path(dataset_path(f'hwangbj_{dataset}_{role}'))
              for role in ['counts', 'metadata']}
    for dataset in ['liver_nuclei', 'pbmc']
}
LIVER = BASE / 'liver_nuclei/harmony'
PBMC = BASE / 'pbmc/harmony_MASL_MASH'
REF = PBMC / 'reference_matching'
COMP = PBMC / 'condition_comparison'
OUTPUT = BASE_OUTPUT / 'HwangBJ_analysis_report.html'


def read_json(path):
    return json.loads(path.read_text())


def link(path, label):
    assert path.exists(), path
    relative = os.path.relpath(path, OUTPUT.parent)
    return f'<a href="{escape(relative, quote=True)}">{escape(label)}</a>'


def table(frame, classes='', table_id=''):
    html = frame.to_html(index=False, border=0, classes=f'data-table {classes}',
                         table_id=table_id or None, escape=True)
    return f'<div class="table-wrap">{html}</div>'


def figure(path, title, caption, fig_id):
    assert path.exists(), path
    data = base64.b64encode(path.read_bytes()).decode('ascii')
    pdf = path.with_suffix('.pdf')
    pdf_link = link(pdf, 'PDF 열기') if pdf.exists() else ''
    return f'''<figure id="{fig_id}" class="figure-card">
      <figcaption><strong>{escape(title)}</strong><span>{pdf_link}</span></figcaption>
      <button type="button" class="figure-button" aria-label="{escape(title, quote=True)} 크게 보기">
      <img src="data:image/png;base64,{data}" alt="{escape(title, quote=True)}" loading="lazy" decoding="async"></button>
      <p class="caption">{caption}</p></figure>'''


# Verify the scope against the original donor metadata rather than donor-name suffixes.
inventory_path = BASE_OUTPUT / 'report_source_metadata_inventory.csv'
rscript = os.environ.get('SLC7A5_RSCRIPT') or shutil.which('Rscript')
if not rscript:
    raise RuntimeError('Set SLC7A5_RSCRIPT or add Rscript to PATH.')
r_code = '''inputs <- commandArgs(trailingOnly=TRUE); out <- inputs[3]
rows <- lapply(c("liver_nuclei", "pbmc"), function(ds) {
 x <- readRDS(inputs[match(ds,c("liver_nuclei","pbmc"))])
 stopifnot(identical(names(x),c("orig.ident","nCount_RNA","nFeature_RNA","Genotype_ID","Condition")))
 z <- as.data.frame(table(donor=x$Genotype_ID,condition=x$Condition)); z <- z[z$Freq>0,]
 names(z)[3] <- "raw_n"; z$dataset <- ds; z[c("dataset","donor","condition","raw_n")]
}); write.csv(do.call(rbind,rows),out,row.names=FALSE)
'''
subprocess.run([rscript, '--vanilla', '-e', r_code, str(RDS_INPUTS['liver_nuclei']['metadata']), str(RDS_INPUTS['pbmc']['metadata']), str(inventory_path)], check=True)
raw_inventory = pd.read_csv(inventory_path)
liver = read_json(LIVER / 'analysis_summary.json')
pbmc = read_json(PBMC / 'analysis_summary.json')
matching = read_json(REF / 'reference_cluster_annotation.json')
comparison = read_json(COMP / 'MASL_MASH_primary_comparison.json')
old_path = BASE / 'pbmc/harmony/reference_matching/reference_cluster_annotation.json'
old_matching = read_json(old_path) if old_path.is_file() else None
frequencies = pd.read_csv(COMP / 'donor_MASL_MASH_counts_and_frequencies.csv')
liver_qc = pd.read_csv(LIVER / 'donor_QC.csv')
liver_audit = pd.read_csv(LIVER / 'myeloid_recluster_marker_QC.csv')
liver_subtypes = pd.read_csv(LIVER / 'myeloid_cluster_signature_scores.csv')
pbmc_subtypes = pd.read_csv(PBMC / 'myeloid_cluster_signature_scores.csv')
correlations = pd.read_csv(REF / 'reference_DEG_cluster_Spearman_correlations.csv', index_col=0)
correspondence_path = REF / 'MASL_only_annotation_to_joint_clusters.csv'
correspondence = pd.read_csv(correspondence_path, index_col=0) if correspondence_path.is_file() else None
sensitivity = pd.read_csv(COMP / 'alternative_denominator_and_expression_gate_descriptive.csv')
cluster = matching['selected_cluster']
assert cluster == comparison['selected_reference_cluster']
assert frequencies.groupby('condition').size().to_dict() == {'MASL': 4, 'MASH': 4}
assert frequencies.high_n.sum() == matching['n_annotated_cells'] == pbmc['SLC7A5_high_candidate_n']
assert liver['monocyte_candidate_n'] == 0 and not liver['high_definition_available']
assert comparison['n_permutations'] == 70

# Read the actual marker panels and configuration from the executable notebook.
notebook_path = Path(__file__).with_name('HwangBJ_analysis.ipynb')
notebook = json.loads(notebook_path.read_text())
cells = {c['id']: ''.join(c['source']) for c in notebook['cells']}
lineage_panels = None
myeloid_panels = None
for cell_id, name in [('8e8ea206', 'LINEAGE'), ('e56fcd24', 'MYELOID_MARKERS')]:
    tree = ast.parse(cells[cell_id])
    node = next(node for node in tree.body if isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == name for t in node.targets))
    if name == 'LINEAGE':
        lineage_panels = ast.literal_eval(node.value)
    else:
        myeloid_panels = ast.literal_eval(node.value)

liver_genes = int((BASE / 'liver_nuclei/sparse_cache/shape.txt').read_text().splitlines()[0])
pbmc_genes = int((BASE / 'pbmc/sparse_cache_MASL_MASH/shape.txt').read_text().splitlines()[0])
raw_n = raw_inventory.groupby('dataset').raw_n.sum().to_dict()
source_rows = []
for dataset, label, genes in [('liver_nuclei', '간 핵 snRNA-seq', liver_genes), ('pbmc', 'PBMC scRNA-seq', pbmc_genes)]:
    source_rows.append({'검체': label, '제공된 matrix의 관측 수': f'{raw_n[dataset]:,}',
                        '입력 유전자 수': f'{genes:,}', '원본 donor 구성': 'MASL 4명 + MASH 4명',
                        '현재 분석에 포함': 'MASL 4명' if dataset == 'liver_nuclei' else 'MASL 4명 + MASH 4명'})
source_table = table(pd.DataFrame(source_rows))
source_links = '<ul class="source-list">' + ''.join(
    f'<li>{link(RDS_INPUTS[dataset]["counts" if role == "counts_matrix" else "metadata"], f"{dataset}_{role}.rds")}</li>'
    for dataset in ['liver_nuclei', 'pbmc'] for role in ['counts_matrix', 'metadata']) + '</ul>'
metadata_table = table(pd.DataFrame([
    {'컬럼': 'orig.ident', '내용': '검체 종류(nuclei 또는 pbmc)', '분석에서의 사용': '검체별 독립 처리'},
    {'컬럼': 'nCount_RNA', '내용': '제공된 세포/핵별 UMI 수', '분석에서의 사용': '기본 QC 정보; QC는 count matrix에서 재계산'},
    {'컬럼': 'nFeature_RNA', '내용': '제공된 세포/핵별 검출 유전자 수', '분석에서의 사용': '기본 QC 정보; QC는 count matrix에서 재계산'},
    {'컬럼': 'Genotype_ID', '내용': 'MASL1–4 및 MASH1–4 donor ID', '분석에서의 사용': 'donor 식별, Harmony batch, 생물학적 반복 단위'},
    {'컬럼': 'Condition', '내용': 'MASL 또는 MASH 질환군', '분석에서의 사용': 'PBMC donor별 군 간 비교'},
]))
qc_rows = []
for record, label in [(liver, '간 핵'), (pbmc, 'PBMC')]:
    high = record['SLC7A5_high_candidate_n']
    qc_rows.append({'검체': label, '선택한 관측 수': f'{record["input_n"]:,}',
                   'QC 통과': f'{record["QC_n"]:,}', '최종 myeloid': f'{record["myeloid_candidate_n"]:,}',
                   'monocyte 후보': f'{record["monocyte_candidate_n"]:,}',
                   'SLC7A5-high 참조 후보': f'{high:,}' if high is not None else '정의 불가 / 검정 미수행'})
qc_table = table(pd.DataFrame(qc_rows))
lineage_table = table(pd.DataFrame([{'Lineage': k, '사용한 marker': ', '.join(v)} for k,v in lineage_panels.items()]))
myeloid_table = table(pd.DataFrame([{'후보 subtype': k, '사용한 marker': ', '.join(v)} for k,v in myeloid_panels.items()]))

initial_liver = int(liver_audit.n_cells.sum())
excluded_liver = int(liver_audit.loc[~liver_audit.retained, 'n_cells'].sum())
liver_subtype_table = table(liver_subtypes[['myeloid_cluster','annotation_candidate','n_cells']].rename(
    columns={'myeloid_cluster':'Cluster', 'annotation_candidate':'Marker 기반 후보 주석','n_cells':'핵 수'}))
liver_donor_table = table(liver_qc.rename(columns={'donor':'Donor','input_n':'분석 입력 핵 수','retained_n':'QC 통과','removed_n':'QC 제외'}))
liver_fig = figure(FIGURE_BASE / 'liver_nuclei/harmony/06_myeloid_UMAP.png',
    '간 핵: 최종 myeloid와 marker 기반 주석',
    '최종 myeloid 234개 핵의 UMAP입니다. 현재 기준에서는 classical/non-classical monocyte 후보가 선택되지 않았습니다. '
    '이는 이 데이터와 자동 분류 기준의 결과이며 간에 monocyte가 없다는 생물학적 결론이 아닙니다.', 'liver-umap')

pbmc_clusters = pbmc_subtypes[['myeloid_cluster','annotation_candidate','n_cells']].copy()
pbmc_clusters['최종 참조 주석'] = pbmc_clusters.apply(lambda r: 'SLC7A5_high_monocyte (잠정적)' if str(r.myeloid_cluster)==cluster else r.annotation_candidate, axis=1)
pbmc_cluster_table = table(pbmc_clusters.rename(columns={'myeloid_cluster':'Cluster','annotation_candidate':'Matching 전 marker 주석','n_cells':'세포 수'}))
corr_table = correlations.T.reset_index().rename(columns={'index':'Cluster'})
for col in corr_table.columns[1:]:
    corr_table[col] = corr_table[col].map(lambda x: f'{x:.3f}')
correlation_table = table(corr_table)
primary_rho = float(matching['primary_rho'])
secondary_best = str(correlations.loc['SLC7A5-high vs Classical'].idxmax())
secondary_selected = float(correlations.loc['SLC7A5-high vs Classical', cluster])
if correspondence is not None and old_matching is not None:
    old_high_total = int(correspondence.SLC7A5_high_monocyte.sum())
    old_to_0 = int(correspondence.loc[0, 'SLC7A5_high_monocyte'])
    old_to_selected = int(correspondence.loc[int(cluster), 'SLC7A5_high_monocyte'])
    correspondence_table = table(correspondence.reset_index().rename(columns={'myeloid_cluster':'통합 PBMC cluster',
        'Classical_monocyte':'이전 Classical','Nonclassical_monocyte':'이전 Nonclassical','SLC7A5_high_monocyte':'이전 MASL-only high 후보'}))
else:
    old_high_total = old_to_0 = old_to_selected = 0
    correspondence_table = '<p>이전 MASL-only 분석 결과를 제공하지 않아 barcode 대응은 표시하지 않습니다.</p>'
ref_fig = figure(FIGURE_BASE / 'pbmc/harmony_MASL_MASH/11_PBMC_reference_DEG_correlation_heatmap.png',
    '참조 DEG와 PBMC 8개 cluster의 signed effect 상관',
    f'주 참조(vs rest)에서는 cluster {cluster}가 최상위입니다(ρ={primary_rho:.3f}). '
    f'보조 참조(vs Classical)의 최상위는 cluster {secondary_best}이며, 선택된 cluster {cluster}의 보조 참조 상관은 {secondary_selected:.3f}입니다.', 'ref-heatmap')
stability_fig = figure(FIGURE_BASE / 'pbmc/harmony_MASL_MASH/13_PBMC_donor_reference_similarity_heatmap.png',
    'Donor별 및 leave-one-donor-out 참조 상관',
    '각 donor의 주 참조 비교 및 donor 한 명씩 제외한 비교에서 모두 cluster 1이 최상위였습니다. '
    '이는 상대적 선택의 안정성을 보여주지만 낮은 상관이나 주·보조 참조 불일치를 해소하는 독립 검증은 아닙니다.', 'ref-stability')
annotation_fig = figure(FIGURE_BASE / 'pbmc/harmony_MASL_MASH/15_PBMC_reference_annotation_UMAP.png',
    'PBMC: 참조 주석과 SLC7A5 발현의 분포',
    'Cluster, celltype_refined, Condition, SLC7A5 발현과 PPIF/ANPEP/ITGAX/VCAN signature를 함께 표시했습니다. '
    '집단 선택에 SLC7A5 자체의 발현이나 질환군별 빈도/P 값을 사용하지 않았습니다.', 'annotation-umap')

freq_table = frequencies[['donor','condition','total_QC_n','monocyte_n','high_n','high_pct_of_monocyte']].copy()
freq_table['high_pct_of_monocyte'] = freq_table.high_pct_of_monocyte.map(lambda x: f'{x:.2f}%')
freq_table = freq_table.rename(columns={'donor':'Donor','condition':'질환군','total_QC_n':'전체 QC PBMC',
    'monocyte_n':'전체 monocyte','high_n':'참조 high 후보 수','high_pct_of_monocyte':'후보 / monocyte'})
donor_table_html = table(freq_table, table_id='donor-table')
# Tag table rows for the optional visual filter; primary statistics stay fixed.
for condition in ['MASL','MASH']:
    donor_table_html = donor_table_html.replace(f'<td>{condition}</td>', f'<td><span class="condition {condition.lower()}">{condition}</span></td>')
means = frequencies.groupby('condition').agg(n=('donor','size'), mean=('high_pct_of_monocyte','mean'), median=('high_pct_of_monocyte','median'))
group_rows = [{'질환군': c, '생물학적 반복': f'{int(means.loc[c,"n"])} donors',
               '평균 비율': f'{means.loc[c,"mean"]:.2f}%', '중앙값 비율': f'{means.loc[c,"median"]:.2f}%'} for c in ['MASL','MASH']]
group_table = table(pd.DataFrame(group_rows))
comparison_fig = figure(FIGURE_BASE / 'pbmc/harmony_MASL_MASH/17_PBMC_MASL_MASH_SLC7A5high_donor_comparison.png',
    'MASL·MASH의 donor별 비율과 평균 차이',
    '왼쪽의 각 점은 donor 한 명입니다. 오른쪽은 MASH − MASL의 평균 차이와 donor bootstrap 95% CI입니다. '
    '후보 비율이 MASH에서 높지만 유의한 차이는 확인되지 않았습니다.', 'condition-comparison')
counts_fig = figure(FIGURE_BASE / 'pbmc/harmony_MASL_MASH/16_PBMC_MASL_MASH_donor_counts_and_frequencies.png',
    'Donor별 포착 세포 수와 monocyte 중 후보 비율',
    '포착된 세포 수와 비율을 함께 제시합니다. 포착 수는 시퀀싱/회수 규모의 영향을 받으므로 혈액의 절대 monocyte 수로 해석하지 않습니다.', 'donor-counts')
q75_total = int(sensitivity.expression_q75_high_n.sum())

artifact_items = [
    (notebook_path, 'HwangBJ_analysis.ipynb 분석 코드'),
    (Path(__file__).with_name('HwangBJ_export_counts.R'), 'RDS sparse 변환 코드'),
    (Path(__file__).with_name('HwangBJ_condition_analysis.py'), 'Donor-level permutation / bootstrap 코드'),
    (LIVER / 'analysis_summary.json', '간 핵 분석 요약'),
    (LIVER / 'myeloid_recluster_marker_QC.csv', '간 핵 myeloid QC 및 제외 근거'),
    (LIVER / 'myeloid_cluster_signature_scores.csv', '간 핵 subtype marker 점수'),
    (PBMC / 'analysis_summary.json', '8-donor PBMC 분석 요약'),
    (REF / 'reference_cluster_annotation.json', '참조 주석 선택 근거'),
    (REF / 'reference_DEG_cluster_Spearman_correlations.csv', '참조별 cluster 상관계수'),
    (REF / 'MASL_only_annotation_to_joint_clusters.csv', 'MASL-only 주석과 통합 주석의 barcode 대응'),
    (COMP / 'donor_MASL_MASH_counts_and_frequencies.csv', 'Donor별 포착 수·분모·비율'),
    (COMP / 'MASL_MASH_primary_comparison.json', '주 비교의 P 값·효과 크기·신뢰구간'),
    (COMP / 'exact_70_donor_label_permutations.csv', '70개 donor label 배치의 null statistic'),
    (COMP / 'leave_one_donor_out_mean_differences.csv', 'Donor 제외 후 평균 차이'),
    (COMP / 'alternative_denominator_and_expression_gate_descriptive.csv', '대체 분모·expression-q75 기술통계'),
    (PBMC / 'MASL_MASH1_4_myeloid_reference_annotated.h5ad', '주석이 포함된 PBMC myeloid AnnData'),
    (PBMC / 'MASL_MASH1_4_monocyte_reference_annotated.h5ad', '주석이 포함된 PBMC monocyte AnnData'),
    (PBMC / 'monocyte_donor_group_pseudobulk_counts.npz', 'Donor × high/other raw UMI pseudobulk'),
    (PBMC / 'pseudobulk_matrix_rows.csv', 'Pseudobulk 행별 donor/group/세포 수'),
    (REF / 'SLC7A5_reference_cluster_prerank.rnk', '후속 pathway 분석용 donor-average ranking'),
    (inventory_path, '원본 RDS metadata에서 다시 확인한 donor별 관측 수'),
]
artifacts = '<ul class="artifact-list">' + ''.join(f'<li>{link(p,label)}</li>' for p,label in artifact_items if p.exists()) + '</ul>'
references = '<ul class="source-list">' + ''.join(f'<li>{link(p,p.name)}</li>' for p in [Path(dataset_path('hwangbj_reference_mono5')),Path(dataset_path('hwangbj_reference_all')),Path(dataset_path('hwangbj_reference_classical'))]) + '</ul>'

style = r'''
:root{--navy:#152d45;--ink:#223448;--muted:#586b7d;--paper:#fff;--bg:#f3f6f9;--line:#dce5ec;--blue:#367da2;--red:#bd4337;--teal:#187d78}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:82px}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.8 system-ui,-apple-system,BlinkMacSystemFont,'Noto Sans CJK KR','Malgun Gothic',sans-serif}a{color:#176b96;text-underline-offset:3px}button,select{font:inherit}button{cursor:pointer}header{background:var(--navy);color:white;padding:44px max(24px,calc((100% - 1140px)/2)) 38px}header h1{font-size:clamp(29px,4vw,44px);line-height:1.3;letter-spacing:-1.1px;margin:12px 0}header p{max-width:920px;color:#d9e5ef;margin:10px 0}.eyebrow{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#a9d6dc}.meta{font-size:13px;color:#b9cddd;margin-top:20px;display:flex;gap:18px;flex-wrap:wrap}nav{position:sticky;top:0;z-index:3;background:#fff;border-bottom:1px solid var(--line)}.nav-inner{max-width:1188px;margin:auto;display:flex;gap:23px;padding:13px 24px;align-items:center;overflow-x:auto}nav a{white-space:nowrap;text-decoration:none;color:var(--muted);font-size:14px;font-weight:600}.print-button{margin-left:auto;white-space:nowrap;background:#eef3f7;color:var(--navy);border:0;border-radius:7px;padding:5px 12px;font-size:13px}main{max-width:1188px;margin:24px auto 70px;padding:0 24px}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.metric{border:1px solid var(--line);border-radius:12px;background:white;padding:19px 21px}.metric .label{font-size:13px;color:var(--muted)}.metric .value{font-weight:750;font-size:31px;color:var(--navy);line-height:1.5}.metric .sub{font-size:12px;color:var(--muted)}section{margin-top:26px;padding:28px 32px;background:var(--paper);border:1px solid var(--line);border-radius:14px}h2{font-size:25px;line-height:1.4;letter-spacing:-.5px;margin:0 0 18px}h3{font-size:19px;line-height:1.5;margin:26px 0 10px}p{margin:12px 0}.section-number{color:var(--teal);font-size:13px;font-weight:700;margin-bottom:7px}.lead{font-size:18px}.callout{border-left:4px solid var(--teal);background:#f0f8f7;border-radius:4px;padding:14px 18px;margin:20px 0}.callout.caution{border-color:#b87737;background:#fff8ef}.callout strong{color:var(--navy)}.small{font-size:13px;color:var(--muted)}code{font-size:.88em;background:#eef3f7;border-radius:4px;padding:2px 5px;overflow-wrap:anywhere}.formula{border:1px solid var(--line);background:#f8fafc;padding:15px 18px;border-radius:8px;margin:17px 0;font:14px/1.8 ui-monospace,monospace;overflow-x:auto}.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:8px;margin:16px 0}.data-table{width:100%;border-collapse:collapse;font-size:14px;text-align:left}.data-table th{background:#edf3f7;color:var(--navy);font-size:13px;white-space:nowrap;text-align:left}.data-table th,.data-table td{padding:11px 13px;border-bottom:1px solid #e6edf2;vertical-align:top}.data-table tr:last-child td{border-bottom:0}.data-table td:first-child{white-space:nowrap;font-weight:600}.data-table tbody tr:hover{background:#f8fbfd}.workflow{padding:0;margin:20px 0;list-style:none;display:grid;grid-template-columns:repeat(4,1fr);gap:10px;counter-reset:step}.workflow li{counter-increment:step;border:1px solid var(--line);border-radius:8px;padding:12px;font-size:13px;background:#f7fafc}.workflow li:before{content:counter(step);display:block;font-weight:750;color:var(--teal);font-size:20px}.workflow strong{display:block;color:var(--navy)}.branch{display:grid;grid-template-columns:1fr 1fr;gap:14px}.branch>div{padding:16px;border:1px solid var(--line);border-radius:8px}.branch p{font-size:14px;margin:7px 0}.figure-card{margin:24px 0 0;border:1px solid var(--line);border-radius:10px;overflow:hidden;background:white}.figure-card figcaption{padding:13px 16px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;gap:14px;align-items:center;font-size:14px}.figure-card figcaption a{font-size:12px;white-space:nowrap}.figure-button{padding:10px;border:0;background:white;display:block;width:100%}.figure-button img{display:block;width:100%;height:auto}.figure-button:focus-visible{outline:3px solid var(--teal);outline-offset:-3px}.caption{font-size:13px;color:var(--muted);padding:10px 17px 15px;margin:0;border-top:1px solid #edf1f5}.condition{font-weight:650;padding:3px 8px;border-radius:15px;font-size:12px}.condition.masl{background:#e8f2f7;color:var(--blue)}.condition.mash{background:#fbece9;color:var(--red)}.filter-row{display:flex;align-items:center;gap:12px;flex-wrap:wrap}.filter-row select{font-size:13px;border:1px solid var(--line);border-radius:6px;background:white;padding:5px 10px}.source-list,.artifact-list{font-size:14px;padding-left:22px;overflow-wrap:anywhere}.artifact-list{columns:2;column-gap:35px}.artifact-list li{break-inside:avoid;margin-bottom:8px}.source-list li{margin:5px 0}details{border:1px solid var(--line);border-radius:8px;padding:13px 16px;margin:17px 0}summary{cursor:pointer;font-weight:650;color:var(--navy);font-size:14px}details[open] summary{margin-bottom:10px}.interpretation{font-size:17px;border-top:1px solid var(--line);padding-top:16px}.quote{font-size:15px;padding:20px;border-radius:8px;background:#f4f7fa;border:1px solid var(--line)}footer{font-size:12px;color:var(--muted);margin-top:25px;overflow-wrap:anywhere}dialog{width:min(95vw,1400px);max-height:94vh;border:0;border-radius:12px;padding:15px;background:white;box-shadow:0 12px 70px #0004}dialog::backdrop{background:#102134aa}dialog img{width:100%;height:auto}dialog .close-dialog{position:sticky;top:0;display:block;margin:0 0 10px auto;border:0;border-radius:6px;background:var(--navy);color:white;padding:5px 12px}
@media(max-width:760px){header{padding:28px 20px}.nav-inner{gap:16px;padding:11px 18px}main{padding:0 14px}.metrics{grid-template-columns:1fr 1fr}.metric{padding:14px}.metric .value{font-size:26px}section{padding:22px 19px}.workflow{grid-template-columns:1fr 1fr}.branch{grid-template-columns:1fr}.artifact-list{columns:1}.figure-card figcaption{align-items:flex-start}.data-table{font-size:12px}.data-table th,.data-table td{padding:9px 10px}.print-button{display:none}}
@media print{body{background:white;font-size:10pt}header{background:white;color:var(--navy);padding:0 0 15px}header p,.eyebrow,.meta{color:var(--ink)}header h1{font-size:26pt}nav,.filter-row,dialog{display:none!important}main{padding:0;margin:0;max-width:none}.metric{padding:10px}.metric .value{font-size:22pt}section{border:0;border-radius:0;padding:20px 0;margin-top:10px;break-inside:auto}h2,h3{break-after:avoid}.figure-card,.metric,.callout,.branch{break-inside:avoid}.figure-card{max-width:100%}.figure-card img{max-height:230mm;object-fit:contain}.caption{font-size:9pt}.data-table{font-size:9pt}.table-wrap{overflow:visible}.data-table tr{break-inside:avoid}.artifact-list{columns:1}details{display:block}a{color:var(--ink)}}
'''

html_template = Template(r'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>HwangBJ | 간 핵·PBMC 분석 보고서</title><meta name="description" content="간 핵과 PBMC의 독립 Harmony 분석, myeloid 분류, 참조 DEG 기반 SLC7A5-high 후보 주석 및 MASL·MASH donor-level 비교 결과.">
<style>$style</style></head><body>
<header><div class="eyebrow">SLC7A5 MONOCYTE · HWANGBJ COHORT</div>
<h1>간 핵과 PBMC에서<br>SLC7A5-high monocyte 후보 찾기</h1>
<p>검체별 독립 분석 → marker 기반 myeloid 분류 → PBMC 참조 DEG matching → MASL·MASH donor별 비율 비교</p>
<div class="meta"><span>저장된 결과 기준: $date</span><span>간 핵 MASL 4명 · PBMC MASL 4명/MASH 4명</span><span>그림은 HTML에 포함</span></div></header>
<nav aria-label="보고서 목차"><div class="nav-inner"><a href="#overview">핵심 결과</a><a href="#data">데이터 구성</a><a href="#method">분류 방법</a><a href="#liver">간 핵 결과</a><a href="#annotation">PBMC 주석</a><a href="#comparison">MASL·MASH 비교</a><a href="#files">근거 파일</a><button type="button" class="print-button" id="print-report">인쇄 / PDF</button></div></nav>
<main><div class="metrics" aria-label="주요 수치"><div class="metric"><div class="label">간 핵 QC 통과</div><div class="value">$liver_qc_n</div><div class="sub">MASL donor 4명</div></div><div class="metric"><div class="label">PBMC QC 통과</div><div class="value">$pbmc_qc_n</div><div class="sub">MASL·MASH donor 총 8명</div></div><div class="metric"><div class="label">PBMC 참조 기반 후보</div><div class="value">$high_n</div><div class="sub">통합 cluster $cluster · 잠정적 주석</div></div><div class="metric"><div class="label">Donor-level 비교 P</div><div class="value">$pvalue</div><div class="sub">양측 exact permutation</div></div></div>
<section id="overview"><div class="section-number">01 · 결과를 읽는 기준</div><h2>MASH에서 비율은 높았지만, 유의한 차이는 확인되지 않았다</h2>
<p class="lead">PBMC에서 참조 기반 후보의 donor별 평균 비율은 MASL <strong>$masl_mean%</strong>, MASH <strong>$mash_mean%</strong>였다. 평균 차이는 <strong>+$difference percentage points</strong>였으며, 95% CI는 <strong>$ci_low~$ci_high</strong>, 양측 P 값은 <strong>$pvalue</strong>였다.</p>
<div class="branch"><div><strong>간 핵: 분류의 한계가 남음</strong><p>Marker 검토 후 myeloid 234개 핵이 남았지만 monocyte 후보를 자동 선택하지 못했다. 따라서 간 핵의 SLC7A5-high monocyte 주석 및 MASL·MASH 비교는 수행하지 않았다.</p></div><div><strong>PBMC: donor별 조성 비교를 수행</strong><p>Myeloid/monocyte 후보 3,891개 중 cluster $cluster의 $high_n개 세포를 주 참조에 가장 유사한 후보로 지정했다. 비교의 생물학적 반복 수는 세포 수가 아닌 각 군 donor 4명이다.</p></div></div>
<div class="callout caution"><strong>주석은 잠정적이다.</strong> 주 참조 상관은 ρ=$rho로 높지 않고 보조 참조는 다른 cluster를 선택한다. <code>SLC7A5_high_monocyte</code>는 참조 matching으로 붙인 분석상 이름이며, 실제 SLC7A5 발현이 가장 높은 cluster라는 뜻이나 기존 세포형의 확정 검증을 의미하지 않는다.</div></section>
<section id="data"><div class="section-number">02 · 데이터와 분석 범위</div><h2>4개 RDS는 두 검체의 counts·metadata 쌍이다</h2>
<p>간 핵(snRNA-seq)과 PBMC(scRNA-seq)는 검체 및 측정 방식이 달라 <strong>서로 합치지 않고 각각 처리</strong>했다. 아래 관측 수는 제공된 count matrix/metadata의 관측 수이며, 원시 FASTQ에서 처음 회수된 전체 수를 의미하지 않는다.</p>
$source_table
<div class="callout"><strong>원본 간 핵에도 MASH가 있다.</strong> 다만 현재 간 핵 실행은 MASL1–4만 포함한다. MASL·MASH를 함께 분석하고 비교한 결과는 PBMC에 해당한다.</div>
<h3>원본 파일</h3>$source_links<h3>실제로 포함된 metadata</h3>$metadata_table
<p><code>MASL1–4</code>, <code>MASH1–4</code>의 숫자는 donor ID이다. 두 metadata에는 fibrosis stage(F0–F4), NAS, 나이·성별 등 임상 공변량이 없다. <code>Condition</code>은 MASL/MASH 질환군 구분이며 수치형 severity stage가 아니다.</p>
<h3>현재 실행에서 사용한 데이터 규모</h3>$qc_table</section>
<section id="method"><div class="section-number">03 · 공통 전처리와 myeloid 분류</div><h2>검체 안에서 donor Harmony를 적용하고 marker로 분류했다</h2>
<ol class="workflow"><li><strong>RDS 읽기</strong>counts/metadata barcode를 정렬하고 sparse AnnData로 변환</li><li><strong>QC·정규화</strong>검출 유전자와 미토콘드리아 비율을 검사</li><li><strong>전체 클러스터링</strong>HVG → PCA → donor Harmony → Leiden</li><li><strong>Myeloid 후보</strong>경쟁 lineage signature와 양의 myeloid score로 선택</li><li><strong>Myeloid 재분석</strong>HVG/PCA/Harmony를 새로 계산</li><li><strong>Marker 검토</strong>canonical myeloid·monocyte/DC marker 검토</li><li><strong>PBMC 참조 주석</strong>donor × cluster pseudobulk 효과를 참조 DEG와 비교</li><li><strong>질환군 비교</strong>MASL/MASH 각 donor의 후보 비율로 검정</li></ol>
<details><summary>QC와 클러스터링 설정</summary><p>검출 유전자 수 ≥200, 미토콘드리아 UMI 비율 ≤10%를 적용했다. 유전자는 3개 이상의 관측에서 검출될 때 유지했다. Library size를 10,000으로 정규화하고 log1p 변환했다. 입력 자료의 기존 QC 여부와 별개로 현재 기준을 재확인했으며 doublet 제거를 수행한 것으로 간주하지 않았다.</p><p>Donor별 batch-aware HVG 최대 2,000개를 고르고 <strong>SLC7A5를 HVG/PCA에서 제외</strong>했다. HVG scaling(max_value=10) 후 PCA 최대 30개 성분을 사용했다. Harmony는 <code>donor</code>를 batch key로 사용했다(θ=2, max_iter=20, seed=42). <code>X_pca_harmony</code>를 neighbors/UMAP/Leiden에 사용했으며 전체 Leiden resolution=0.6, myeloid resolution=0.5였다.</p><p>Harmony는 PCA 공간을 보정한다. 원본 UMI는 <code>layers['counts']</code>, 발현 확인은 log-normalized 값으로 유지했다. Donor 간 차이에는 생물학적 차이도 포함될 수 있어 보정 전후 UMAP과 marker를 함께 저장했다.</p></details>
<h3>전체 PBMC/간 핵에서 myeloid 후보를 선택한 기준</h3><p>각 lineage panel을 <code>scanpy.tl.score_genes</code>로 점수화하고 cluster 평균을 비교했다. Myeloid score가 가장 높고 양수인 cluster를 초기 후보로 선택했다. NK와 공유하는 TYROBP/FCER1G만으로 결정하지 않고 T, NK, B, 간세포 등 경쟁 lineage를 함께 검토했다.</p>
<details><summary>전체 lineage marker panel</summary>$lineage_table</details>
<h3>재클러스터링 후 myeloid marker 검토</h3><p><strong>SPI1, CSF1R, LST1, CTSS, FCER1G, TYROBP</strong> 중 3개 이상이 cluster 관측의 10% 이상에서 검출되고, dominant lineage가 Myeloid이며 평균 score가 양수인 cluster를 남겼다. 이 조건을 만족하지 않는 cluster는 myeloid 후보에서 제외했다.</p>
<h3>Monocyte와 macrophage/DC subtype 구분</h3><p>Subtype signature의 cluster 평균이 가장 높은 panel을 후보 주석으로 사용했다. 모든 subtype score가 0 이하이면 <code>Unresolved_myeloid</code>로 표시했다. Classical 후보에서 CD14/FCN1/VCAN 검출률의 최댓값이 10% 미만이거나 non-classical 후보에서 FCGR3A 검출률이 10% 미만이면 <code>Monocyte_DC_ambiguous</code>로 표시했다. PBMC 참조 matching에는 marker 지지가 있는 classical/non-classical 후보만 허용했다.</p>
<details><summary>Myeloid subtype marker panel</summary>$myeloid_table</details>
<p class="small">Cluster top-marker ranking은 기술통계용 logFC만 내보냈다. 이 cell-level ranking의 P 값을 질환군 차이나 biological DE의 근거로 사용하지 않았다. 자동 signature 주석은 검토용 후보이며 확정 cell type 분류가 아니다.</p></section>
<section id="liver"><div class="section-number">04 · 간 핵 snRNA-seq 결과</div><h2>Myeloid는 남았지만 monocyte 후보는 정의하지 못했다</h2>
<p>MASL1–4의 <strong>10,442개 핵</strong>을 읽어 QC 후 <strong>10,096개</strong>를 유지했다. 전체 cluster 13에서 초기 myeloid $initial_liver개 핵을 선택했다. 재클러스터링에서 hepatocyte signature가 우세했던 cluster 0(56개)과 5(31개), 총 $excluded_liver개를 제외하여 <strong>234개</strong>를 남겼다.</p>
$liver_donor_table$liver_subtype_table
<p>최종 후보는 Kupffer cell <strong>161개</strong>, LAM <strong>37개</strong>, cDC2 <strong>36개</strong>였다. 현재 자동 기준으로 monocyte cluster를 선택하지 못했으므로 SLC7A5-high monocyte의 개수·비율을 0으로 단정하지 않고 <strong>정의 불가</strong>로 기록했다.</p>
$liver_fig
<div class="callout caution">이 결과는 간에서 monocyte가 생물학적으로 없거나 SLC7A5가 발현되지 않는다는 의미가 아니다. 현재 제공된 nuclei 데이터와 분류 기준에서 monocyte 후보를 확보하지 못한 결과이다. 간 핵에서 MASL·MASH 군 간 비교도 수행하지 않았다.</div></section>
<section id="annotation"><div class="section-number">05 · PBMC SLC7A5-high 후보 주석</div><h2>참조 DEG의 방향과 가장 유사한 cluster를 선택했다</h2>
<p>MASL1–4와 MASH1–4의 <strong>24,492개 세포</strong>는 모두 현재 QC를 통과했다. 전체 cluster 0/1에서 myeloid <strong>3,891개</strong>를 선택하고 재클러스터링했다. 최종 8개 cluster는 모두 classical/non-classical monocyte marker 지지를 보여 monocyte 후보 3,891개를 주 분석의 분모로 사용했다.</p>
$pbmc_cluster_table
<h3>기존 scRNA-seq 결과를 참조한 방식</h3><p>주 참조는 <code>scmono5_DEG.csv</code>의 mono5/SLC7A5-high vs rest 효과였다. <code>MASLD_mono_DEG_allclusters.csv</code>의 <code>SLC7A5_high_monocyte</code> logFC와 일치하는지 확인하고 검출률 정보를 결합했다. <code>DEG_Special_monocyte_vs_Classical_monocyte.csv</code>는 보조 참조로 사용했다.</p>
<details><summary>참조 DEG 파일</summary>$references</details>
<p>PBMC의 <strong>donor × cluster별 raw UMI를 합산</strong>했다. 각 donor 안에서 해당 cluster와 나머지 myeloid의 CPM을 비교하고, donor별 효과를 동일한 가중치로 평균했다. 이 signed effect를 참조 signed logFC와 같은 유전자 순서로 정렬하여 Spearman 상관을 계산했다.</p>
<div class="formula">Donor별 효과 = log2[(CPM_cluster + 1) / (CPM_other_myeloid + 1)]<br>Cluster profile = donor별 효과의 평균<br>Matching score = Spearman(reference signed logFC, cluster profile)</div>
<p>주 참조의 필터는 BH-adjusted P&lt;0.05, |logFC|≥0.5, 참조 어느 그룹에서든 검출률 ≥5%, PBMC 전체 검출률 ≥1%였다. <strong>SLC7A5 자체와 MT-/RPS/RPL prefix 유전자</strong>는 matching에서 제외했다. 주 참조에서 공통 유전자 <strong>$n_genes개</strong>를 사용했다. 여기서 참조 BH 값은 기존 DEG 필터용이며 MASL/MASH 조성 비교에 BH를 적용했다는 뜻이 아니다.</p>
$ref_fig
<details><summary>8개 cluster의 참조별 상관계수 표</summary>$correlation_table</details>
<h3>선택 및 후속 분석 연결</h3><p>Marker 지지가 있는 monocyte cluster 중 주 참조에 가장 높은 양의 상관을 보인 <strong>cluster $cluster(ρ=$rho, $high_n개 세포)</strong>를 선택했다. MASL/MASH별 빈도나 P 값은 선택에 사용하지 않았다. <code>celltype_refined</code>에 <code>SLC7A5_high_monocyte</code>를 지정하고 <code>SLC7A5_reference_cluster</code>, <code>SLC7A5_high_candidate</code>와 후속 donor별 비율·pseudobulk·gene ranking을 같은 집단으로 연결했다.</p>
<p>단일 유전자 SLC7A5 양성 발현값의 pooled 75백분위 gate는 <code>SLC7A5_expression_high_q75</code>에 보존했다. 이 보조 gate의 $q75_total개 세포와 참조 cluster의 $high_n개 세포는 서로 다른 정의이다. CD14-high/FCGR3A-low/SLC7A5-expression-high triple gate도 보조 지표로 저장했다.</p>
$stability_fig$annotation_fig
<div class="callout caution"><strong>안정적인 최상위 선택과 확정적인 세포형 검증은 다르다.</strong> 8명과 leave-one-donor-out 모두 cluster $cluster를 선택했지만 주 참조 상관은 낮다. 보조 vs-Classical 참조는 cluster $secondary_best를 선택했고, cluster $cluster의 보조 상관은 $secondary_rho이다. Marker 그림과 단일 유전자 발현이 이 후보를 독립적으로 확정했다고 해석하지 않는다.</div>
$history_section</section>
<section id="comparison"><div class="section-number">06 · MASL·MASH donor-level 조성 비교</div><h2>세포를 합쳐 검정하지 않고 donor마다 비율 하나를 계산했다</h2>
<div class="formula">Donor별 후보 비율(%) = 100 × cluster $cluster 세포 수 / 해당 donor의 전체 monocyte 후보 수<br>주 효과 = MASH donor들의 평균 비율 − MASL donor들의 평균 비율</div>
<p>독립 donor ID 8명을 생물학적 반복으로 취급했다. 같은 숫자의 MASL1/MASH1을 자동으로 paired donor로 간주하지 않았다. 각 donor는 한 번씩 포함했고 포착 세포 수로 가중하지 않았다.</p>
<div class="filter-row"><label for="condition-filter">Donor 표 표시</label><select id="condition-filter"><option value="all">전체 8명</option><option value="MASL">MASL 4명</option><option value="MASH">MASH 4명</option></select><span class="small">필터는 표 표시만 변경하며 아래 통계는 전체 8명 기준이다.</span></div>
$donor_table$group_table
<h3>검정과 효과 크기</h3><p>평균 비율 차이에 대해 8명 중 4명을 각 군에 배정하는 <strong>70개 donor label 배치</strong>를 전수 계산했다. |null 차이|가 |관찰 차이| 이상인 배치의 비율을 양측 exact permutation P로 사용했다. Pooled Fisher나 cell-level Wilcoxon/Mann–Whitney를 주 검정으로 사용하지 않았다.</p>
<p>95% CI는 각 질환군 안에서 donor 4명을 복원 추출하는 <strong>65,536개 조합</strong>의 평균 차이 분포에서 2.5/97.5백분위로 구했다. 이는 donor bootstrap CI이며 cell-level binomial CI가 아니다. 주 비교는 monocyte 분모 한 가지이므로 별도 BH 보정은 적용하지 않았다.</p>
$comparison_fig
<p class="interpretation"><strong>현재 결과:</strong> 평균 비율 차이는 +$difference percentage points, 95% CI $ci_low~$ci_high, P=$pvalue였다. MASH에서 평균 비율이 높았지만 <strong>통계적으로 유의한 증가를 확인하지 못했다</strong>. 이 결과만으로 차이가 없다고 입증하거나 질병 진행에 따른 시간적 증가를 주장할 수 없다.</p>
$counts_fig
<details><summary>민감도 확인 및 해석 범위</summary><p>Donor를 한 명씩 제외해도 평균 차이의 방향은 모두 양수였다. 그러나 이 분석은 새로운 유의성을 주장하는 검정이 아닌 효과 방향의 기술적 확인이다. Myeloid/전체 QC PBMC를 분모로 한 비율과 expression-q75 gate도 표로 저장했고, 분모별 최솟값 P를 선택하지 않았다.</p><p>이번 PBMC에서는 myeloid와 monocyte 후보가 모두 3,891개라 두 분모의 비율이 같다. 전체 PBMC를 분모로 한 비율은 다른 질문을 답하므로 주 결과와 구분한다. 포착 수는 혈액의 절대 세포 수가 아니다. 각 군 donor 4명, 낮은 참조 상관, 보조 참조 불일치, 임상 공변량의 부재를 고려해 탐색적 관찰로 해석한다.</p></details>
<h3>보고서·답변에 사용할 수 있는 설명</h3><div class="quote">PBMC에서 MASL 및 MASH 각각 4명의 donor를 포함하여 donor별 Harmony 보정과 myeloid 재클러스터링을 수행하였다. 기존 SLC7A5-high monocyte DEG의 signed effect profile과 가장 유사한 marker-supported monocyte cluster를 잠정적 참조 후보로 주석하였다. 각 donor의 전체 monocyte 중 후보 비율을 계산하고 donor 단위 exact permutation으로 질환군을 비교하였다. MASH의 평균 비율은 MASL보다 높았으나(40.27% 대 33.32%), 평균 차이 6.95 percentage points는 유의하지 않았다(양측 P=0.257, donor bootstrap 95% CI −3.21~16.27). 참조 일치도가 낮으므로 세포형 주석과 질환군 차이는 탐색적으로 해석하였다.</div></section>
<section id="files"><div class="section-number">07 · 근거 파일과 후속 분석 상태</div><h2>현재 실행과 이전 실행을 구분해 보존했다</h2>
<p>간 핵은 <code>liver_nuclei/harmony/</code>, 최신 MASL/MASH PBMC는 <code>pbmc/harmony_MASL_MASH/</code>에 저장되어 있다. 이전 MASL-only PBMC의 <code>pbmc/harmony/</code> 및 backup notebook은 보존했다. 이 보고서는 최신 저장 결과를 읽어 작성했으며 원본 데이터나 분석을 다시 변경하지 않았다.</p>
$artifacts
<div class="callout"><strong>후속 분석 준비:</strong> donor × high/other raw-count pseudobulk와 gene ranking은 저장했다. 최소 20개 관측의 group을 DE용 eligibility로 기록했다. 이것은 donor를 포함한 paired pseudobulk DESeq2/edgeR 검정이나 GSEA를 실제 수행했다는 뜻이 아니다. 새 cluster DEG 파일은 donor-average 효과를 기록한 기술통계 profile이다.</div>
<footer>생성: $generated · HwangBJ_build_report.py<br>주 비교 JSON SHA-256: $sha<br>이미지와 스타일은 HTML에 포함되어 인터넷 없이 열 수 있다. CSV·PDF·코드 링크는 이 보고서를 현재 프로젝트 경로에서 열 때 연결된다. 그림을 누르면 확대되고 브라우저 인쇄로 PDF를 저장할 수 있다.</footer></section></main>
<dialog id="figure-dialog" aria-label="그림 확대"><button type="button" class="close-dialog">닫기</button><img alt=""></dialog>
<script>
document.getElementById('print-report').addEventListener('click',()=>window.print());
const dialog=document.getElementById('figure-dialog');
document.querySelectorAll('.figure-button').forEach(button=>button.addEventListener('click',()=>{const source=button.querySelector('img');const target=dialog.querySelector('img');target.src=source.src;target.alt=source.alt;dialog.showModal();}));
dialog.querySelector('button').addEventListener('click',()=>dialog.close());
dialog.addEventListener('click',event=>{if(event.target===dialog)dialog.close();});
document.getElementById('condition-filter').addEventListener('change',event=>{document.querySelectorAll('#donor-table tbody tr').forEach(row=>{const condition=row.querySelector('.condition').textContent;row.hidden=event.target.value!=='all'&&condition!==event.target.value;});});
window.addEventListener('beforeprint',()=>{document.querySelectorAll('details').forEach(item=>{item.dataset.printWasOpen=String(item.open);item.open=true;});document.querySelectorAll('#donor-table tbody tr').forEach(row=>{row.dataset.printWasHidden=String(row.hidden);row.hidden=false;});});
window.addEventListener('afterprint',()=>{document.querySelectorAll('details').forEach(item=>{item.open=item.dataset.printWasOpen==='true';});document.querySelectorAll('#donor-table tbody tr').forEach(row=>{row.hidden=row.dataset.printWasHidden==='true';});});
</script></body></html>''')
now = datetime.now(ZoneInfo('Asia/Seoul'))
values = dict(style=style,date=now.strftime('%Y-%m-%d'),generated=now.strftime('%Y-%m-%d %H:%M KST'),
    liver_qc_n=f'{liver["QC_n"]:,}',pbmc_qc_n=f'{pbmc["QC_n"]:,}',high_n=f'{matching["n_annotated_cells"]:,}',
    cluster=escape(cluster),pvalue=f'{comparison["p_value"]:.3f}',
    masl_mean=f'{comparison["MASL_mean_pct"]:.2f}',mash_mean=f'{comparison["MASH_mean_pct"]:.2f}',
    difference=f'{comparison["mean_difference_pct_points"]:.2f}',
    ci_low=f'{comparison["mean_difference_95CI_low"]:.2f}',ci_high=f'{comparison["mean_difference_95CI_high"]:.2f}',
    rho=f'{primary_rho:.3f}',secondary_best=secondary_best,secondary_rho=f'{secondary_selected:.3f}',
    source_table=source_table,source_links=source_links,metadata_table=metadata_table,qc_table=qc_table,
    lineage_table=lineage_table,myeloid_table=myeloid_table,initial_liver=initial_liver,excluded_liver=excluded_liver,
    liver_subtype_table=liver_subtype_table,liver_donor_table=liver_donor_table,liver_fig=liver_fig,
    pbmc_cluster_table=pbmc_cluster_table,references=references,n_genes=f'{matching["n_primary_genes"]:,}',
    ref_fig=ref_fig,correlation_table=correlation_table,stability_fig=stability_fig,annotation_fig=annotation_fig,
    history_section=Template('<details><summary>이전 MASL-only cluster 3와 왜 달라졌는가</summary><p>이전에는 MASL donor 4명만 분석하여 cluster 3의 $old_total개 세포를 후보로 선택했다(주 참조 ρ=$old_rho). MASH를 추가하면서 HVG·Harmony·클러스터링·참조 matching을 다시 실행했으므로 번호와 집단 경계가 모두 달라질 수 있다.</p><p>이전 후보 $old_total개 중 $old_to_0개는 통합 cluster 0, $old_to_selected개는 통합 cluster $cluster에 속한다. 따라서 기존 cluster 3가 통합 cluster $cluster로 단순히 이름만 바뀐 것으로 보지 않는다. 아래 표는 공유 barcode의 실제 대응이다.</p>$correspondence_table</details>').safe_substitute(old_total=old_high_total, old_rho=f'{old_matching["primary_rho"]:.3f}', old_to_0=old_to_0, old_to_selected=old_to_selected, cluster=cluster, correspondence_table=correspondence_table) if old_matching is not None and correspondence is not None else '<details><summary>이전 MASL-only 분석</summary><p>이전 결과가 제공되지 않아 barcode 대응은 표시하지 않습니다.</p></details>',
    old_total=old_high_total,old_rho=f'{old_matching["primary_rho"]:.3f}' if old_matching else 'NA',old_to_0=old_to_0,
    old_to_selected=old_to_selected,correspondence_table=correspondence_table,q75_total=q75_total,
    donor_table=donor_table_html,group_table=group_table,comparison_fig=comparison_fig,counts_fig=counts_fig,
    artifacts=artifacts,sha=hashlib.sha256((COMP/'MASL_MASH_primary_comparison.json').read_bytes()).hexdigest())
OUTPUT.write_text(html_template.substitute(values),encoding='utf-8')
print(f'Created {OUTPUT} ({OUTPUT.stat().st_size/1024/1024:.2f} MiB; embedded figures, offline styles, relative evidence links)')
