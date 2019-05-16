#!/usr/bin/env bash

python eval_runs.py \
    --runs_path "../9_data/runs/DD" \
    --out_path "../9_data/measurements"\
    --cutoff 10 \
    --list_depth 5 \
    --track "DD" \
    --maxrel "True"


