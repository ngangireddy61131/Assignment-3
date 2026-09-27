"""
Hash table with separate chaining (Assignment 3, Part 2).

Hash function: the universal family from CLRS (Carter & Wegman)
    h_{a,b}(k) = ((a * k + b) mod p) mod m
where p = 2^61 - 1 is prime, a is chosen at random from [1, p-1] and b from
[0, p-1]. For any two distinct keys, Pr[h(k1) == h(k2)] <= 1/m.
Non-integer keys (e.g. strings) are first mapped to integers with Python's
built-in hash().

Collisions are resolved by chaining: each slot holds a Python list of
(key, value) pairs.

Dynamic resizing:
  * grow  (double m) when the load factor n/m exceeds max_load (default 0.75)
  * shrink (halve m) when n/m drops below min_load (default 0.25)
A new random hash function is drawn each time the table is resized.
"""

import random


class HashTableChaining:
    _P = (1 << 61) - 1  # Mersenne prime 2^61 - 1

    def __init__(self, capacity=8, max_load=0.75, min_load=0.25,
                 auto_resize=True, seed=None):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        if not 0 < min_load < max_load:
            raise ValueError("need 0 < min_load < max_load")
        self._rng = random.Random(seed)
        self._min_capacity = capacity
        self._m = capacity
        self._buckets = [[] for _ in range(capacity)]
        self._n = 0
        self.max_load = max_load
        self.min_load = min_load
        self.auto_resize = auto_resize
        self._choose_hash_function()

    # ---------- hashing ----------
    def _choose_hash_function(self):
        self._a = self._rng.randrange(1, self._P)
        self._b = self._rng.randrange(0, self._P)

    def _index(self, key):
        k = hash(key) % self._P
        return ((self._a * k + self._b) % self._P) % self._m

    def _find(self, key):
        """Return (bucket, position) of key; position is -1 if not present."""
        bucket = self._buckets[self._index(key)]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                return bucket, i
        return bucket, -1

    # ---------- core operations ----------
    def insert(self, key, value):
        """Add a key-value pair (updates the value if the key already exists)."""
        bucket, i = self._find(key)
        if i >= 0:
            bucket[i] = (key, value)
            return
        bucket.append((key, value))
        self._n += 1
        if self.auto_resize and self._n > self.max_load * self._m:
            self._resize(2 * self._m)

    def search(self, key):
        """Return the value stored for key. Raises KeyError if key is absent."""
        bucket, i = self._find(key)
        if i < 0:
            raise KeyError(key)
        return bucket[i][1]

    def get(self, key, default=None):
        """Like search(), but returns `default` instead of raising KeyError."""
        bucket, i = self._find(key)
        return bucket[i][1] if i >= 0 else default

    def delete(self, key):
        """Remove key and return its value. Raises KeyError if key is absent."""
        bucket, i = self._find(key)
        if i < 0:
            raise KeyError(key)
        value = bucket[i][1]
        bucket[i] = bucket[-1]   # swap with the last pair, then pop: O(1)
        bucket.pop()
        self._n -= 1
        if (self.auto_resize and self._m > self._min_capacity
                and self._n < self.min_load * self._m):
            self._resize(max(self._min_capacity, self._m // 2))
        return value

    # ---------- resizing ----------
    def _resize(self, new_m):
        old_buckets = self._buckets
        self._m = new_m
        self._buckets = [[] for _ in range(new_m)]
        self._choose_hash_function()
        for bucket in old_buckets:
            for k, v in bucket:
                self._buckets[self._index(k)].append((k, v))

    # ---------- helpers ----------
    @property
    def num_slots(self):
        return self._m

    @property
    def load_factor(self):
        return self._n / self._m

    def chain_stats(self):
        lengths = [len(b) for b in self._buckets]
        nonempty = [x for x in lengths if x]
        return {
            "max_chain": max(lengths),
            "avg_nonempty_chain": sum(nonempty) / len(nonempty) if nonempty else 0.0,
            "empty_slots": lengths.count(0),
        }

    def items(self):
        for bucket in self._buckets:
            yield from bucket

    def __len__(self):
        return self._n

    def __contains__(self, key):
        return self._find(key)[1] >= 0

    def __getitem__(self, key):
        return self.search(key)

    def __setitem__(self, key, value):
        self.insert(key, value)

    def __delitem__(self, key):
        self.delete(key)

    def __repr__(self):
        return (f"HashTableChaining(n={self._n}, slots={self._m}, "
                f"load_factor={self.load_factor:.2f})")


if __name__ == "__main__":
    table = HashTableChaining(seed=1)
    for word in ["apple", "banana", "cherry", "date", "elderberry"]:
        table.insert(word, len(word))
    print(table)
    print("search('cherry') ->", table.search("cherry"))
    print("delete('banana') ->", table.delete("banana"))
    print("'banana' in table ->", "banana" in table)