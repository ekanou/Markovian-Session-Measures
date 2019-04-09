#!/usr/bin/env python

import sys
import os
import io
from oct2py import octave
import pickle
import argparse


def write_measurements(out_f, track, year, run, topic, MsM_lin, MsM_log):
    # write measurements
    out_f.write(
    '{track}\t{year}\t{run}\t{topic}'
    '\t{MsM_lin}\t{MsM_log}'
    '\n'.format(
        track = track,
        year = year,
        run = run,
        topic = topic,
        MsM_lin = MsM_lin,
        MsM_log = MsM_log
        ))#.decode('utf-8'))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--matlab_path', type=str, required=True)
    parser.add_argument('--out_path', type=str, required=True)
    parser.add_argument('--matrices_path', type=str, required=True)
    parser.add_argument('--config_file', type=str, required=True)    
    

    args = parser.parse_args()
    matlab_path = args.matlab_path
    out_path = args.out_path
    matrices_path = args.matrices_path
    config_file = args.config_file

    octave.addpath(matlab_path)

    with open(config_file,'r') as msm_f:
        msm_configs = eval(msm_f.read())

    # run linear and logarithmic variants
    # matlab function format: [m] = msm(run, p, q, r, s)
    for cfg in msm_configs.items():
        cfg_id = cfg[0]
        p,q,r,s = cfg[1]

        out_file = os.path.join(out_path, cfg_id + '.eval')
        with io.open(out_file, 'w', encoding='utf8') as out_f:
            out_f.write('dataset\tyear\trun\ttopic\t' + cfg_id + '_lin'
                        '\t' + cfg_id + '_log\n' #.decode('utf-8')
                        )

            topic_runs = [f for f in os.listdir(matrices_path) if f.endswith('m')]
            for topic_run in topic_runs:
                tr = topic_run.split('__')
                track = tr[0]
                year = tr[1]
                run = tr[2]
                rel = tr[3]
                topic = tr[4][:-2]

                if rel == 'max': continue

                print(topic_run)
                f = open(matrices_path + topic_run, 'rb')
                topic_matrix = pickle.load(f)
                f.close()
                
                # score
                m_lin = octave.msm_lin(topic_matrix, p,q,r,s)
                m_log = octave.msm_log(topic_matrix, p,q,r,s)

                write_measurements(out_f, track, year, run, topic, m_lin, m_log)


if __name__ == "__main__":
    sys.exit(main())
