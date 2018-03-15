#ifndef ALGORITHMS_INT_HASH_SET_H
#define ALGORITHMS_INT_HASH_SET_H

#include "../utils/collections.h"
#include "../utils/language.h"
#include "../utils/system.h"

#include <algorithm>
#include <cassert>
#include <iostream>
#include <utility>
#include <vector>

namespace int_hash_set {
/*
  Hash set using a single vector for storing non-negative integer keys.

  Usage:

  IntHashSet<MyHasher, MyEqualityTester> s;
  pair<int, bool> result1 = s.insert(3);
  assert(result1 == make_pair(3, true));
  pair<int, bool> result2 = s.insert(3);
  assert(result2 == make_pair(3, false));

  Limitations:

  The range of valid keys is [0, 2^31 - 1]. This range could be extended to [0,
  2^32 - 1] without using more memory by using unsigned integers for the keys
  and a different designated value for empty buckets (currently we use -1 for
  this).

  The maximum capacity (i.e., number of buckets) is 2^30 because we use a
  signed integer to store it and the next larger power of 2 (2^31) is too big
  for an int. The maximum capacity could be raised by storing the number of
  buckets in a larger data type.

  Implementation:

  We use ideas from hopscotch hashing
  (https://en.wikipedia.org/wiki/Hopscotch_hashing) to ensure that each key is
  at most "max_distance" buckets away from its ideal bucket. This ensures
  constant lookup times since we always need to check at most "max_distance"
  buckets. Since all buckets we need to check for a given key are aligned in
  memory, the lookup has good cache locality.
*/
template<typename Hasher, typename Equal>
class IntHashSet {
    using KeyType = int;
    using HashType = unsigned int;

    // Max distance from the ideal bucket to the actual bucket for each key.
    static const int max_distance = 32;

    struct Bucket {
        KeyType key;
        HashType hash;

        static const KeyType empty_bucket_key = -1;

        Bucket()
            : key(empty_bucket_key),
              hash(0) {
        }

        Bucket(KeyType key, HashType hash)
            : key(key),
              hash(hash) {
        }

        bool full() const {
            return key != empty_bucket_key;
        }
    };

    Hasher hasher;
    Equal equal;
    std::vector<Bucket> buckets;
    int num_entries;
    int num_resizes;

    int capacity() const {
        return buckets.size();
    }

    void rehash(int new_capacity) {
        assert(new_capacity >= 1);
        int num_entries_before = num_entries;
        std::vector<Bucket> old_buckets = std::move(buckets);
        assert(buckets.empty());
        num_entries = 0;
        buckets.resize(new_capacity);
        for (const Bucket &bucket : old_buckets) {
            if (bucket.full()) {
                insert(bucket.key, bucket.hash);
            }
        }
        utils::unused_variable(num_entries_before);
        assert(num_entries == num_entries_before);
        ++num_resizes;
    }

    void enlarge() {
        int num_buckets = buckets.size();
        assert(num_buckets == 1 || num_buckets % 2 == 0);
        if (num_buckets == (1 << 30)) {
            std::cerr << "Int hash set surpassed maximum capacity. Aborting."
                      << std::endl;
            utils::exit_with(utils::ExitCode::CRITICAL_ERROR);
        }
        rehash(num_buckets * 2);
    }

    int get_bucket(HashType hash) const {
        /* Since the number of buckets is restricted to powers of 2,
           we can use "i % 2^n = i & (2^n - 1)" to speed this up. */
        assert(!buckets.empty());
        return hash & (buckets.size() - 1);
    }

    /*
      Return distance from index1 to index2, only moving right and wrapping
      from the last to the first bucket.
    */
    int get_distance(int index1, int index2) const {
        assert(utils::in_bounds(index1, buckets));
        assert(utils::in_bounds(index2, buckets));
        if (index2 >= index1) {
            return index2 - index1;
        } else {
            return capacity() + index2 - index1;
        }
    }

    int find_next_free_bucket_index(int index) const {
        assert(num_entries < capacity());
        assert(utils::in_bounds(index, buckets));
        while (buckets[index].full()) {
            index = get_bucket(index + 1);
        }
        return index;
    }

    KeyType find_equal_key(KeyType key, HashType hash) const {
        assert(hasher(key) == hash);
        int ideal_index = get_bucket(hash);
        for (int i = 0; i < max_distance; ++i) {
            int index = get_bucket(ideal_index + i);
            const Bucket &bucket = buckets[index];
            if (bucket.full() && bucket.hash == hash && equal(bucket.key, key)) {
                return bucket.key;
            }
        }
        return Bucket::empty_bucket_key;
    }

    /*
      Private method that inserts a key and its corresponding hash into the
      hash set.

      The method ensures that each key is at most "max_distance" buckets away
      from its ideal bucket by moving the closest free bucket towards the ideal
      bucket. If this can't be achieved, we resize the vector, reinsert the old
      keys and try inserting the new key again.

      For the return type, see the public insert() method.

      Note that the private insert() may call enlarge() and therefore rehash(),
      which itself calls the private insert() again.
    */
    std::pair<KeyType, bool> insert(KeyType key, HashType hash) {
        assert(hasher(key) == hash);

        /* If the hash set already contains the key, return the key and a
           Boolean indicating that no new key has been inserted. */
        KeyType equal_key = find_equal_key(key, hash);
        if (equal_key != Bucket::empty_bucket_key) {
            return std::make_pair(equal_key, false);
        }

        assert(num_entries <= capacity());
        if (num_entries == capacity()) {
            enlarge();
        }
        assert(num_entries < capacity());

        // Compute ideal bucket.
        int ideal_index = get_bucket(hash);

        // Find first free bucket left of the ideal bucket.
        int free_index = find_next_free_bucket_index(ideal_index);

        /*
          While the free bucket is too far from the ideal bucket, move the free
          bucket towards the ideal bucket by swapping a suitable third bucket
          with the free bucket. A full and an empty bucket can be swapped if
          the swap doesn't move the full bucket too far from its ideal
          position.
        */
        while (get_distance(ideal_index, free_index) >= max_distance) {
            bool swapped = false;
            int num_buckets = capacity();
            int max_offset = std::min(max_distance, num_buckets) - 1;
            for (int offset = max_offset; offset >= 1; --offset) {
                assert(offset < num_buckets);
                int candidate_index = free_index + num_buckets - offset;
                assert(candidate_index >= 0);
                candidate_index = get_bucket(candidate_index);
                HashType candidate_hash = buckets[candidate_index].hash;
                int candidate_ideal_index = get_bucket(candidate_hash);
                if (get_distance(candidate_ideal_index, free_index) < max_distance) {
                    // Candidate can be swapped.
                    std::swap(buckets[candidate_index], buckets[free_index]);
                    free_index = candidate_index;
                    swapped = true;
                    break;
                }
            }
            if (!swapped) {
                /* Free bucket could not be moved close enough to ideal bucket.
                   -> Enlarge and try inserting again. */
                enlarge();
                return insert(key, hash);
            }
        }
        assert(utils::in_bounds(free_index, buckets));
        assert(!buckets[free_index].full());
        buckets[free_index] = Bucket(key, hash);
        ++num_entries;
        return std::make_pair(key, true);
    }

public:
    IntHashSet(const Hasher &hasher, const Equal &equal)
        : hasher(hasher),
          equal(equal),
          buckets(1),
          num_entries(0),
          num_resizes(0) {
    }

    int size() const {
        return num_entries;
    }

    /*
      Insert a key into the hash set.

      Return a pair whose first item is the given key, or an equivalent key
      already contained in the hash set. The second item in the pair is a bool
      indicating whether a new key was inserted into the hash set.
    */
    std::pair<KeyType, bool> insert(KeyType key) {
        assert(key >= 0);
        return insert(key, hasher(key));
    }

    void dump() const {
        int num_buckets = capacity();
        std::cout << "[";
        for (int i = 0; i < num_buckets; ++i) {
            const Bucket &bucket = buckets[i];
            if (bucket.full()) {
                std::cout << bucket.key;
            } else {
                std::cout << "_";
            }
            if (i < num_buckets - 1) {
                std::cout << ", ";
            }
        }
        std::cout << "]" << std::endl;
    }

    void print_statistics() const {
        assert(!buckets.empty());
        int num_buckets = capacity();
        assert(num_buckets != 0);
        std::cout << "Int hash set load factor: " << num_entries << "/"
                  << num_buckets << " = "
                  << static_cast<double>(num_entries) / num_buckets
                  << std::endl;
        std::cout << "Int hash set resizes: " << num_resizes << std::endl;
    }
};
}

#endif
