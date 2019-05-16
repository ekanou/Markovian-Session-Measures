#!/usr/bin/env python

import sys
import os
import pickle
import io
import argparse
from scorer.reader import *
from scorer.truth import *


def _years(runs_path, track):
    if track == 'DD':
        return [year for year in os.listdir(runs_path) if not
                year.startswith('.')]

# dynamic domain
def _file_path(root_dir, year, sub):
    path = root_dir + '/' +  year + '/' + sub + '/'
    file = [f for f in os.listdir(path) if not f.startswith('.')][0]
    return path + file


def _runs_DD(root_dir, year, sub):
    path = root_dir + '/' + year + '/' + sub + '/'
    return [(path + f, f) for f in os.listdir(path) if not f.startswith('.')]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runs_path', type=str, required=True)
    parser.add_argument('--out_path', type=str, required=True)
    
    parser.add_argument('--cutoff', type=int, default=10)
    parser.add_argument('--list_depth', type=int, default=10)
    
    # DD=dynamic domain track, S=session track
    parser.add_argument('--track', type=str, required=True)
    
    args = parser.parse_args()
    runs_path = args.runs_path
    out_path = args.out_path
    cutoff = args.cutoff
    list_depth = args.list_depth
    track = args.track

    for year in _years(runs_path, track):
        if track == 'DD':
            truth_file_path = _file_path(runs_path, year, 'groundtruth')
            dd_info_path = _file_path(runs_path, year, 'params')
            doc_length = pickle.load(open(dd_info_path, 'rb'))
            truth = DDTruth(truth_file_path, 'DD', doc_length, 'True')
            runs = _runs_DD(runs_path, year, 'runs')
        if track == 'S':
            runs = _runs_S(runs_path, year)
            
        for run, r_name in runs:
            itercorr = False
            
            run_result = DDReader(run, itercorr).run_result
        
            # sort by topic no
            sorted_results = sorted(run_result.items(), key=lambda x:
                                    int(x[0].split('-')[1]))

            for topic_id, topic_result in sorted_results:
                topic_matrix = [[0 for x in range(cutoff)] for y in range(list_depth)]
                topic_truth = truth.truth4SDCG(topic_id)
                sorted_result = sorted(topic_result.items(),key=lambda x: x[0])
                for query_pos, doc_list in sorted_result: # pos. starts from 0
                    if query_pos >= cutoff:
                        break
                    if(len(doc_list) > list_depth):
                        doc_list = doc_list[:list_depth]
                
                    for doc_pos, doc_no in enumerate(doc_list):
                        topic_matrix[doc_pos][query_pos] = topic_truth[doc_no]

                f = open(out_path + '/' + \
                            track + '__' + year + '__'  + \
                            r_name + '__sum__' + topic_id + '.m','wb')
                pickle.dump(topic_matrix, f)
                f.close()


if __name__ == "__main__":
    sys.exit(main())

