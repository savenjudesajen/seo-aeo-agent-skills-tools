# -*- coding: utf-8 -*-
"""
Chart generators for the Quick AEO Audit (builder script; requires matplotlib).

    sov_bar     category share of voice, horizontal bar (the signature chart)
    theme_bar   keyword gap by non-brand theme, horizontal bar
    pareto_bar  competitor top-5-pages traffic share, vertical bar

Neutral palette from reference/deck-layout.md; swap the constants for the
client's brand colours if they have them. Pure ASCII on purpose.

The default titles are neutral placeholders. Pass title= to each function with
the finding stated as a sentence and the real figure (one message per slide).

Usage:
    python sov_chart.py      # writes demo PNGs with fictional brands
    from sov_chart import sov_bar, theme_bar, pareto_bar
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ACCENT = "#2563EB"     # client / opportunity
GRAY = "#B8BEC6"       # competitors
FAINT = "#DDE1E6"      # zero values, last bar
DARK = "#1F2933"
MUTED = "#5F6B7A"
GREEN = "#166534"
GRID = "#EEF0F3"
AXIS = "#DDE1E6"
TICK = "#8A95A3"


def _style_axes(ax, grid_axis):
    ax.set_facecolor("white")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.spines["left"].set_color(AXIS)
    ax.tick_params(colors=TICK, labelsize=10)
    ax.set_axisbelow(True)
    (ax.xaxis if grid_axis == "x" else ax.yaxis).grid(True, color=GRID, zorder=0)


def _save(fig, ax, title, out, size=16):
    ax.set_title(title, loc="left", fontsize=size, fontweight="bold", color=DARK, pad=12)
    plt.tight_layout()
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def sov_bar(brands_vals, client, out="chart_sov.png", n_prompts=50,
            title="Share of voice on non-branded category prompts",
            figsize=(13.0, 3.7)):
    """brands_vals: list of (brand, pct) sorted descending. client: the brand drawn in the accent colour."""
    labels = [b for b, _ in brands_vals]
    vals = [v for _, v in brands_vals]
    colors = [ACCENT if b == client else (FAINT if v == 0 else GRAY) for b, v in brands_vals]
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    fig.patch.set_facecolor("white")
    ax.barh(range(len(labels)), vals, color=colors, height=0.62, zorder=3)
    ax.invert_yaxis()
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=15, color=DARK)
    ax.set_xlim(0, max(vals) * 1.15 + 5)
    for i, (b, v) in enumerate(brands_vals):
        ax.text(v + 1.2, i, "%s%%" % v, va="center", ha="left", fontsize=15, fontweight="bold",
                color=(ACCENT if b == client else MUTED))
    ax.set_xlabel("Share of voice across %d non-branded category prompts (single-run baseline)" % n_prompts,
                  fontsize=11, color=MUTED)
    _style_axes(ax, "x")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    return _save(fig, ax, title, out)


def theme_bar(themes_vals, out="chart_gap.png",
              title="Untapped search volume by theme",
              xlabel="Monthly search volume where competitors rank and the client does not (brand terms excluded)",
              figsize=(13.0, 4.6)):
    """themes_vals: list of (theme, monthly volume). All bars in the accent colour (all are opportunities)."""
    tv = sorted(themes_vals, key=lambda x: x[1])
    labels = [t for t, _ in tv]
    vals = [v for _, v in tv]
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    fig.patch.set_facecolor("white")
    ax.barh(range(len(labels)), vals, color=ACCENT, height=0.66, zorder=3)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=14, color=DARK)
    ax.set_xlim(0, max(vals) * 1.12)
    for i, v in enumerate(vals):
        ax.text(v + max(vals) * 0.012, i, "{:,}".format(v), va="center", ha="left", fontsize=13,
                fontweight="bold", color=GREEN)
    ax.set_xlabel(xlabel, fontsize=10.5, color=MUTED)
    _style_axes(ax, "x")
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    return _save(fig, ax, title, out)


def pareto_bar(pages_vals, out="chart_pareto.png",
               title="Organic traffic share of the top 5 pages",
               figsize=(13.0, 4.6)):
    """pages_vals: list of (page label, traffic pct); the last item is usually 'All other pages'.

    Rewrite the title to state the finding with the real figure once you know it.
    """
    labels = [p for p, _ in pages_vals]
    vals = [v for _, v in pages_vals]
    colors = [GRAY] * (len(vals) - 1) + [FAINT]
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    fig.patch.set_facecolor("white")
    ax.bar(range(len(labels)), vals, color=colors, width=0.62, zorder=3)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=11, color=DARK, rotation=12, ha="right")
    ax.set_ylim(0, max(vals) * 1.15)
    for i, v in enumerate(vals):
        ax.text(i, v + max(vals) * 0.02, "%s%%" % v, ha="center", fontsize=13, fontweight="bold", color=MUTED)
    ax.set_ylabel("Share of organic traffic", fontsize=11, color=MUTED)
    _style_axes(ax, "y")
    return _save(fig, ax, title, out, size=15.5)


if __name__ == "__main__":
    # Fictional demo values only.
    sov_bar([("BrandE", 35), ("BrandB", 25), ("BrandD", 15), ("BrandA", 12), ("ClientX", 8), ("BrandF", 5)],
            "ClientX")
    theme_bar([("Theme one", 12000), ("Theme two", 8000), ("Theme three", 5000), ("Theme four", 2000)])
    pareto_bar([("Page 1", 25), ("Page 2", 15), ("Page 3", 10), ("Page 4", 5), ("Page 5", 5),
                ("All other pages", 40)])
    print("demo charts written")
