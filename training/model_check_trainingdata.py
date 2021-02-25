#! /usr/bin/env python

import sys
sys.path.append("../src")
sys.path.append("../src/subdominization-training")
sys.path.append("../src/subdominization-training/learning")
sys.path.append("../src/translate")
sys.nosetup = True  # workaround for argparse bug in fast-downward suite

import os
import numpy as np

import helpers
from collections import defaultdict
from rule_training_evaluator import *
from subdominization.model import TrainedModel
import lisp_parser
import shutil
import bz2

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import autosklearn.metrics
import sklearn.metrics
from sklearn import metrics 
from IPython import embed

try:
    # Python 3.x
    from builtins import open as file_open
except ImportError:
    # Python 2.x
    from codecs import open as file_open

import parsing_functions
import instantiate

def parse_pddl_file(type, filename):
    try:
        # The builtin open function is shadowed by this module's open function.
        # We use the Latin-1 encoding (which allows a superset of ASCII, of the
        # Latin-* encodings and of UTF-8) to allow special characters in
        # comments. In all other parts, we later validate that only ASCII is
        # used.
        return lisp_parser.parse_nested_list(file_open(filename,
                                                       encoding='ISO-8859-1'))
    except IOError as e:
        raise SystemExit("Error: Could not read file: %s\nReason: %s." %
                         (e.filename, e))
    except lisp_parser.ParseError as e:
        raise SystemExit("Error: Could not parse %s file: %s\nReason: %s." %
                         (type, filename, e))



if __name__ == "__main__":
    import argparse
    import os
    
    argparser = argparse.ArgumentParser()
    argparser.add_argument("domain", help="domain.pddl file")
    argparser.add_argument("problem", help="problem.pddl file")
    argparser.add_argument(
        "--truth-data", type=str,
        help="The folder containing training data *.csv and relevant_rules file")
    argparser.add_argument(
        "--trained-model-folder", type=str,
        help="The folder that should contain the trained model and relevant files if 'trained' is used as queue ordering")

    options = argparser.parse_args()

    domain_pddl = parse_pddl_file("domain", options.domain)
    task_pddl = parse_pddl_file("task", options.problem)

    task = parsing_functions.parse_task(domain_pddl, task_pddl)

    all_instances = sorted([d for d in os.listdir(options.truth_data)])
    np.random.seed(2018)
    # testing_instances = np.random.choice(all_instances, 20, replace=False)

    model = TrainedModel(options.trained_model_folder, task)

    remove_duplicate_features = True
    take_max_for_duplicates = True
    # testSize = 0.03
    testSize = 0.5


    for training_file in all_instances:        
        print ("Processing ", training_file)

        schema = training_file.split(".")[0]
        cur_model = model.model[schema].model

        # 1. test how internal methods operate on data

        dataset = helpers.get_dataset_from_csv(options.truth_data+"/"+training_file, not remove_duplicate_features, take_max_for_duplicates)
        
        if (dataset is None):
            continue
        
        # print dataset.shape
        # separate in features an target
        X, y = dataset.iloc[:,:-1], list(dataset.iloc[:, -1])

        # if we want to separate into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=testSize, random_state=1)

        X=X_train
        y=y_train

        # Standarize features
        scaler = StandardScaler(copy=True, with_mean=True, with_std=True)

        X_std = scaler.fit_transform(X)
        predictions = cur_model.predict(X_test)
        print("Accuracy score on TEST {:g} using {:s}".
            format(sklearn.metrics.accuracy_score(y_test, list(predictions)),
                    cur_model.automl_._metric.name))

        predictions = cur_model.predict(X_std)
        print("Accuracy score on REAL {:g} using {:s}".
            format(sklearn.metrics.accuracy_score(y, list(predictions)),
                    cur_model.automl_._metric.name))

        # 2. Test by manually checking the data directly, line-by-line
        if False:
            # Now run result with the model
            if cur_model.is_classifier:
                est = cur_model.predict_proba([eval])[0]
                # if len(est) > 1: est = est[1]
                # else: est = est[0]
            else:
                est = cur_model.predict([eval])[0]
            print(" --- ", est)

                           
    #print ("Only 0/1 rules: ", len(re.get_only_0_rules()), len(re.get_only_1_rules()), len(re.get_all_rules()))
