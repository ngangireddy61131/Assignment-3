"""
Randomized and deterministic Quicksort (Assignment 3, Part 1).

Both versions share the same partition routine (Hoare's scheme), so the ONLY
difference between them is how the pivot is chosen:
  * randomized_quicksort    -> pivot chosen uniformly at random from a[lo..hi]
  * deterministic_quicksort -> pivot is always the first element a[lo]

Design notes
  * Hoare partitioning stops on keys equal to the pivot, so arrays with many
    repeated elements are split evenly instead of degrading to O(n^2).
  * After partitioning we recurse on the SMALLER side and loop on the larger
    side. This keeps the recursion depth O(log n) even in the worst case, so
    deterministic quicksort on a large sorted array does not crash with
    RecursionError. It is still slow (O(n^2)), which is what we want to measure.
"""

import random

__all__ = ["randomized_quicksort", "deterministic_quicksort"]


def _hoare_partition(a, lo, hi):
    """Partition a[lo..hi] around the pivot a[lo] (CLRS Hoare-Partition).

    Returns j with lo <= j < hi such that every element of a[lo..j] is <= pivot
    and every element of a[j+1..hi] is >= pivot.
    """
    pivot = a[lo]
    i = lo - 1
    j = hi + 1
    while True:
        j -= 1
        while a[j] > pivot:
            j -= 1
        i += 1
        while a[i] < pivot:
            i += 1
        if i < j:
            a[i], a[j] = a[j], a[i]
        else:
            return j


def _quicksort(a, lo, hi, choose_pivot):
    """Sort a[lo..hi] in place using the given pivot-selection function."""
    while lo < hi:
        p = choose_pivot(lo, hi)
        a[lo], a[p] = a[p], a[lo]          # move the chosen pivot to the front
        j = _hoare_partition(a, lo, hi)
        if j - lo < hi - j:                 # left part a[lo..j] is smaller
            _quicksort(a, lo, j, choose_pivot)
            lo = j + 1
        else:                               # right part a[j+1..hi] is smaller
            _quicksort(a, j + 1, hi, choose_pivot)
            hi = j


def randomized_quicksort(arr, inplace=False, rng=None):
    """Randomized Quicksort: pivot chosen uniformly at random.

    Args:
        arr: list (or any iterable) of mutually comparable items.
        inplace: if True, sort `arr` itself (must be a list); otherwise a new
                 sorted list is returned and `arr` is left unchanged.
        rng: optional random.Random instance (useful for reproducible runs).
    Returns:
        The sorted list.
    """
    a = arr if inplace else list(arr)
    rand = rng if rng is not None else random
    _quicksort(a, 0, len(a) - 1, lambda lo, hi: rand.randint(lo, hi))
    return a


def deterministic_quicksort(arr, inplace=False):
    """Deterministic Quicksort: the first element of each subarray is the pivot."""
    a = arr if inplace else list(arr)
    _quicksort(a, 0, len(a) - 1, lambda lo, hi: lo)
    return a


if __name__ == "__main__":
    sample = [9, 3, 7, 3, 1, 8, 2, 9, 0]
    print("Input:        ", sample)
    print("Randomized:   ", randomized_quicksort(sample))
    print("Deterministic:", deterministic_quicksort(sample))