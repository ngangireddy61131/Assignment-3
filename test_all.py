"""Correctness tests. Run:  python test_all.py   (also works with pytest)"""

import random

from quicksort import randomized_quicksort, deterministic_quicksort
from hash_table import HashTableChaining

SORTS = (randomized_quicksort, deterministic_quicksort)


def test_quicksort_edge_cases():
    cases = [
        [], [1], [2, 1], [1, 2, 3, 4, 5], [5, 4, 3, 2, 1],
        [3, 3, 3, 3], [5, 1, 5, 1, 5, 1], [0, -1, -5, 3, 2],
        [2.5, -1.0, 3.25, 0.0], list(range(1000)),
        list(range(1000, 0, -1)), [7] * 1000,
    ]
    for sort in SORTS:
        for case in cases:
            assert sort(case) == sorted(case), (sort.__name__, case[:10])


def test_quicksort_random_fuzz():
    rng = random.Random(0)
    for _ in range(300):
        n = rng.randint(0, 200)
        data = [rng.randint(-50, 50) for _ in range(n)]
        for sort in SORTS:
            assert sort(data) == sorted(data)


def test_quicksort_strings_and_inplace():
    words = ["pear", "apple", "fig", "apple", "kiwi"]
    for sort in SORTS:
        assert sort(words) == sorted(words)
    data = [3, 1, 2]
    result = randomized_quicksort(data)          # default: returns a copy
    assert data == [3, 1, 2] and result == [1, 2, 3]
    randomized_quicksort(data, inplace=True)     # in place
    assert data == [1, 2, 3]


def test_hash_basic_operations():
    t = HashTableChaining(seed=1)
    t.insert("a", 1)
    t.insert("b", 2)
    assert t.search("a") == 1 and t.search("b") == 2
    t.insert("a", 10)                            # update existing key
    assert t.search("a") == 10 and len(t) == 2
    assert t.delete("a") == 10
    assert "a" not in t and len(t) == 1
    assert t.get("missing", "default") == "default"
    for bad in (lambda: t.search("missing"), lambda: t.delete("missing")):
        try:
            bad()
            raise AssertionError("expected KeyError")
        except KeyError:
            pass


def test_hash_resizing_keeps_all_items():
    t = HashTableChaining(capacity=4, seed=2)
    for k in range(1000):
        t.insert(k, k * k)
    assert len(t) == 1000
    assert t.load_factor <= 0.75
    assert all(t.search(k) == k * k for k in range(1000))
    for k in range(990):
        t.delete(k)
    assert len(t) == 10
    assert t.num_slots >= 4 and t.load_factor >= 0.25 or t.num_slots == 4
    assert all(t.search(k) == k * k for k in range(990, 1000))


def test_hash_fixed_table_load_factor():
    t = HashTableChaining(capacity=10, auto_resize=False, seed=3)
    for k in range(50):
        t.insert(k, str(k))
    assert t.num_slots == 10 and abs(t.load_factor - 5.0) < 1e-9
    assert all(t.search(k) == str(k) for k in range(50))


if __name__ == "__main__":
    tests = [f for name, f in list(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print("PASS", test.__name__)
    print(f"\nAll {len(tests)} tests passed.")