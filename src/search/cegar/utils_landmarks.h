#ifndef CEGAR_UTILS_LANDMARKS_H
#define CEGAR_UTILS_LANDMARKS_H

#include "utils.h"

#include <memory>
#include <unordered_map>
#include <utility>
#include <vector>

namespace Landmarks {
class LandmarkGraph;
}

// TODO: Move into "Landmarks" namespace and directory?
namespace CEGAR {
using VarToValues = std::unordered_map<int, std::vector<int>>;

extern std::unique_ptr<Landmarks::LandmarkGraph> get_landmark_graph();
extern std::vector<Fact> get_fact_landmarks(
    const Landmarks::LandmarkGraph &graph);

/*
  Do a breadth-first search through the landmark graph ignoring
  duplicates. Start at the node for the given fact and collect for each
  variable the facts that have to be made true before the given fact
  can be true for the first time.
*/
extern VarToValues get_prev_landmarks(
    const Landmarks::LandmarkGraph &graph, const Fact &fact);
}

#endif
