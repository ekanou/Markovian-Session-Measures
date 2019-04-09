#!/usr/bin/env python

import sys
import os
import io
import argparse
from collections import Counter, defaultdict
import pickle
from scorer.reader import *
from scorer.truth import *
from scorer.sDCG import *
from scorer.expected_utility import *
from scorer.cubetest import *


def _years(runs_path):
    return [year for year in os.listdir(runs_path) if year.startswith('2')]

# session
def _runs_S(runs_path, year):
    path = runs_path + '/' + year + '/'
    return [(path + f, f[:-4]) for f in os.listdir(path) if f.endswith('run')]


# dynamic domain
def _file_path(root_dir, year, sub):
    path = root_dir + '/' +  year + '/' + sub + '/'
    file = [f for f in os.listdir(path) if not f.startswith('.')][0]
    return path + file


def _runs_DD(root_dir, year, sub):
    path = root_dir + '/' + year + '/' + sub + '/'
    return [(path + f, f) for f in os.listdir(path) if not f.startswith('.')]

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runs_path', type=str, required=True)
    parser.add_argument('--out_path', type=str, required=True)
    
    parser.add_argument('--cutoff', type=int, default=10)
    parser.add_argument('--list_depth', type=int, default=10)
    
    # DD=dynamic domain track, S=session track
    parser.add_argument('--track', type=str, required=True)

    parser.add_argument('--maxrel', type=str2bool, default=True)
    
    args = parser.parse_args()
    runs_path = args.runs_path
    out_path = args.out_path
    cutoff = args.cutoff
    list_depth = args.list_depth
    track = args.track
    max_doc_rel = args.maxrel
    print(max_doc_rel)
    
    out_file_path = os.path.join(out_path, track + '.new.max.eval')
    
    with io.open(out_file_path, 'w', encoding='utf8') as out_f:
        out_f.write('dataset\tyear\trun\ttopic\tsDCG\tnsDCG\tEU\tnEU\tCT\tnCT'
        '\tsDCGs\tnsDCGs\tEUs\tnEUs\tCTs\tnCTs\n')
    
        for year in _years(runs_path):
            print(year)
            if track == 'DD':
                truth_file_path = _file_path(runs_path, year, 'groundtruth')
                dd_info_path = _file_path(runs_path, year, 'params')
                doc_length = pickle.load(open(dd_info_path, 'rb'))
                truth = DDTruth(truth_file_path, 'DD', doc_length, max_doc_rel)
                runs = _runs_DD(runs_path, year, 'runs')
                
            for run, r_name in runs:
                print(run)
                print(r_name)
                itercorr = False
            
                run_result = DDReader(run, itercorr).run_result
            
                # sort by topic no
                sorted_results = sorted(run_result.items(), key=lambda x: \
                                        int(x[0].split('-')[1]))
                
                # sDCG params
                bq, b = 4, 2
                
                # EU params
                a, eu_gamma, p = 0.001, 0.5, 0.5
        
                # CT params
                ct_gamma, max_height = 0.5, 50
        
                for topic_id, topic_result in sorted_results:
                    sdcg, normalized_sdcg, utility, normalized_eu, ct, normalized_ct = 0,0,0,0,0,0
                    
                    if track == 'DD':
                        # sDCG
                        sdcg = sDCG_per_topic(truth.truth4SDCG(topic_id), \
                                    topic_result, bq, b, cutoff, list_depth)
                        sdcg_bound = sDCG_bound_per_topic( \
                                    truth.truth4SDCG_bound(topic_id), bq, b, \
                                    cutoff, list_depth)
                        normalized_sdcg = 0
                        if sdcg_bound != 0:
                            normalized_sdcg = sdcg / sdcg_bound
                        else:
                            print('Optimal dcg is equal to 0')
                            print(topic_id)
                            print(truth.truth4SDCG(topic_id))
                            print(topic_result)
                            break

                        
                        # EU
                        clear_prob()
                        utility = eu_per_topic(truth.truth4EU(topic_id), \
                                topic_result, a, eu_gamma, p, cutoff, list_depth)
                        upper, lower = eu_bound_per_topic( \
                                truth.truth4EU_bound(topic_id), a, eu_gamma, p, \
                                cutoff, list_depth)
                        normalized_eu = 0
                        if (upper - lower) != 0:
                            normalized_eu = (utility - lower) / (upper - lower)

                        # CT
                        gain, ct, act = cubetest_per_topic( \
                                            truth.truth4CT(topic_id), \
                                            topic_result, ct_gamma, max_height, \
                                            cutoff, list_depth)
                        bound = ct_bound_per_topic(truth.truth4CT_bound(topic_id),\
                                    ct_gamma, max_height, cutoff, list_depth)
                        normalized_ct = 0
                        if bound != 0:
                            normalized_ct = ct / bound
                    
                    # and again, without subtopics
                    
                    # sDCG
                    sdcg_s = sDCG_per_topic(truth.truth4SDCG_simple(topic_id),\
                                    topic_result, bq, b, cutoff, list_depth)
                    sdcg_bound_s = sDCG_bound_per_topic( \
                                    truth.truth4SDCG_bound_simple(topic_id), \
                                    bq, b, cutoff, list_depth)
                    normalized_sdcg_s = 0
                    if sdcg_bound_s != 0:
                        normalized_sdcg_s = sdcg_s / sdcg_bound_s
                    
                    # EU
                    clear_prob()
                    utility_s = eu_per_topic(truth.truth4EU_simple(topic_id), \
                                    topic_result, a, eu_gamma, p, cutoff, \
                                    list_depth)
                    upper_s, lower_s = eu_bound_per_topic( \
                                        truth.truth4EU_bound_simple(topic_id),\
                                        a, eu_gamma, p, cutoff, list_depth)
                    normalized_eu_s = (utility_s - lower_s)/(upper_s - lower_s)

                    # CT
                    gain_s, ct_s, act_s = cubetest_per_topic( \
                                            truth.truth4CT_simple(topic_id), \
                                            topic_result, ct_gamma, \
                                            max_height, cutoff, list_depth)
                    bound_s = ct_bound_per_topic( \
                                truth.truth4CT_bound_simple(topic_id), \
                                ct_gamma, max_height, cutoff, list_depth)
                    normalized_ct_s = 0
                    if bound_s != 0:
                        normalized_ct_s = ct_s / bound_s


                    # write measurements
                    out_f.write(
                    '{dataset}\t{year}\t{run}\t{topic}'
                    '\t{sDCG}\t{nsDCG}'
                    '\t{EU}\t{nEU}'
                    '\t{CT}\t{nCT}'
                    '\t{sDCGs}\t{nsDCGs}'
                    '\t{EUs}\t{nEUs}'
                    '\t{CTs}\t{nCTs}'
                    '\n'.format(
                        dataset = track,
                        year = year,
                        run = r_name,
                        topic = topic_id,
                        sDCG = sdcg,
                        nsDCG = normalized_sdcg,
                        EU = utility,
                        nEU = normalized_eu,
                        CT = ct,
                        nCT = normalized_ct,
                        sDCGs = sdcg_s,
                        nsDCGs = normalized_sdcg_s,
                        EUs = utility_s,
                        nEUs = normalized_eu_s,
                        CTs = ct_s,
                        nCTs = normalized_ct_s,
                        ))



if __name__ == "__main__":
    sys.exit(main())
