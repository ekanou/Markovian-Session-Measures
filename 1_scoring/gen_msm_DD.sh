#!/usr/bin/env bash


python generate_msm_matrices.py \
    --runs_path "../9_data/runs/DD" \
    --out_path "../9_data/topic_matrices"\
    --cutoff 10 \
    --list_depth 5 \
    --track "DD" \


