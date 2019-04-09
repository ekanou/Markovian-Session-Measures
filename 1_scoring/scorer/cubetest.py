"""
Cube Test
Copyright 2017 @ Georgetown University
"""

from scorer.truth import *
from scorer.reader import *
from collections import Counter
import statistics
import argparse
import sys


def cubetest(run_file_path, truth_xml_path, doc_len_path, gamma=0.5, max_height=100, cutoff=10, verbose=False, max_doc_rel=True):
    """return ct, act over all topics"""

    truth = DDTruth(truth_xml_path, doc_len_path, max_doc_rel)
    run_result = DDReader(run_file_path).run_result

    if verbose:
        print(run_file_path)
        print('%8s' % 'topic-id', '%10s' % ('ct@' + str(cutoff)), '%10s' % ('act@' + str(cutoff)), '%10s' % ('nct@' + str(cutoff)),
              sep='\t')

    ct_list, act_list = [], []
    gain_list = []
    normalized_ct_list = []
    sorted_results = sorted(run_result.items(), key=lambda x: int(x[0].split('-')[1]))
    for topic_id, topic_result in sorted_results:
        topic_truth = truth.truth4CT(topic_id)
        gain, ct, act = cubetest_per_topic(topic_truth, topic_result,
                                           gamma, max_height, cutoff, 1000000)

        ct_list.append(ct)
        act_list.append(act)
        gain_list.append(gain)

        bound = ct_bound_per_topic(truth.truth4CT_bound(topic_id), gamma, max_height, cutoff, 1000000)
        normalized_ct = ct / bound
        normalized_ct_list.append(normalized_ct)

        if verbose:
            print('%8s' % topic_id, '%10.7f' % ct, '%10.7f' % act, '%10.7f' % normalized_ct, sep='\t')

    if verbose:
        print('%8s' % 'all', '%10.7f' % statistics.mean(ct_list), '%10.7f' % statistics.mean(act_list), '%10.7f' % statistics.mean(normalized_ct_list),
              sep='\t')

    return gain_list, ct_list, act_list


def cubetest_per_topic(topic_truth, topic_result, gamma, max_height, cutoff, list_depth):
    """return gain, ct and act of one topic"""
    subtopic_num = topic_truth[1]
    topic_truth = topic_truth[0]
    subtopic_height = Counter()  # current height of every subtopic
    subtopic_count = Counter()  # #docs found relevant to every subtopic (nrels)

    weight_per_subtopic = 1.0 / subtopic_num

    def gain_per_doc(doc_no):
        if doc_no not in topic_truth:
            return 0
        gain = 0
        for subtopic_id, rating in topic_truth[doc_no].items():
            if subtopic_height[subtopic_id] < max_height:
                discount_height = (gamma ** (subtopic_count[subtopic_id] + 1)) * rating
                if discount_height + subtopic_height[subtopic_id] > max_height:
                    discount_height = max_height - subtopic_height[subtopic_id]

                gain += weight_per_subtopic * discount_height
                subtopic_height[subtopic_id] += discount_height
                subtopic_count[subtopic_id] += 1
        return gain

    sorted_result = sorted(topic_result.items(), key=lambda x: x[0])
    time = 0.0
    total_gain = 0
    accu_gain = 0
    doc_num = 0
    for iter_num, doc_list in sorted_result:
        if iter_num >= cutoff:
            break
        if(len(doc_list) > list_depth):
            doc_list = doc_list[:list_depth]
        time += 1
        for doc_no in doc_list:
            total_gain += gain_per_doc(doc_no)
            accu_gain += (total_gain / max_height / time)
            doc_num += 1

    if time != 0:
        ct = total_gain / max_height / time
    else:
        ct = 0
    if doc_num > 0:
        act = accu_gain / doc_num
    else:
        act = 0
    return total_gain / max_height, ct, act


def ct_bound_per_topic(topic_truth, gamma, max_height, cutoff, list_depth):
    doc_sub_rel, subtopic_num = topic_truth
    
    gain = 0
    subtopic_set = set()
    for doc_no in doc_sub_rel:
        for subtopic_id in doc_sub_rel[doc_no]:
            subtopic_set.add(subtopic_id)
    for subtopic_id in subtopic_set:
        subtopic_gain = 0
        rels = [doc_sub_rel[doc_no][subtopic_id] if subtopic_id in doc_sub_rel[doc_no]
                else 0
                for doc_no in doc_sub_rel]
        rels = sorted(rels, reverse=True)
        for i, rel in enumerate(rels):
            h = rel * (gamma ** i)
            if subtopic_gain + h >= max_height:
                h = max_height - subtopic_gain
            subtopic_gain += h
            if i >= cutoff * list_depth:
                break
        gain += subtopic_gain / subtopic_num

    opt_ct = gain / max_height #/ max_iter

    return opt_ct


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--runfile", required=True, help="run file path")
    parser.add_argument("--topics", required=True, help="topic xml file path")
    parser.add_argument("--params", required=True, help="file containing parameters for evaluation")
    parser.add_argument("--cutoff", required=True, type=int, help="first # iterations are taken into evaluation")

    params = parser.parse_args(sys.argv[1:])

    if params.cutoff <= 0:
        parser.error("cutoff value must be greater than 0")

    cubetest(params.runfile, params.topics, params.params, cutoff=params.cutoff, verbose=True)
