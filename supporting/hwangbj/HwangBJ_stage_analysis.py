"""Donor-level clinical-stage analysis for the frozen PBMC reference annotation.

Each donor contributes one proportion. Captured cell counts are descriptive;
they are not absolute blood cell counts or biological replicates.
"""
from math import factorial

import numpy as np
import pandas as pd
from scipy import stats


def attach_clinical_stage(frequencies, clinical):
    """Join explicit clinical measurements; never derive stage from donor IDs."""
    required = {'donor', 'stage'}
    if not required.issubset(clinical.columns):
        raise ValueError('Clinical metadata needs donor and stage columns.')
    clinical = clinical.copy()
    if clinical.donor.isna().any():
        raise ValueError('Clinical metadata has a missing donor ID.')
    clinical['donor'] = clinical.donor.astype(str).str.strip()
    if clinical.donor.eq('').any() or clinical.donor.duplicated().any():
        raise ValueError('Clinical metadata must have exactly one row per donor.')
    raw = clinical.stage.replace(r'^\s*$', np.nan, regex=True)
    clinical['stage'] = pd.to_numeric(raw, errors='coerce')
    invalid = raw.notna() & (clinical.stage.isna() | ~np.isfinite(clinical.stage))
    if invalid.any():
        raise ValueError('Stage must be an explicit finite numeric clinical measurement: '
                         + ', '.join(clinical.loc[invalid, 'donor']))
    for name in ['stage_label', 'stage_source']:
        if name not in clinical:
            clinical[name] = ''
        clinical[name] = clinical[name].fillna('').astype(str)
    result = frequencies.copy()
    result.index.name = 'donor'
    result = result.reset_index()
    if result.donor.duplicated().any():
        raise ValueError('Frequencies must have exactly one row per donor.')
    if 'condition' in clinical:
        supplied = clinical.set_index('donor').condition.dropna()
        actual = result.set_index('donor').condition
        shared = supplied.index.intersection(actual.index)
        if not supplied.loc[shared].astype(str).eq(actual.loc[shared].astype(str)).all():
            raise ValueError('Supplied condition disagrees with the source metadata.')
    result = result.merge(clinical[['donor', 'stage', 'stage_label', 'stage_source']],
                          on='donor', how='left', validate='one_to_one')
    result['stage_available'] = result.stage.notna()
    extra = sorted(set(clinical.donor) - set(result.donor))
    return result, extra


def donor_stage_trend(table, outcome='high_pct_of_monocyte', seed=42,
                      max_exact=100000, n_resamples=100000):
    """Spearman trend, donor-pair permutation P, and Theil-Sen slope/95% CI.

    Exact tests enumerate all donor pairings (<= max_exact), including ties.
    Otherwise Monte Carlo pairings use a fixed seed and +1 correction.
    Two-sided P is the probability of |rho_null| >= |rho_observed|.
    Slope CI is SciPy's rank-based Theil-Sen interval, not a cell-level CI.
    """
    included = table.loc[table.stage.notna() & table[outcome].notna()].copy()
    result = {
        'status': 'pending_clinical_stage', 'test_performed': False,
        'experimental_unit': 'donor', 'outcome': outcome,
        'n_total_donors': len(table), 'n_included_donors': len(included),
        'included_donors': included.donor.tolist(),
        'excluded_donors': table.loc[~table.donor.isin(included.donor), 'donor'].tolist(),
        'alternative': 'two-sided', 'primary_test_count': 1,
        'note': 'Cell counts do not enter the hypothesis-test sample size.',
    }
    if included.empty:
        return result
    if len(included) < 3:
        result['status'] = 'insufficient_donors_with_stage'
        return result
    x = included.stage.to_numpy(dtype=float)
    y = included[outcome].to_numpy(dtype=float)
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError('Non-finite donor stage or outcome.')
    if np.unique(x).size < 2:
        result['status'] = 'no_stage_variation'
        return result
    if np.unique(y).size < 2:
        result['status'] = 'no_frequency_variation'
        return result
    rx, ry = stats.rankdata(x), stats.rankdata(y)
    rx, ry = rx - rx.mean(), ry - ry.mean()
    norm = float(np.linalg.norm(rx) * np.linalg.norm(ry))

    def statistic(permuted, axis=-1):
        return np.sum(permuted * ry, axis=axis) / norm

    exact = factorial(len(included)) <= max_exact
    perm = stats.permutation_test(
        (rx,), statistic, permutation_type='pairings', vectorized=True,
        n_resamples=np.inf if exact else n_resamples,
        batch=2000, random_state=seed, alternative='two-sided')
    rho = float(np.dot(rx, ry) / norm)
    exceedances = int(np.count_nonzero(np.abs(perm.null_distribution) >= abs(rho) - 1e-12))
    total = len(perm.null_distribution)
    pvalue = exceedances / total if exact else (exceedances + 1) / (total + 1)
    slope = stats.theilslopes(y, x, alpha=0.95, method='joint')
    result.update({
        'status': 'analysed', 'test_performed': True, 'spearman_rho': rho,
        'p_value': float(pvalue),
        'p_value_method': 'exact donor-pairing permutation, absolute rho' if exact
                          else 'Monte Carlo donor-pairing permutation, absolute rho, +1 correction',
        'n_permutations': total, 'seed': seed,
        'theil_sen_slope_pct_points_per_stage_unit': float(slope.slope),
        'slope_95CI_low': float(slope.low_slope),
        'slope_95CI_high': float(slope.high_slope),
        'slope_CI_method': 'SciPy Theil-Sen rank-based slope interval',
        'intercept': float(slope.intercept),
        'positive_association_p_lt_0_05': bool(rho > 0 and pvalue < .05),
        'interpretation': 'exploratory donor-level association; not longitudinal progression',
    })
    return result


def plot_donor_counts_and_frequencies(table, stage_name='MASLD stage'):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    positions = np.arange(len(table))
    axes[0].bar(positions, table.high_n, color='#bd4337', width=.65)
    axes[0].set_ylabel('Captured SLC7A5-high cells (n)')
    axes[0].set_title('Cluster 3: captured cell counts')
    axes[1].scatter(positions, table.high_pct_of_monocyte, color='#bd4337', s=65)
    axes[1].set_ylabel('SLC7A5-high / all monocytes (%)')
    axes[1].set_title('One observation per donor')
    for i, row in table.reset_index(drop=True).iterrows():
        axes[0].annotate(str(int(row.high_n)), (i, row.high_n),
                         xytext=(0, 5), textcoords='offset points', ha='center', fontsize=9)
        axes[1].annotate(f'{int(row.high_n)}/{int(row.monocyte_n)}',
                         (i, row.high_pct_of_monocyte), xytext=(0, 7),
                         textcoords='offset points', ha='center', fontsize=9)
    labels = [f'{r.donor}\n{r.stage_label or f"stage {r.stage:g}"}' if pd.notna(r.stage)
              else r.donor for r in table.itertuples()]
    for ax in axes:
        ax.set_xticks(positions, labels, fontsize=9)
        ax.set_ylim(0, max(ax.get_ylim()[1], 1) * 1.18)
        ax.spines[['top', 'right']].set_visible(False)
    missing = table.loc[table.stage.isna(), 'donor'].tolist()
    caption = ('Clinical stage unavailable: ' + ', '.join(missing)
               if missing else f'Clinical measure: {stage_name}')
    fig.text(.5, .01, caption, ha='center', fontsize=9)
    fig.tight_layout(rect=(0, .055, 1, 1))
    return fig


def plot_stage_trend(table, result, stage_name='MASLD stage'):
    import matplotlib.pyplot as plt

    included = table.loc[table.donor.isin(result['included_donors'])].copy()
    fig, ax = plt.subplots(figsize=(6.8, 5))
    outcome = result['outcome']
    # Display-only jitter separates donors tied at a stage; statistics use actual stages.
    for stage, group in included.groupby('stage', sort=True):
        offsets = np.linspace(-.045, .045, len(group)) if len(group) > 1 else [0]
        for offset, row in zip(offsets, group.itertuples()):
            xpos = stage + offset
            ax.scatter(xpos, getattr(row, outcome), color='#bd4337', s=65, zorder=3)
            ax.annotate(f'{row.donor} ({int(row.high_n)}/{int(row.monocyte_n)})',
                        (xpos, getattr(row, outcome)), xytext=(5, 7),
                        textcoords='offset points', fontsize=8)
    if result['test_performed']:
        xs = np.linspace(included.stage.min(), included.stage.max(), 100)
        ax.plot(xs, result['intercept'] + result['theil_sen_slope_pct_points_per_stage_unit'] * xs,
                '--', color='#666666', label='Theil-Sen descriptive trend')
        title = (f"Cluster 3: SLC7A5-high monocytes; n={len(included)} donors\n"
                 f"Spearman rho={result['spearman_rho']:.3f}, permutation P={result['p_value']:.4g}")
        fig.text(.5, .01,
                 f"Slope: {result['theil_sen_slope_pct_points_per_stage_unit']:.3g} percentage points / stage unit; "
                 f"95% CI [{result['slope_95CI_low']:.3g}, {result['slope_95CI_high']:.3g}]",
                 ha='center', fontsize=8)
        ax.legend(fontsize=8, loc='best')
    else:
        title = f"Stage association not tested: {result['status']}"
    ax.set_title(title, fontsize=11)
    ax.set_xlabel(stage_name)
    ax.set_ylabel('SLC7A5-high / all monocytes (%)')
    stages = sorted(included.stage.unique())
    labels = []
    for stage in stages:
        names = included.loc[included.stage.eq(stage), 'stage_label'].dropna().unique() if 'stage_label' in included else []
        labels.append(str(names[0]) if len(names) == 1 and names[0] else f'{stage:g}')
    ax.set_xticks(stages, labels)
    ax.set_ylim(0, max(1, included[outcome].max() * 1.35))
    ax.margins(x=.2)
    ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout(rect=(0, .05, 1, 1))
    return fig
