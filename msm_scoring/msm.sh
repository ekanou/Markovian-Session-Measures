#!/usr/bin/env bash

python score_msm.py \
    --matlab_path "../3_matlab_msm" \
    --out_path "../9_data/measurements" \
    --matrices_path  "../9_data/topic_matrices/" \
    --config_file "msm_configurations.txt"

