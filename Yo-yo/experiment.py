"""
CSI4109 - Assignment 3: Experimental Analysis of Yo-Yo Algorithm
=================================================================
This script runs the two experiment sets required by the assignment:

  Experiment 1: Fix n, vary m (Impact of Graph Density)
    - n ∈ {20, 30, 40, 60, 80, 100}
    - m ∈ {n, n·log(n), n·√n, n²}
    - 1000 trials per (n, m) pair

  Experiment 2: Fix m/n ratio, vary n (Impact of Graph Size)
    - m = 2n and m = 3n (two linear densities)
    - n ∈ {20, 30, 40, 60, 80, 100}
    - 1000 trials per (n, m) pair

Outputs:
  - experiment1_results.csv  — raw averages for Experiment 1
  - experiment2_results.csv  — raw averages for Experiment 2
  - experiment1_density.png  — plot: message complexity vs. m (one line per n)
  - experiment2_size.png     — plot: message complexity vs. n (one line per density)
  - Console progress updates

Usage:
  python experiment.py
"""

import math
import time
import csv
import sys
from collections import defaultdict

# ── Inline matplotlib config (works even without display) ──
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ── Import from yoyo.py (must be in the same directory) ──
from yoyo import YoYoAlgorithm, generate_random_connected_graph


# ═════════════════════════════════════════════════════════════
# Configuration
# ═════════════════════════════════════════════════════════════
TRIALS = 1000                              # Number of runs per (n, m) pair
N_VALUES = [20, 30, 40, 60, 80, 100]      # Node counts to test
LINEAR_DENSITIES = [2, 3]                  # For Experiment 2: m = k·n


def compute_m_values(n):
    """
    Compute the four edge-count targets for a given n.
    Returns a list of (label, m_value) pairs.

    Per the assignment:
      m = n            (very sparse, tree-like)
      m = n · log(n)   (moderate)
      m = n · √n       (dense)
      m = n²           (very dense, near-complete)

    All values are clamped to [n-1, n(n-1)/2].
    """
    max_m = n * (n - 1) // 2
    raw = [
        ("n",          n),
        ("n*log(n)",   int(n * math.log2(n))),
        ("n*sqrt(n)",  int(n * math.sqrt(n))),
        ("n^2",        n * n),
    ]
    results = []
    for label, m in raw:
        m_clamped = max(n - 1, min(m, max_m))
        results.append((label, m_clamped))
    return results


def run_trials(n, m, num_trials=TRIALS):
    """
    Run the Yo-Yo algorithm `num_trials` times on random graphs
    with parameters (n, m).

    Returns:
        (avg_messages, min_messages, max_messages, std_dev)
    """
    message_counts = []
    for _ in range(num_trials):
        nodes, edges = generate_random_connected_graph(n, m)
        algo = YoYoAlgorithm(nodes, edges)
        leader, msgs = algo.run()
        message_counts.append(msgs)

    avg = sum(message_counts) / len(message_counts)
    min_m = min(message_counts)
    max_m = max(message_counts)
    variance = sum((x - avg) ** 2 for x in message_counts) / len(message_counts)
    std = variance ** 0.5
    return avg, min_m, max_m, std


def progress_bar(current, total, width=40, prefix=""):
    """Simple console progress bar."""
    frac = current / total
    filled = int(width * frac)
    bar = "#" * filled + "-" * (width - filled)
    sys.stdout.write(f"\r  {prefix} [{bar}] {current}/{total} ({frac:.0%})")
    sys.stdout.flush()


# ═════════════════════════════════════════════════════════════
# Experiment 1: Fix n, vary m (Impact of Graph Density)
# ═════════════════════════════════════════════════════════════
def run_experiment1():
    print("=" * 65)
    print("EXPERIMENT 1: Fix n, vary m (Impact of Graph Density)")
    print("=" * 65)

    # results[n] = list of (m_label, actual_m, avg, min, max, std)
    results = defaultdict(list)
    total_configs = len(N_VALUES) * 4
    done = 0

    for n in N_VALUES:
        m_configs = compute_m_values(n)
        print(f"\n  n = {n}:")

        for label, m in m_configs:
            t0 = time.time()
            avg, mn, mx, std = run_trials(n, m)
            elapsed = time.time() - t0
            results[n].append((label, m, avg, mn, mx, std))
            done += 1
            print(f"    m = {m:>5d} ({label:>8s}) | "
                  f"avg = {avg:8.1f} | min = {mn:5d} | max = {mx:5d} | "
                  f"std = {std:6.1f} | {elapsed:.1f}s")

    # ── Save CSV ──
    with open("experiment1_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["n", "m_label", "m_actual", "avg_messages",
                         "min_messages", "max_messages", "std_dev"])
        for n in N_VALUES:
            for label, m, avg, mn, mx, std in results[n]:
                writer.writerow([n, label, m, f"{avg:.2f}", mn, mx, f"{std:.2f}"])
    print("\n  -> Saved: experiment1_results.csv")

    # ── Plot: line plot, one line per n, x = m with density labels ──
    fig, ax = plt.subplots(figsize=(11, 7))
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#e377c2"]
    markers = ["o", "s", "^", "D", "v", "P"]

    for i, n in enumerate(N_VALUES):
        m_vals = [r[1] for r in results[n]]
        avg_vals = [r[2] for r in results[n]]
        ax.plot(m_vals, avg_vals, marker=markers[i], linewidth=2, markersize=7,
                color=colors[i], label=f"n = {n}", zorder=3)

        # Annotate each point with its value
        for m, avg in zip(m_vals, avg_vals):
            ax.annotate(f"{avg:.0f}", (m, avg), textcoords="offset points",
                        xytext=(5, 8), fontsize=7, color=colors[i])

    # Add vertical reference lines at density levels for n=100
    density_display = {"n": "m=n", "n*log(n)": "m=n log n",
                       "n*sqrt(n)": "m=n sqrt(n)", "n^2": "m=n^2"}
    for label, m, avg, mn, mx, std in results[100]:
        display = density_display.get(label, label)
        ax.axvline(x=m, color="gray", linestyle="--", alpha=0.3, zorder=1)
        ax.text(m, ax.get_ylim()[1] if ax.get_ylim()[1] > 0 else 10000,
                display, rotation=0, va="bottom", ha="center",
                fontsize=9, color="gray", style="italic")

    ax.set_xlabel("Number of Edges (m)", fontsize=13)
    ax.set_ylabel("Average Message Complexity", fontsize=13)
    ax.set_title("Experiment 1: Impact of Graph Density on Message Complexity",
                 fontsize=15, fontweight="bold")
    ax.legend(title="Nodes", fontsize=10, loc="upper left")
    ax.grid(True, alpha=0.3)
    ax.set_xscale("log")
    ax.set_yscale("log")
    plt.tight_layout()
    fig.savefig("experiment1_density.png", dpi=150)
    plt.close()
    print("  -> Saved: experiment1_density.png")

    return results


# ═════════════════════════════════════════════════════════════
# Experiment 2: Fix m/n ratio, vary n (Impact of Graph Size)
# ═════════════════════════════════════════════════════════════
def run_experiment2():
    print("\n" + "=" * 65)
    print("EXPERIMENT 2: Fix m = k·n, vary n (Impact of Graph Size)")
    print("=" * 65)

    # results[k] = list of (n, actual_m, avg, min, max, std)
    results = defaultdict(list)

    for k in LINEAR_DENSITIES:
        print(f"\n  Density: m = {k}n")

        for n in N_VALUES:
            m = k * n
            max_m = n * (n - 1) // 2
            m = min(m, max_m)

            t0 = time.time()
            avg, mn, mx, std = run_trials(n, m)
            elapsed = time.time() - t0
            results[k].append((n, m, avg, mn, mx, std))
            print(f"    n = {n:>3d}, m = {m:>4d} | "
                  f"avg = {avg:8.1f} | min = {mn:5d} | max = {mx:5d} | "
                  f"std = {std:6.1f} | {elapsed:.1f}s")

    # ── Save CSV ──
    with open("experiment2_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["density_k", "n", "m_actual", "avg_messages",
                         "min_messages", "max_messages", "std_dev"])
        for k in LINEAR_DENSITIES:
            for n, m, avg, mn, mx, std in results[k]:
                writer.writerow([k, n, m, f"{avg:.2f}", mn, mx, f"{std:.2f}"])
    print("\n  -> Saved: experiment2_results.csv")

    # ── Plot ──
    fig, ax = plt.subplots(figsize=(10, 6))
    markers = ["o", "s", "^", "D"]
    colors = ["#2196F3", "#FF5722", "#4CAF50", "#9C27B0"]

    for i, k in enumerate(LINEAR_DENSITIES):
        n_vals = [r[0] for r in results[k]]
        avg_vals = [r[2] for r in results[k]]
        ax.plot(n_vals, avg_vals, marker=markers[i], linewidth=2, markersize=7,
                color=colors[i], label=f"m = {k}n")

    ax.set_xlabel("Number of Nodes (n)", fontsize=12)
    ax.set_ylabel("Average Message Complexity", fontsize=12)
    ax.set_title("Experiment 2: Impact of Graph Size on Message Complexity",
                 fontsize=14, fontweight="bold")
    ax.legend(title="Density", fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(N_VALUES)
    plt.tight_layout()
    fig.savefig("experiment2_size.png", dpi=150)
    plt.close()
    print("  -> Saved: experiment2_size.png")

    return results


# ═════════════════════════════════════════════════════════════
# Summary Table
# ═════════════════════════════════════════════════════════════
def print_summary(exp1_results, exp2_results):
    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)

    print("\n  Experiment 1 — Density Impact (avg messages):")
    header = f"  {'n':>5s} | {'m=n':>8s} | {'m=nlogn':>10s} | {'m=nsqrtn':>10s} | {'m=n^2':>8s}"
    print(header)
    print("  " + "-" * len(header))
    for n in N_VALUES:
        row = f"  {n:5d}"
        for _, m, avg, *_ in exp1_results[n]:
            row += f" | {avg:8.1f}"
        print(row)

    print(f"\n  Experiment 2 — Size Impact (avg messages):")
    for k in LINEAR_DENSITIES:
        print(f"\n    m = {k}n:")
        for n, m, avg, mn, mx, std in exp2_results[k]:
            print(f"      n = {n:3d}: avg = {avg:.1f}, std = {std:.1f}")

    print("\n  Output files:")
    print("    experiment1_results.csv   — raw data for Experiment 1")
    print("    experiment2_results.csv   — raw data for Experiment 2")
    print("    experiment1_density.png   — density impact plot")
    print("    experiment2_size.png      — size impact plot")


# ═════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print()
    print("  CSI4109 — Yo-Yo Algorithm: Experimental Analysis")
    print(f"  Trials per configuration: {TRIALS}")
    print(f"  Node values tested: {N_VALUES}")
    print()

    t_start = time.time()

    exp1 = run_experiment1()
    exp2 = run_experiment2()
    print_summary(exp1, exp2)

    elapsed_total = time.time() - t_start
    print(f"\n  Total runtime: {elapsed_total:.1f}s")
    print()