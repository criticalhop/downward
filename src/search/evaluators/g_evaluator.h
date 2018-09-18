#ifndef EVALUATORS_G_EVALUATOR_H
#define EVALUATORS_G_EVALUATOR_H

#include "../evaluator.h"

namespace g_evaluator {
class GEvaluator : public Evaluator {
public:
    GEvaluator() = default;
    virtual ~GEvaluator() override = default;

    virtual EvaluationResult compute_result(
        EvaluationContext &eval_context) override;

    virtual void get_path_dependent_evaluators(std::set<std::shared_ptr<Evaluator>> &) override {}
    //TODO: remove if shared_ptr to evaluators are used by all search algorithms
    virtual void get_path_dependent_evaluators(std::set<Evaluator *> &) override {}
};
}

#endif
