# matplotlib is required to run this

# python3 ../src/subdominization-training/learning/train_model_for_domain.py --training-folder runs_folder --model-folder learning_m --model-type LRCV
# python3 ../src/subdominization-training/learning/train_model_for_domain.py --training-set-folder training_data --model-folder learned_model --model-type LINR
python3 ../src/subdominization-training/learning/train_model_for_domain.py --training-set-folder training_data --model-folder learned_model --model-type SVR
