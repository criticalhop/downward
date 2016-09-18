#ifndef UTILS_ORDERED_SET_H
#define UTILS_ORDERED_SET_H

#include <cassert>
#include <unordered_set>
#include <vector>

namespace utils {
template <typename T>
class OrderedSet {
    std::vector<T> ordered_items;
    std::unordered_set<T> unordered_items;

public:
    bool empty() const {
        assert(!(unordered_items.empty() ^ ordered_items.empty()));
        return ordered_items.empty();
    }

    void clear() {
        ordered_items.clear();
        unordered_items.clear();
        assert(empty());
    }

    void add(const T &item) {
        if (!unordered_items.count(item)) {
            ordered_items.push_back(item);
            unordered_items.insert(item);
        }
        assert(unordered_items.size() <= ordered_items.size());
    }

    std::vector<T> extract_items() {
        std::vector<T> items = std::move(ordered_items);
        unordered_items.clear();
        assert(empty());
        return items;
    }
};
}

#endif
