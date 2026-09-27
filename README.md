# Assignment 3: Understanding Algorithm Efficiency and Scalability

Python implementations and experiments for:

1. **Randomized Quicksort** (compared with deterministic first-element-pivot Quicksort)
2. **Hash table with chaining** using a universal hash function and dynamic resizing

## Repository contents

| File | Purpose |
|---|---|
| `quicksort.py` | Randomized and deterministic Quicksort (shared Hoare partition) |
| `hash_table.py` | `HashTableChaining` class: insert, search, delete, resizing |
| `benchmark.py` | Runs all timing experiments and saves tables and plots to `results/` |
| `test_all.py` | Correctness tests, including edge cases |
| `REPORT.md` | Theoretical analysis, empirical results, and discussion |
| `results/` | CSV files, `results.md` tables, and PNG plots from the benchmark |

## How to run

Requires Python 3.8 or newer.

```bash
pip install -r requirements.txt     # optional; only needed for the plots
python test_all.py                  # run correctness tests
python benchmark.py                 # full experiments (a few minutes)
python benchmark.py --quick         # faster, smaller run
python quicksort.py                 # small demo
python hash_table.py                # small demo
```

## Using the code

```python
from quicksort import randomized_quicksort, deterministic_quicksort
from hash_table import HashTableChaining

randomized_quicksort([5, 2, 9, 2])        # -> [2, 2, 5, 9]

table = HashTableChaining()
table.insert("apple", 3)
table.search("apple")                      # -> 3
table.delete("apple")                      # -> 3
```

## Summary of findings

- **Randomized Quicksort** runs in expected O(n log n) time on every input type (random, sorted, reverse-sorted, and repeated values), because the pivot's randomness, not the input order, decides how balanced the splits are.
- **Deterministic Quicksort** with the first element as pivot matches randomized Quicksort on random data but degrades to O(n²) on sorted and reverse-sorted arrays. In the experiments, its running time grows roughly 4× each time n doubles on those inputs.
- **Repeated elements** are handled efficiently by both versions because Hoare partitioning splits equal keys evenly.
- **Hash table with chaining:** expected search, insert, and delete time is Θ(1 + α), where α = n/m is the load factor. With a fixed table, time per operation rises as α grows. With resizing (grow at α > 0.75, shrink at α < 0.25), α stays bounded and operations remain O(1) on average (amortized for insert).

See `REPORT.md` for the full analysis and `results/` for the measured data.