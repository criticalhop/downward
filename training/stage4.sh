# matplotlib is required to run this

# python3 ../src/subdominization-training/learning/train_model_for_domain.py --training-folder runs_folder --model-folder learning_m --model-type LRCV
# python3 ../src/subdominization-training/learning/train_model_for_domain.py --training-set-folder training_data --model-folder learned_model --model-type LINR


# python3 ../src/subdominization-training/learning/train_model_for_domain.py --training-set-folder training_data --model-folder learning_m --model-type RF_RG --keep-duplicate-features
# python ../src/subdominization-training/learning/train_model_for_domain.py --training-set-folder training_data --model-folder learning_m --model-type RF_RG

#python3 ../src/subdominization-training/learning/train_model_for_domain.py --training-set-folder training_data/training --model-folder learned_model --model-type SVR
python3 ../src/subdominization-training/learning/train_model_for_domain.py --training-set-folder training_data_merged_r2 --model-folder learned_model_svc_r2 --model-type SVC
