# matplotlib is required to run this

# Below fails with K-fold needed due to classes amt, see https://stackoverflow.com/questions/45139163/roc-auc-score-only-one-class-present-in-y-true
# python3 ../src/subdominization-training/learning/select_features.py --training-folder training_data --selector-type LOGRCV 

# python3 ../src/subdominization-training/learning/select_features.py --training-folder training_data --selector-type LINR
python3 ../src/subdominization-training/learning/select_features.py --training-folder training_data --selector-type SVR
