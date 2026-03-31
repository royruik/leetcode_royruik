"""
Experimental analysis of the Yo-Yo algorithm's message complexity.
Runs two sets of experiments and produces plots + CSV data.

Experiment 1: fix n, vary m across four density levels
Experiment 2: fix m = k*n (linear density), vary n
"""

import math
import time
import csv
import sys
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from yoyo import YoYoAlgorithm, generate_random_connected_graph

# how many times to repeat each (n, m) config
TRIALS = 1000
# node counts we test
N_VALUES = [20, 30, 40, 60, 80, 100]
# for experiment 2
LINEAR_DENSITIES = [2, 3]


def get_density_levels(n):
    """Return the four (label, m) pairs for a given n, clamped to valid range."""
    max_m = n * (n - 1) // 2
    levels = [
        ("n",         n),
        ("n*log(n)",  int(n * math.log2(n))),
        ("n*sqrt(n)", int(n * math.sqrt(n))),
        ("n^2",       n * n),
    ]
    return [(lbl, max(n - 1, min(m, max_m))) for lbl, m in levels]


def run_trials(n, m, trials=TRIALS):
    """Run the algorithm `trials` times, return (avg, min, max, std)."""
    counts = []
    for _ in range(trials):
        nodes, edges = generate_random_connected_graph(n, m)
        algo = YoYoAlgorithm(nodes, edges)
        _, msgs = algo.run()
        counts.append(msgs)

    avg = sum(counts) / len(counts)
    lo, hi = min(counts), max(counts)
    std = (sum((x - avg) ** 2 for x in counts) / len(counts)) ** 0.5
    return avg, lo, hi, std


# ---- Experiment 1: fix n, vary density ----

def experiment1():
    print("=" * 60)
    print("EXPERIMENT 1: fix n, vary m")
    print("=" * 60)

    data = defaultdict(list)  # n -> [(label, m, avg, min, max, std)]

    for n in N_VALUES:
        levels = get_density_levels(n)
        print(f"\n  n = {n}:")
        for label, m in levels:
            t0 = time.time()
            avg, lo, hi, std = run_trials(n, m)
            dt = time.time() - t0
            data[n].append((label, m, avg, lo, hi, std))
            print(f"    m={m:>5} ({label:>9}) | avg={avg:8.1f}  "
                  f"min={lo:5}  max={hi:5}  std={std:6.1f}  ({dt:.1f}s)")

    # save csv
    with open("experiment1_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["n", "m_label", "m_actual", "avg_messages",
                     "min_messages", "max_messages", "std_dev"])
        for n in N_VALUES:
            for label, m, avg, lo, hi, std in data[n]:
                w.writerow([n, label, m, f"{avg:.2f}", lo, hi, f"{std:.2f}"])
    print("\n  Saved experiment1_results.csv")

    # plot: one line per n, x = m (log-log)
    fig, ax = plt.subplots(figsize=(11, 7))
    palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#e377c2"]
    shapes = ["o", "s", "^", "D", "v", "P"]

    for i, n in enumerate(N_VALUES):
        ms = [r[1] for r in data[n]]
        avgs = [r[2] for r in data[n]]
        ax.plot(ms, avgs, marker=shapes[i], linewidth=2, markersize=7,
                color=palette[i], label=f"n={n}", zorder=3)
        for m, a in zip(ms, avgs):
            ax.annotate(f"{a:.0f}", (m, a), textcoords="offset points",
                        xytext=(5, 8), fontsize=7, color=palette[i])

    # vertical lines showing density levels (using n=100 as reference)
    nice_names = {"n": "m=n", "n*log(n)": "m=n log n",
                  "n*sqrt(n)": "m=n sqrt(n)", "n^2": "m=n^2"}
    for label, m, *_ in data[100]:
        ax.axvline(x=m, color="gray", ls="--", alpha=0.3, zorder=1)
        ax.text(m, ax.get_ylim()[1] or 10000, nice_names.get(label, label),
                va="bottom", ha="center", fontsize=9, color="gray", style="italic")

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
    print("  Saved experiment1_density.png")

    return data


# ---- Experiment 2: fix density ratio, vary n ----

def experiment2():
    print("\n" + "=" * 60)
    print("EXPERIMENT 2: fix m = k*n, vary n")
    print("=" * 60)

    data = defaultdict(list)  # k -> [(n, m, avg, min, max, std)]

    for k in LINEAR_DENSITIES:
        print(f"\n  m = {k}n:")
        for n in N_VALUES:
            m = min(k * n, n * (n - 1) // 2)
            t0 = time.time()
            avg, lo, hi, std = run_trials(n, m)
            dt = time.time() - t0
            data[k].append((n, m, avg, lo, hi, std))
            print(f"    n={n:>3}, m={m:>4} | avg={avg:8.1f}  "
                  f"min={lo:5}  max={hi:5}  std={std:6.1f}  ({dt:.1f}s)")

    # save csv
    with open("experiment2_results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["density_k", "n", "m_actual", "avg_messages",
                     "min_messages", "max_messages", "std_dev"])
        for k in LINEAR_DENSITIES:
            for n, m, avg, lo, hi, std in data[k]:
                w.writerow([k, n, m, f"{avg:.2f}", lo, hi, f"{std:.2f}"])
    print("\n  Saved experiment2_results.csv")

    # plot
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#2196F3", "#FF5722"]
    marks = ["o", "s"]

    for i, k in enumerate(LINEAR_DENSITIES):
        ns = [r[0] for r in data[k]]
        avgs = [r[2] for r in data[k]]
        ax.plot(ns, avgs, marker=marks[i], linewidth=2, markersize=7,
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
    print("  Saved experiment2_size.png")

    return data


# ---- print a summary at the end ----

def summary(d1, d2):
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print("\n  Experiment 1 (avg messages):")
    print(f"  {'n':>5} | {'m=n':>8} | {'m=nlogn':>10} | {'m=nsqrtn':>10} | {'m=n^2':>8}")
    print("  " + "-" * 55)
    for n in N_VALUES:
        vals = " | ".join(f"{r[2]:8.1f}" for r in d1[n])
        print(f"  {n:5} | {vals}")

    for k in LINEAR_DENSITIES:
        print(f"\n  Experiment 2 (m={k}n):")
        for n, m, avg, lo, hi, std in d2[k]:
            print(f"    n={n:3}: avg={avg:.1f}, std={std:.1f}")


if __name__ == "__main__":
    print(f"\nYo-Yo experimental analysis  |  {TRIALS} trials per config\n")

    t0 = time.time()
    d1 = experiment1()
    d2 = experiment2()
    summary(d1, d2)
    print(f"\nDone in {time.time() - t0:.1f}s\n")