#include "utils.h"

#include <cassert>
#include <fstream>
#include <set>
#include <sstream>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#include "../globals.h"
#include "../operator.h"
#include "../option_parser.h"
#include "../state.h"
#include "../utilities.h"
#include "../landmarks/landmark_factory_rpg_sasp.h"
#include "../landmarks/landmark_graph.h"

using namespace std;

namespace cegar_heuristic {
bool DEBUG = false;
typedef unordered_map<int, unordered_set<int> > Edges;

Operator create_op(const string desc) {
    istringstream iss("begin_operator\n" + desc + "\nend_operator");
    return Operator(iss, false);
}

Operator create_op(const string name, vector<string> prevail, vector<string> pre_post, int cost) {
    ostringstream oss;
    // Create operator description.
    oss << name << endl << prevail.size() << endl;
    for (int i = 0; i < prevail.size(); ++i)
        oss << prevail[i] << endl;
    oss << pre_post.size() << endl;
    for (int i = 0; i < pre_post.size(); ++i)
        oss << pre_post[i] << endl;
    oss << cost;
    return create_op(oss.str());
}

State *create_state(const string desc) {
    string full_desc = "begin_state\n" + desc + "\nend_state";
    istringstream iss(full_desc);
    return new State(iss);
}

int get_pre(const Operator &op, int var) {
    for (int i = 0; i < op.get_prevail().size(); i++) {
        const Prevail &prevail = op.get_prevail()[i];
        if (prevail.var == var)
            return prevail.prev;
    }
    for (int i = 0; i < op.get_pre_post().size(); i++) {
        const PrePost &pre_post = op.get_pre_post()[i];
        if (pre_post.var == var)
            return pre_post.pre;
    }
    return UNDEFINED;
}

int get_post(const Operator &op, int var) {
    for (int i = 0; i < op.get_prevail().size(); ++i) {
        const Prevail &prevail = op.get_prevail()[i];
        if (prevail.var == var)
            return prevail.prev;
    }
    for (int i = 0; i < op.get_pre_post().size(); ++i) {
        const PrePost &pre_post = op.get_pre_post()[i];
        if (pre_post.var == var)
            return pre_post.post;
    }
    return UNDEFINED;
}

void get_unmet_preconditions(const Operator &op, const State &state, Splits *splits) {
    assert(splits->empty());
    for (int i = 0; i < op.get_prevail().size(); ++i) {
        const Prevail &prevail = op.get_prevail()[i];
        if (state[prevail.var] != prevail.prev) {
            vector<int> wanted;
            wanted.push_back(prevail.prev);
            splits->push_back(make_pair(prevail.var, wanted));
        }
    }
    for (int i = 0; i < op.get_pre_post().size(); ++i) {
        const PrePost &pre_post = op.get_pre_post()[i];
        if ((pre_post.pre != -1) && (state[pre_post.var] != pre_post.pre)) {
            vector<int> wanted;
            wanted.push_back(pre_post.pre);
            splits->push_back(make_pair(pre_post.var, wanted));
        }
    }
    assert(splits->empty() == op.is_applicable(state));
}

void get_unmet_goal_conditions(const State &state, Splits *splits) {
    assert(splits->empty());
    for (int i = 0; i < g_goal.size(); i++) {
        int var = g_goal[i].first;
        int value = g_goal[i].second;
        if (state[var] != value) {
            vector<int> wanted;
            wanted.push_back(value);
            splits->push_back(make_pair(var, wanted));
        }
    }
}

bool goal_var(int var) {
    for (int i = 0; i < g_goal.size(); i++) {
        if (var == g_goal[i].first)
            return true;
    }
    return false;
}

bool test_cegar_goal(const State &state) {
    for (int i = 0; i < g_goal.size(); i++) {
        if (state[g_goal[i].first] != g_goal[i].second) {
            return false;
        }
    }
    return true;
}

bool cheaper(Operator *op1, Operator* op2) {
    return op1->get_cost() < op2->get_cost();
}

void partial_ordering(Edges &predecessors, Edges &successors, vector<int> *order) {
    assert(order->empty());
    bool debug = true;
    // Set of nodes that still have to be ordered.
    set<int> nodes;
    for (auto it = predecessors.begin(); it != predecessors.end(); ++it) {
        nodes.insert(it->first);
    }
    for (auto it = successors.begin(); it != successors.end(); ++it) {
        nodes.insert(it->first);
    }
    const int num_nodes = nodes.size();
    vector<int> front;
    vector<int> back;
    while (!nodes.empty()) {
        int front_in = INF;
        int front_out = -1;
        int front_node = -1;
        int back_in = -1;
        int back_out = INF;
        int back_node = -1;
        for (auto it = nodes.begin(); it != nodes.end(); ++it) {
            unordered_set<int> &pre = predecessors[*it];
            unordered_set<int> &succ = successors[*it];
            if (debug) {
                cout << "pre(" << *it << "): ";
                for (auto p = pre.begin(); p != pre.end(); ++p)
                    cout << *p << " ";
                cout << "(" << succ.size() << " succ)" << endl;
            }
            // A node is a better front_node if it has fewer incoming or more
            // outgoing edges.
            if ((pre.size() < front_in) || ((pre.size() == front_in) && (succ.size() > front_out))) {
                front_node = *it;
                front_in = pre.size();
                front_out = succ.size();
            }
            // A node is a better back_node if it has fewer outgoing edges or
            // more incoming edges.
            if ((succ.size() < back_out) || ((succ.size() == back_out) && (pre.size() > back_in))) {
                back_node = *it;
                back_in = pre.size();
                back_out = succ.size();
            }
        }
        assert(front_node >= 0);
        assert(back_node >= 0);
        int node = -1;
        if ((front_in < back_out) || ((front_in == back_out) && (front_out >= back_in))) {
            // When many edges leave the front node, it should probably be put in front.
            node = front_node;
            front.push_back(node);
            if (debug)
                cout << "Put in front: " << node << endl << endl;
        } else {
            node = back_node;
            back.push_back(node);
            if (debug)
                cout << "Put in back: " << node << endl << endl;
        }
        nodes.erase(node);
        // For all unsorted nodes, delete node from their predecessor and
        // successor lists.
        for (auto it = nodes.begin(); it != nodes.end(); ++it) {
            unordered_set<int> &pre = predecessors[*it];
            unordered_set<int>::iterator pos = find(pre.begin(), pre.end(), node);
            if (pos != pre.end())
                pre.erase(pos);
            unordered_set<int> &succ = successors[*it];
            pos = find(succ.begin(), succ.end(), node);
            if (pos != succ.end())
                succ.erase(pos);
        }
    }
    reverse(back.begin(), back.end());
    order->insert(order->begin(), front.begin(), front.end());
    order->insert(order->end(), back.begin(), back.end());
    if (order->size() != num_nodes)
        ABORT("Not all nodes have been ordered.");
}

void partial_ordering(const CausalGraph &causal_graph, vector<int> *order) {
    // For each variable, maintain sets of predecessor and successor variables
    // that haven't been ordered yet.
    Edges predecessors(g_variable_domain.size());
    Edges successors(g_variable_domain.size());
    for (int var = 0; var < g_variable_domain.size(); ++var) {
        const vector<int> &pre = causal_graph.get_predecessors(var);
        for (int i = 0; i < pre.size(); ++i) {
            predecessors[var].insert(pre[i]);
        }
        const vector<int> &succ = causal_graph.get_successors(var);
        for (int i = 0; i < succ.size(); ++i) {
            successors[var].insert(succ[i]);
        }
    }
    partial_ordering(predecessors, successors, order);
}

int get_fact_number(int var, int value) {
    return g_fact_borders[var] + value;
}

int get_fact_number(const LandmarkNode *node) {
    assert(node);
    assert(node->vars.size() == 1);
    int var = node->vars[0];
    int value = node->vals[0];
    return get_fact_number(var, value);
}

void get_fact_from_number(int fact_number, int &var, int &value) {
    var = 0;
    while (g_fact_borders[var] + g_variable_domain[var] <= fact_number)
        ++var;
    value = fact_number - g_fact_borders[var];
    assert(get_fact_number(var, value) == fact_number);
}

void order_facts_in_landmark_graph(vector<int> *ordered_fact_numbers) {
    Options opts = Options();
    opts.set<int>("cost_type", 0);
    opts.set<int>("memory_padding", 75);
    opts.set<bool>("reasonable_orders", true);
    opts.set<bool>("only_causal_landmarks", false);
    opts.set<bool>("disjunctive_landmarks", false);
    opts.set<bool>("conjunctive_landmarks", false);
    opts.set<bool>("no_orders", false);
    opts.set<int>("lm_cost_type", 0);
    opts.set<Exploration *>("explor", new Exploration(opts));
    LandmarkFactoryRpgSasp lm_graph_factory(opts);
    LandmarkGraph *graph = lm_graph_factory.compute_lm_graph();
    const set<LandmarkNode *> &nodes = graph->get_nodes();
    set<LandmarkNode *, LandmarkNodeComparer> nodes2(nodes.begin(), nodes.end());
    Edges predecessors;
    Edges successors;

    for (set<LandmarkNode *>::const_iterator it = nodes2.begin(); it
         != nodes2.end(); it++) {
        LandmarkNode *node_p = *it;
        for (auto parent_it = node_p->parents.begin(); parent_it
             != node_p->parents.end(); ++parent_it) {
            //const edge_type &edge = parent_it->second;
            const LandmarkNode *parent_p = parent_it->first;
            int node_number = get_fact_number(node_p);
            int parent_number = get_fact_number(parent_p);
            predecessors[node_number].insert(parent_number);
            successors[parent_number].insert(node_number);
        }
    }
    partial_ordering(predecessors, successors, ordered_fact_numbers);
    cout << "Ordering: " << to_string(*ordered_fact_numbers) << endl;
    for (int i = 0; i < ordered_fact_numbers->size(); ++i) {
        int var = -1;
        int value = -1;
        get_fact_from_number((*ordered_fact_numbers)[i], var, value);
        cout << (*ordered_fact_numbers)[i] << " " << var << "=" << value << " " << g_fact_names[var][value] << endl;
    }
}

void write_causal_graph(const CausalGraph &causal_graph) {
    ofstream dotfile("causal-graph.dot");
    if (!dotfile.is_open()) {
        cout << "dot file for causal graph could not be opened" << endl;
        exit_with(EXIT_CRITICAL_ERROR);
    }
    dotfile << "digraph cg {" << endl;
    for (int var = 0; var < g_variable_domain.size(); ++var) {
        const vector<int> &successors = causal_graph.get_successors(var);
        for (int i = 0; i < successors.size(); ++i) {
            dotfile << "  " << var << " -> " << successors[i] << ";" << endl;
        }
    }
    for (int i = 0; i < g_goal.size(); i++) {
        int var = g_goal[i].first;
        dotfile << var << " [color=red];" << endl;
    }
    dotfile << "}" << endl;
    dotfile.close();
}

string to_string(int i) {
    stringstream out;
    out << i;
    return out.str();
}

string to_string(const vector<int> &v) {
    string sep = "";
    stringstream out;
    for (int i = 0; i < v.size(); ++i) {
        out << sep << v[i];
        sep = ",";
    }
    return out.str();
}
}
