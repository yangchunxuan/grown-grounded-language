"""Generate all figures for ggl.tex from banked verdict JSONs."""
import json, os, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype'] = 42  # embed TrueType (Type 42), avoid Type 3 — publisher-safe
matplotlib.rcParams['ps.fonttype'] = 42
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OFFSCREEN = os.path.join(ROOT, 'offscreen')
FIGS = os.path.join(ROOT, 'paper', 'figs')
os.makedirs(FIGS, exist_ok=True)

def savefig(name):
    path = os.path.join(FIGS, name)
    plt.savefig(path, format='pdf', bbox_inches='tight')
    plt.close()
    print(f'Saved {path}')

# ─────────────────────────────────────────────────────────────────────────────
# f_headline.pdf  — per-seed MII scatter + paired margin
# ─────────────────────────────────────────────────────────────────────────────
def fig_headline():
    d = json.load(open(os.path.join(OFFSCREEN, 'rtc_g1f_commblind_verdict_formal48_rngfix.json')))
    surv = np.array(d['survival_final_mii'])
    comm = np.array(d['commblind_final_mii'])
    margin = d['survival_mean'] - d['commblind_mean']  # 0.0548
    ci_lo, ci_hi = d['survival_minus_commblind_ci']

    fig, axes = plt.subplots(1, 2, figsize=(8, 3.8))

    # left: per-seed scatter
    ax = axes[0]
    ax.scatter(comm, surv, alpha=0.55, s=18, color='steelblue', zorder=3)
    lo = min(surv.min(), comm.min()) - 0.01
    hi = max(surv.max(), comm.max()) + 0.01
    ax.plot([lo, hi], [lo, hi], 'k--', lw=0.8, label='y = x')
    ax.set_xlabel('Random-fitness control MII')
    ax.set_ylabel('Survival arm MII')
    ax.set_title('Per-seed MII (n=48)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # right: paired margin with CI
    ax2 = axes[1]
    ax2.barh([0], [margin], xerr=[[margin - ci_lo], [ci_hi - margin]],
             height=0.45, color='steelblue', ecolor='black', capsize=5,
             error_kw={'linewidth': 1.5})
    ax2.axvline(0, color='red', lw=1.2, linestyle='--', label='0')
    ax2.set_yticks([0])
    ax2.set_yticklabels(['Survival−Random'])
    ax2.set_xlabel('Paired MII win-margin')
    ax2.set_title('Margin +{:.4f}\n95% CI [{:.4f}, {:.4f}]'.format(margin, ci_lo, ci_hi))
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3, axis='x')

    fig.suptitle('Co-evolution headline: survival vs random-fitness control (gen 28, n=48)',
                 fontsize=9)
    plt.tight_layout()
    savefig('f_headline.pdf')


# ─────────────────────────────────────────────────────────────────────────────
# f_transient.pdf  — margin trajectory + two arms
# ─────────────────────────────────────────────────────────────────────────────
def fig_transient():
    d = json.load(open(os.path.join(OFFSCREEN, 'rtc_g1f_transient_probe_verdict.json')))
    gens = [int(c) for c in d['checkpoints']]
    surv_mii   = [d['trajectory'][str(g)]['survival_mii'] for g in gens]
    rand_mii   = [d['trajectory'][str(g)]['random_mii']   for g in gens]
    margins    = [d['trajectory'][str(g)]['margin']        for g in gens]
    ci_lo      = [d['trajectory'][str(g)]['margin_ci'][0]  for g in gens]
    ci_hi      = [d['trajectory'][str(g)]['margin_ci'][1]  for g in gens]

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))

    # left: two arms
    ax = axes[0]
    ax.plot(gens, surv_mii, 'o-', color='steelblue', label='Survival arm')
    ax.plot(gens, rand_mii, 's--', color='darkorange', label='Random-fitness control')
    ax.axhline(0.0016, color='gray', lw=0.8, linestyle=':', label='Chance floor (1/625)')
    ax.set_xlabel('Generation')
    ax.set_ylabel('Mean MII')
    ax.set_title('MII trajectories (n=24)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # right: margin + CI
    ax2 = axes[1]
    marg_arr = np.array(margins)
    lo_arr   = np.array(ci_lo)
    hi_arr   = np.array(ci_hi)
    ax2.errorbar(gens, marg_arr,
                 yerr=[marg_arr - lo_arr, hi_arr - marg_arr],
                 fmt='o-', color='steelblue', ecolor='black', capsize=5,
                 elinewidth=1.5)
    ax2.axhline(0, color='red', lw=1.2, linestyle='--', label='0')
    ax2.set_xlabel('Generation')
    ax2.set_ylabel('Paired margin (survival − random)')
    ax2.set_title('Margin trajectory (n=24, 95% CI)')
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)

    fig.suptitle('Transient probe: selection sharpens a clonal-descent channel (post-hoc)',
                 fontsize=9)
    plt.tight_layout()
    savefig('f_transient.pdf')


# ─────────────────────────────────────────────────────────────────────────────
# f_wf_cf.pdf  — WF vs CF with chance floor
# ─────────────────────────────────────────────────────────────────────────────
def fig_wf_cf():
    # Use diagnostic data (the most complete source for WF/CF)
    d = json.load(open(os.path.join(OFFSCREEN, 'rtc_g1f_kinonly_diagnostic_verdict.json')))
    wf     = d['WF']
    wf_ci  = d['WF_CI']
    cf     = d['CF']
    cf_ci  = d['CF_CI']
    floor  = d['FLOOR']

    fig, ax = plt.subplots(figsize=(5, 3.8))
    bars_labels = ['WF (within-founder)', 'CF (cross-founder)']
    vals   = [wf, cf]
    ci_lo  = [wf - wf_ci[0], cf - cf_ci[0]]
    ci_hi  = [wf_ci[1] - wf, cf_ci[1] - cf]
    colors = ['steelblue', 'darkorange']
    xs = [0, 1]
    ax.bar(xs, vals, color=colors, width=0.5,
           yerr=[ci_lo, ci_hi], capsize=6, error_kw={'linewidth': 1.5})
    ax.axhline(floor, color='red', lw=1.5, linestyle='--', label=f'Chance floor 1/625 ≈{floor:.4f}')
    ax.set_xticks(xs)
    ax.set_xticklabels(bars_labels, fontsize=9)
    ax.set_ylabel('MII')
    ax.set_title('Within-founder vs cross-founder MII\n(kin-only diagnostic, n=16, 5/16 seeds with window)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis='y')

    # annotate (placed in clear areas, not over the error bars)
    ax.set_ylim(0, 0.215)
    ax.text(0.32, 0.135, f'WF = {wf:.4f}\n(~100× chance)', fontsize=8, color='steelblue',
            ha='left', va='center')
    ax.text(1.0, 0.028, f'CF = {cf:.5f}\n(≈ floor)', fontsize=8, color='darkorange',
            ha='center', va='bottom')

    plt.tight_layout()
    savefig('f_wf_cf.pdf')


# ─────────────────────────────────────────────────────────────────────────────
# f_neff.pdf  — N_eff: soft96 sustained vs hard96 collapse
# ─────────────────────────────────────────────────────────────────────────────
def fig_neff():
    d = json.load(open(os.path.join(OFFSCREEN, 'rtc_g1f_c1_collapse_probe_verdict.json')))
    cs = d['cells_summary']
    cells  = ['hard16', 'hard96', 'soft16', 'soft96']
    labels = ['hard×16', 'hard×96', 'soft×16', 'soft×96']
    neff   = [cs[c]['mean_final_neff'] for c in cells]
    colors = ['steelblue', 'cornflowerblue', 'darkorange', 'tomato']

    fig, ax = plt.subplots(figsize=(5.8, 4.0))
    bars = ax.bar(range(4), neff, color=colors, width=0.55)
    ax.set_ylim(0, 5.0)
    ax.axhline(1, color='gray', lw=1.0, linestyle='--', label='$N_{\\mathrm{eff}}$ = 1 (monoclonal)')
    # highlight soft96 / hard96 (text in clear interior space, arrows to the bars)
    ax.annotate('soft96 sustained\n$N_{\\mathrm{eff}}$ ≈ 4.10', xy=(3, neff[3]), xytext=(2.0, 3.7),
                fontsize=8, color='tomato', ha='center', va='center',
                arrowprops=dict(arrowstyle='->', color='tomato', lw=1.0))
    ax.annotate('hard96 still\ncollapsing\n$N_{\\mathrm{eff}}$ ≈ 1.44', xy=(1, neff[1]), xytext=(1.05, 2.75),
                fontsize=8, color='cornflowerblue', ha='center', va='center',
                arrowprops=dict(arrowstyle='->', color='cornflowerblue', lw=1.0))
    ax.set_xticks(range(4))
    ax.set_xticklabels(labels)
    ax.set_ylabel('Final inverse-Simpson $N_{\\mathrm{eff}}$')
    ax.set_title('Lineage diversity: population and selection interact\n(C1 collapse probe 2×2 factorial)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis='y')
    for bar, v in zip(bars, neff):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f'{v:.2f}', ha='center', va='bottom', fontsize=8)
    plt.tight_layout()
    savefig('f_neff.pdf')


# ─────────────────────────────────────────────────────────────────────────────
# f_crosslineage.pdf  — CF at floor across three probes
# ─────────────────────────────────────────────────────────────────────────────
def fig_crosslineage():
    # C2X
    dc2x  = json.load(open(os.path.join(OFFSCREEN, 'rtc_g1f_c2x_crosslineage_verdict.json')))
    # C2X2 — use the STAT025 (viable 0.25 non-kin) arm
    dc2x2 = json.load(open(os.path.join(OFFSCREEN, 'rtc_g1f_c2x2_ramped_verdict.json')))
    # C2X3
    dc2x3 = json.load(open(os.path.join(OFFSCREEN, 'rtc_g1f_c2x3_forced_verdict.json')))

    floor   = 0.00159
    alive_vals = [dc2x['arm_mean_alive']['C2X_OPEN'],
                  dc2x2['STAT025_detail']['mean_alive'],
                  dc2x3['FORCED_detail']['mean_alive']]
    labels  = [f'C2X\n(100% non-kin)\nalive={alive_vals[0]:.2f}',
               f'C2X2 STAT025\n(0.25 non-kin, viable)\nalive={alive_vals[1]:.2f}',
               f'C2X3\n(0.5 forced-quota)\nalive={alive_vals[2]:.2f}']
    cf_vals = [
        dc2x['CF_OPEN'],
        dc2x2['STAT025_detail']['CF'],
        dc2x3['FORCED_detail']['CF'],
    ]
    ci_lo = [
        dc2x['CF_margin_CI'][0] + dc2x['FLOOR'],   # approximate CI around CF
        dc2x2['STAT025_detail']['CF_margin_CI'][0] + dc2x2['FLOOR'],
        dc2x3['FORCED_detail']['CF_margin_CI'][0] + dc2x3['FLOOR'],
    ]
    ci_hi = [
        dc2x['CF_margin_CI'][1] + dc2x['FLOOR'],
        dc2x2['STAT025_detail']['CF_margin_CI'][1] + dc2x2['FLOOR'],
        dc2x3['FORCED_detail']['CF_margin_CI'][1] + dc2x3['FLOOR'],
    ]

    fig, ax = plt.subplots(figsize=(6, 4))
    xs = [0, 1, 2]
    err_lo = [max(cf_vals[i] - ci_lo[i], 0) for i in range(3)]
    err_hi = [max(ci_hi[i] - cf_vals[i], 0) for i in range(3)]
    ax.errorbar(xs, cf_vals,
                yerr=[err_lo, err_hi],
                fmt='o', color='steelblue', ecolor='black', capsize=6,
                markersize=8, elinewidth=1.5)
    ax.axhline(floor, color='red', lw=1.5, linestyle='--',
               label=f'Chance floor 1/625 ≈ {floor:.5f}')
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_ylabel('Cross-founder MII (CF)')
    ax.set_title('Cross-lineage CF stays at chance floor\nacross three heterogeneous interventions (n=8 each)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    savefig('f_crosslineage.pdf')


# ─────────────────────────────────────────────────────────────────────────────
# f_schematic.pdf  — simple box diagram of agent + world + evolution loop
# ─────────────────────────────────────────────────────────────────────────────
def fig_schematic():
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5.6)
    ax.axis('off')

    def box(x, y, w, h, label, color='lightblue', fontsize=9):
        rect = mpatches.FancyBboxPatch((x, y), w, h,
                                       boxstyle='round,pad=0.1',
                                       facecolor=color, edgecolor='black', linewidth=1.2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, label, ha='center', va='center',
                fontsize=fontsize, multialignment='center')

    def arrow(x1, y1, x2, y2, label='', label_dy=0.2, va='bottom'):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', lw=1.3, color='dimgray'))
        if label:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + label_dy, label,
                    fontsize=8, color='dimgray', ha='center', va=va,
                    multialignment='center')

    # boxes with WIDE gaps so arrow labels fit in the empty space between them
    box(0.3, 1.6, 2.7, 2.4, '48×48 lethal-vent\nworld\n(4-channel field,\nfixed-rule physics)',
        color='#d4ecd4')
    box(4.7, 1.2, 3.0, 3.2,
        'Agent\nUnifiedIO code-table\nK×BANDS×VOCAB (4×5×6)\ninit N(0,1)\n\nEmit: argmax→symbol\nDecode: argmax→bin',
        color='#cce0f5')
    box(9.3, 1.6, 2.5, 2.4,
        'Reproduction\n(mutation + selection)\nSurvival arm: fit = survival\nControl arm: fit = random',
        color='#f5e6cc')

    # world ↔ agent (gap x≈3.0–4.7): top arrow label ABOVE, bottom arrow label BELOW
    arrow(3.0, 3.5, 4.7, 3.5, 'lagged noisy\nsensor', label_dy=0.22, va='bottom')
    arrow(4.7, 2.1, 3.0, 2.1, 'messages\n(decode+use)', label_dy=-0.22, va='top')
    # agent ↔ reproduction (gap x≈7.7–9.3)
    arrow(7.7, 3.5, 9.3, 3.5, 'energy\n(survival)', label_dy=0.22, va='bottom')
    arrow(9.3, 2.1, 7.7, 2.1, 'offspring\n(mutated\ncode-table)', label_dy=-0.22, va='top')

    ax.text(6.0, 0.55,
            'MII probe: sample referents → emit → decode → exact-tuple recovery (chance 1/625)',
            ha='center', fontsize=8, color='dimgray',
            bbox=dict(boxstyle='round', facecolor='#f0f0f0', alpha=0.8))

    ax.set_title('Substrate schematic: lethal-vent world, tied code-table agent, and evolution loop',
                 fontsize=10)
    plt.tight_layout()
    savefig('f_schematic.pdf')


if __name__ == '__main__':
    fig_headline()
    fig_transient()
    fig_wf_cf()
    fig_neff()
    fig_crosslineage()
    fig_schematic()
    print('All figures done.')
