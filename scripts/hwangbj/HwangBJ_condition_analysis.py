"""Compare MASL and MASH using independent donors, never pooled cells."""
from itertools import combinations, product

import numpy as np
import pandas as pd


def compare_donor_conditions(table, outcome='high_pct_of_monocyte', seed=42):
    required = {'donor', 'condition', outcome}
    if not required.issubset(table.columns):
        raise ValueError(f'Required columns: {sorted(required)}')
    if table.donor.isna().any() or table.donor.duplicated().any():
        raise ValueError('Each independent donor must occur exactly once.')
    if set(table.condition) != {'MASL', 'MASH'}:
        raise ValueError('Exactly MASL and MASH condition labels are required.')
    values = pd.to_numeric(table[outcome], errors='raise')
    if not np.isfinite(values).all() or not values.between(0, 100).all():
        raise ValueError('Donor percentages must be finite and within 0–100.')
    a = values.loc[table.condition.eq('MASL')].to_numpy(dtype=float)
    b = values.loc[table.condition.eq('MASH')].to_numpy(dtype=float)
    if min(len(a), len(b)) < 2:
        raise ValueError('At least two independent donors are required in each condition.')
    pooled = np.r_[a, b]
    observed = float(b.mean() - a.mean())
    n_a, n_b = len(a), len(b)
    # For four donors per condition, all 70 label allocations are enumerated.
    null_rows = []
    for mash_indices in combinations(range(len(pooled)), n_b):
        mask = np.zeros(len(pooled), dtype=bool)
        mask[list(mash_indices)] = True
        null_rows.append({'MASH_indices': ','.join(map(str, mash_indices)),
                         'mean_difference_pct_points': pooled[mask].mean() - pooled[~mask].mean()})
    null = pd.DataFrame(null_rows)
    p = float((null.mean_difference_pct_points.abs() >= abs(observed) - 1e-12).mean())

    # Independent within-condition donor bootstrap: no cell resampling or cell weights.
    n_boot = n_a**n_a * n_b**n_b
    if n_boot <= 100000:
        means_a = np.asarray([a[list(idx)].mean() for idx in product(range(n_a), repeat=n_a)])
        means_b = np.asarray([b[list(idx)].mean() for idx in product(range(n_b), repeat=n_b)])
        bootstrap = (means_b[:, None] - means_a[None, :]).ravel()
        bootstrap_method = 'percentile, all within-condition donor bootstrap resamples'
    else:
        rng = np.random.default_rng(seed)
        bootstrap = (b[rng.integers(n_b, size=(100000, n_b))].mean(axis=1)
                     - a[rng.integers(n_a, size=(100000, n_a))].mean(axis=1))
        bootstrap_method = 'percentile, 100000 within-condition donor bootstrap resamples'
    low, high = np.quantile(bootstrap, [.025, .975])
    result = {
        'experimental_unit': 'independent donor', 'outcome': outcome,
        'comparison': 'MASH minus MASL', 'n_MASL_donors': n_a, 'n_MASH_donors': n_b,
        'MASL_mean_pct': float(a.mean()), 'MASH_mean_pct': float(b.mean()),
        'MASL_median_pct': float(np.median(a)), 'MASH_median_pct': float(np.median(b)),
        'mean_difference_pct_points': observed, 'mean_difference_95CI_low': float(low),
        'mean_difference_95CI_high': float(high), 'CI_method': bootstrap_method,
        'n_bootstrap_resamples': len(bootstrap), 'bootstrap_seed': seed,
        'p_value': p, 'alternative': 'two-sided',
        'test': 'exact independent-donor label permutation of the mean percentage difference',
        'n_permutations': len(null), 'primary_test_count': 1,
        'multiplicity_correction': 'none: one prespecified primary comparison',
        'MASH_increase_P_lt_0_05': bool(observed > 0 and p < .05),
        'note': 'Exploratory association; four donors per condition; bootstrap CI may be imprecise.',
        'pairing_assumption': 'distinct donor IDs treated as independent; matching numbers do not establish pairing',
    }
    leave_one_out = []
    for donor in table.donor:
        reduced = table.loc[table.donor.ne(donor)]
        means = reduced.groupby('condition')[outcome].mean()
        leave_one_out.append({'excluded_donor': donor,
                              'MASH_minus_MASL_mean_pct_points': means['MASH'] - means['MASL']})
    return result, null, pd.DataFrame(leave_one_out)


def plot_condition_comparison(table, result, cluster):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 5))
    colors = {'MASL': '#367da2', 'MASH': '#bd4337'}
    for pos, condition in enumerate(['MASL', 'MASH']):
        group = table.loc[table.condition.eq(condition)].sort_values('donor')
        ys = group[result['outcome']].to_numpy()
        axes[0].boxplot([ys], positions=[pos], widths=.38, showfliers=False,
                        patch_artist=True,
                        boxprops={'facecolor': colors[condition], 'alpha': .2},
                        medianprops={'color': colors[condition]})
        xs = pos + np.linspace(-.13, .13, len(group))
        axes[0].scatter(xs, ys, color=colors[condition], s=60, zorder=3)
        for i, (x, row) in enumerate(zip(xs, group.itertuples())):
            axes[0].annotate(row.donor, (x, getattr(row, result['outcome'])),
                             xytext=(4, 7 if i % 2 == 0 else -14),
                             textcoords='offset points', fontsize=8)
    axes[0].set_xticks([0, 1], [f"MASL (n={result['n_MASL_donors']} donors)",
                               f"MASH (n={result['n_MASH_donors']} donors)"])
    axes[0].set_ylabel('SLC7A5-high / all monocytes (%)')
    axes[0].set_ylim(0, max(1, table[result['outcome']].max() * 1.3))
    axes[0].set_title(f"Reference-matched cluster {cluster}\nExact donor permutation P={result['p_value']:.4g}", fontsize=11)
    difference = result['mean_difference_pct_points']
    lo, hi = result['mean_difference_95CI_low'], result['mean_difference_95CI_high']
    axes[1].hlines(0, lo, hi, color='#444444', linewidth=2)
    axes[1].scatter([difference], [0], color='#bd4337', s=65, zorder=3)
    axes[1].axvline(0, color='#777777', linestyle='--')
    axes[1].set_yticks([])
    axes[1].set_ylim(-1, 1)
    axes[1].set_xlabel('MASH − MASL mean difference\n(percentage points)')
    axes[1].set_title(f'Mean difference: {difference:.2f}\nDonor bootstrap 95% CI [{lo:.2f}, {hi:.2f}]', fontsize=11)
    for ax in axes:
        ax.tick_params(labelsize=10)
        ax.xaxis.label.set_size(10)
        ax.yaxis.label.set_size(10)
        ax.spines[['top', 'right']].set_visible(False)
    fig.text(.5, .015, 'One point per donor; exploratory reference annotation; no pooled-cell hypothesis test.',
             ha='center', fontsize=9)
    fig.tight_layout(rect=(0, .05, 1, 1))
    return fig


def plot_donor_counts_and_frequencies(table, cluster):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    x = np.arange(len(table))
    colors = ['#367da2' if c == 'MASL' else '#bd4337' for c in table.condition]
    axes[0].bar(x, table.high_n, color=colors)
    axes[0].set_ylabel('Captured SLC7A5-high cells (n)')
    axes[0].set_title(f'Reference-matched cluster {cluster}: captured counts', fontsize=11)
    axes[1].scatter(x, table.high_pct_of_monocyte, color=colors, s=60)
    axes[1].set_ylabel('SLC7A5-high / all monocytes (%)')
    axes[1].set_title('One observation per donor', fontsize=11)
    for i, row in enumerate(table.itertuples()):
        axes[0].annotate(str(int(row.high_n)), (i, row.high_n),
                         xytext=(0, 5), textcoords='offset points', ha='center', fontsize=8)
        axes[1].annotate(f'{int(row.high_n)}/{int(row.monocyte_n)}', (i, row.high_pct_of_monocyte),
                         xytext=(0, 6), textcoords='offset points', ha='center', fontsize=8)
    for ax in axes:
        ax.tick_params(labelsize=9)
        ax.xaxis.label.set_size(10)
        ax.yaxis.label.set_size(10)
        ax.set_xticks(x, table.donor, rotation=45, ha='right', fontsize=9)
        ax.set_ylim(0, max(1, ax.get_ylim()[1]) * 1.18)
        ax.spines[['top', 'right']].set_visible(False)
    fig.text(.5, .01, 'MASL: blue; MASH: red. Captured counts are not absolute blood cell counts.',
             ha='center', fontsize=9)
    fig.tight_layout(rect=(0, .05, 1, 1))
    return fig
