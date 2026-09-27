"""
Empirical experiments for Assignment 3.

Run:   python benchmark.py          (full run, a few minutes)
       python benchmark.py --quick  (smaller sizes, under a minute)

Outputs (in the results/ folder):
  quicksort_results.csv, hashing_results.csv, results.md (tables for the report)
  quicksort_comparison.png, hashing_load_factor.png   (if matplotlib is installed)
"""

import argparse
import csv
import os
import platform
import random
import statistics
import time

from quicksort import randomized_quicksort, deterministic_quicksort
from hash_table import HashTableChaining

RESULTS_DIR = "results"
DISTRIBUTIONS = ("random", "sorted", "reverse", "repeated")


# ---------------- Part 1: Quicksort ----------------
def make_input(kind, n, rng):
    if kind == "random":
        return [rng.randint(0, 10 * n) for _ in range(n)]
    if kind == "sorted":
        return list(range(n))
    if kind == "reverse":
        return list(range(n, 0, -1))
    if kind == "repeated":
        return [rng.randint(0, 9) for _ in range(n)]  # only 10 distinct values
    raise ValueError(kind)


def time_sort(sort_fn, data, repeats):
    """Median running time (seconds) of sort_fn over `repeats` runs."""
    expected = sorted(data)
    times = []
    for _ in range(repeats):
        arr = list(data)
        start = time.perf_counter()
        sort_fn(arr, inplace=True)
        times.append(time.perf_counter() - start)
        assert arr == expected, f"{sort_fn.__name__} produced wrong output"
    return statistics.median(times)


def run_quicksort(sizes, repeats, seed):
    rng = random.Random(seed)
    random.seed(seed)  # makes the randomized pivots reproducible
    rows = []
    for kind in DISTRIBUTIONS:
        for n in sizes:
            data = make_input(kind, n, rng)
            t_rand = time_sort(randomized_quicksort, data, repeats)
            t_det = time_sort(deterministic_quicksort, data, repeats)
            rows.append({
                "distribution": kind,
                "n": n,
                "randomized_s": t_rand,
                "deterministic_s": t_det,
                "det_over_rand": t_det / t_rand if t_rand > 0 else float("nan"),
            })
            print(f"  {kind:>9}  n={n:>6}   randomized={t_rand:8.4f}s   "
                  f"deterministic={t_det:8.4f}s")
    return rows


# ---------------- Part 2: Hashing ----------------
def time_per_op_us(fn, keys):
    start = time.perf_counter()
    for k in keys:
        fn(k)
    return (time.perf_counter() - start) / len(keys) * 1e6


def run_hashing(fixed_slots, n_values, seed):
    rng = random.Random(seed)
    rows = []
    for auto_resize in (False, True):
        for n in n_values:
            keys = rng.sample(range(1, 10**9), n)
            missing = [-k for k in keys]  # negative keys are never inserted
            capacity = 8 if auto_resize else fixed_slots
            table = HashTableChaining(capacity=capacity,
                                      auto_resize=auto_resize, seed=seed)
            t_insert = time_per_op_us(lambda k: table.insert(k, k), keys)
            t_hit = time_per_op_us(table.search, keys)
            t_miss = time_per_op_us(table.get, missing)
            stats = table.chain_stats()
            load = table.load_factor
            slots = table.num_slots
            t_delete = time_per_op_us(table.delete, keys)
            rows.append({
                "resizing": "on" if auto_resize else "off",
                "n": n,
                "slots": slots,
                "load_factor": load,
                "max_chain": stats["max_chain"],
                "insert_us": t_insert,
                "search_hit_us": t_hit,
                "search_miss_us": t_miss,
                "delete_us": t_delete,
            })
            print(f"  resizing={'on ' if auto_resize else 'off'} n={n:>6} "
                  f"slots={slots:>6} alpha={load:5.2f} max_chain={stats['max_chain']:>3} "
                  f"hit={t_hit:6.3f}us miss={t_miss:6.3f}us")
    return rows


# ---------------- Output helpers ----------------
def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def to_markdown(rows, floatfmt):
    headers = list(rows[0].keys())
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "---|" * len(headers)]
    for r in rows:
        cells = [format(v, floatfmt) if isinstance(v, float) else str(v)
                 for v in r.values()]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def make_plots(qs_rows, hash_rows, fixed_slots):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - skipping plots (pip install matplotlib)")
        return

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    for ax, kind in zip(axes.flat, DISTRIBUTIONS):
        rows = [r for r in qs_rows if r["distribution"] == kind]
        ns = [r["n"] for r in rows]
        ax.plot(ns, [r["randomized_s"] for r in rows], "o-", label="Randomized")
        ax.plot(ns, [r["deterministic_s"] for r in rows], "s--",
                label="Deterministic (first pivot)")
        ax.set_title(f"{kind} input")
        ax.set_xlabel("n")
        ax.set_ylabel("time (s)")
        ax.grid(alpha=0.3)
        ax.legend()
    fig.suptitle("Randomized vs Deterministic Quicksort")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "quicksort_comparison.png"), dpi=150)
    plt.close(fig)

    fixed = [r for r in hash_rows if r["resizing"] == "off"]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot([r["load_factor"] for r in fixed], [r["search_hit_us"] for r in fixed],
            "o-", label="Successful search")
    ax.plot([r["load_factor"] for r in fixed], [r["search_miss_us"] for r in fixed],
            "s--", label="Unsuccessful search")
    ax.plot([r["load_factor"] for r in fixed], [r["insert_us"] for r in fixed],
            "^:", label="Insert")
    ax.set_xlabel("load factor  alpha = n / m")
    ax.set_ylabel("average time per operation (microseconds)")
    ax.set_title(f"Hashing with chaining, fixed table (m = {fixed_slots})")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "hashing_load_factor.png"), dpi=150)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Assignment 3 benchmarks")
    parser.add_argument("--quick", action="store_true",
                        help="use smaller input sizes for a fast run")
    parser.add_argument("--repeats", type=int, default=3,
                        help="runs per measurement (median is reported)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    sizes = [500, 1000, 2000] if args.quick else [1000, 2000, 4000, 8000]
    hash_n = ([256, 1024, 4096] if args.quick
              else [256, 512, 1024, 2048, 4096, 8192])
    fixed_slots = 1024
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"Python {platform.python_version()} on {platform.system()} "
          f"({platform.processor() or platform.machine()})")
    print("\n== Part 1: Randomized vs Deterministic Quicksort ==")
    qs_rows = run_quicksort(sizes, args.repeats, args.seed)
    print("\n== Part 2: Hash table with chaining ==")
    hash_rows = run_hashing(fixed_slots, hash_n, args.seed)

    write_csv(os.path.join(RESULTS_DIR, "quicksort_results.csv"), qs_rows)
    write_csv(os.path.join(RESULTS_DIR, "hashing_results.csv"), hash_rows)
    with open(os.path.join(RESULTS_DIR, "results.md"), "w") as f:
        f.write(f"Environment: Python {platform.python_version()}, "
                f"{platform.system()} {platform.machine()}\n\n")
        f.write("## Quicksort (median time in seconds)\n\n")
        f.write(to_markdown(qs_rows, ".4f") + "\n\n")
        f.write(f"## Hashing (fixed table uses m = {fixed_slots}; "
                "times in microseconds per operation)\n\n")
        f.write(to_markdown(hash_rows, ".3f") + "\n")
    make_plots(qs_rows, hash_rows, fixed_slots)
    print(f"\nDone. Results saved in the '{RESULTS_DIR}/' folder.")


if __name__ == "__main__":
    main()