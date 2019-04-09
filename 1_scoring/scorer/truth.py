"""
Ground truth
Copyright 2017 @ Georgetown University
"""
import xml.etree.ElementTree as ET
from collections import defaultdict
import math
import pickle
import io
import sys
import numpy as np


class DDTruth:
    """
    truth=
    {
        topic_id:
        {
            subtopic_id:
            {
                doc_no:
                {
                    passage_id:
                    {
                        nugget_id:
                        rating:
                    }
                }
            }
        }
    }
    """

    def __init__(self, truth_xml_path, track, doc_length=dict(), max_doc_rel=True):
    
        self.doc_length = doc_length
        # sort in ascending order
        self.sorted_doc_len = sorted(self.doc_length.items(), key=lambda x: x[1])
        self.max_doc_rel = max_doc_rel
        print(self.max_doc_rel)
        if track == 'DD':
            self.init_dd(truth_xml_path)
        elif track == 'S':
            self.init_s(truth_xml_path)
        else:
           print('The track name is wrong.')
           sys.exit(0)
        
        
    def init_dd(self, truth_xml_path):
        
        self.truth = defaultdict(dict)

        root = ET.parse(truth_xml_path).getroot()

        for domain in list(root):
            for topic in list(domain):
                topic_id = topic.attrib['id']

                for subtopic in list(topic):
                    if subtopic.tag == 'subtopic':
                        subtopic_id = subtopic.attrib['id']
                        subtopic_data = defaultdict(dict)
                        nugget_id = ''
                        doc_no, rating = '', 0
                        for passage in list(subtopic):
                            passage_data = {}
                            passage_id = passage.attrib['id']

                            for tag_under_passage in list(passage):
                                if tag_under_passage.tag == 'docno':
                                    doc_no = tag_under_passage.text
                                elif tag_under_passage.tag == 'rating':
                                    rating = int(tag_under_passage.text)
                                    if rating == 0:
                                        rating = 1
                                elif tag_under_passage.tag == 'type':
                                    if tag_under_passage.text == 'MANUAL':
                                        nugget_id = passage_id

                            passage_data['nugget_id'] = nugget_id
                            passage_data['rating'] = rating

                            subtopic_data[doc_no][passage_id] = passage_data

                        self.truth[topic_id][subtopic_id] = subtopic_data
                        
    def init_s(self, truth_xml_path):
        def rec_dd():
            return defaultdict(rec_dd)
        
        self.truth = rec_dd()

        with io.open(truth_xml_path, mode="r", encoding="utf-8") as f:
        
            for line in f:
                l = line.replace('\n','').strip().split('\t')
                topic_id = l[0]
                doc_no = l[1]
                rating = int(l[2])
                passage_data = {}
                passage_data['nugget_id'] = 0
                if rating == -2:
                    rating = 0
                passage_data['rating'] = rating

                self.truth[topic_id][0][doc_no][0] = passage_data
    

    def truth4SDCG(self, topic_id):
        """return doc_no: rating"""
        return_data = defaultdict(int)
        for subtopic_id, subtopic_data in self.truth[topic_id].items():
            for doc_no, doc_data in subtopic_data.items():
                if self.max_doc_rel:
                    ratings = []
                    for _, passage_data in doc_data.items():
                        ratings.append(passage_data['rating'])
                        return_data[doc_no] = max(ratings)
                else:
                    for _, passage_data in doc_data.items():
                        return_data[doc_no] += passage_data['rating']
        return return_data
    
    
    def truth4SDCG_bound(self, topic_id):
        return self.truth4SDCG(topic_id)

    def truth4SDCG_simple(self, topic_id):
        return self.truth4SDCG(topic_id)

    def truth4SDCG_bound_simple(self, topic_id):
        return self.truth4SDCG(topic_id)


    def truth4CT(self, topic_id):
        """return doc_no: {subtopic_id: rating}, subtopic_num"""

        return_data = defaultdict(dict)
        for subtopic_id, subtopic_data in self.truth[topic_id].items():
            for doc_no, doc_data in subtopic_data.items():
                ratings = []
                for _, passage_data in doc_data.items():
                    ratings.append(passage_data['rating'])
                if self.max_doc_rel:
                    r2 = max(ratings)
                else:
                    ratings = sorted(ratings, reverse=True)
                    r1 = 0  # with discount
                    r2 = 0  # no discount
                    for i in range(len(ratings)):
                        r1 += ratings[i] / math.log(i + 2, 2)
                        r2 += ratings[i]
                return_data[doc_no][subtopic_id] = r2

        return return_data, len(self.truth[topic_id])


    def truth4CT_simple(self, topic_id):
        """return doc_no: {subtopic_id: rating}, subtopic_num"""
        return_data = defaultdict(lambda: defaultdict(int))
        doc_list = defaultdict(list)
        for subtopic_id, subtopic_data in self.truth[topic_id].items():
            for doc_no, doc_data in subtopic_data.items():
                    for _, passage_data in doc_data.items():
                        doc_list[doc_no].append(passage_data['rating'])
        for doc_no in doc_list:
            if self.max_doc_rel:
                return_data[doc_no]['no subtopics'] = max(doc_list[doc_no])
            else:
                return_data[doc_no]['no subtopics'] = sum(doc_list[doc_no])
        return return_data, 1


    def truth4CT_bound(self, topic_id):
        return self.truth4CT(topic_id)
        
    def truth4CT_bound_simple(self, topic_id):
        return self.truth4CT_simple(topic_id)
    
    
    def truth4EU(self, topic_id):
        """return doc_no:[nugget_id1, nugget_id2,....],  nugget_id: rating, doc: length"""
        doc_nugget = defaultdict(list)  # doc_no -> nugget list
        nugget_rating = defaultdict(int)  # nugget_id -> rating
        for subtopic_id, subtopic_data in self.truth[topic_id].items():
            for doc_no, doc_data in subtopic_data.items():
                for passage_id, passage_data in doc_data.items():
                    doc_nugget[doc_no].append(passage_data['nugget_id'])
                    if passage_data['nugget_id'] in nugget_rating and nugget_rating[passage_data['nugget_id']] != \
                            passage_data['rating']:
                        print('failed!')
                    nugget_rating[passage_data['nugget_id']] = passage_data['rating']
        return doc_nugget, nugget_rating, self.doc_length


    #CHECK why is this different from above
    def truth4EU_bound(self, topic_id):
        """return nugget_id:[doc_no1, doc_no2, ... ], nugget_id: rating, sorted (doc, length)"""
        nugget_doc = defaultdict(list)  # nugget -> doc_no list
        nugget_rating = defaultdict(int)  # nugget_id -> rating
        for subtopic_id, subtopic_data in self.truth[topic_id].items():
            for doc_no, doc_data in subtopic_data.items():
                for passage_id, passage_data in doc_data.items():
                    nugget_id = passage_data["nugget_id"]
                    if doc_no not in nugget_doc[nugget_id]:
                        nugget_doc[nugget_id].append(doc_no)

                    nugget_rating[nugget_id] = passage_data['rating']

        return nugget_doc, nugget_rating, self.sorted_doc_len

    def truth4EU_simple(self, topic_id):
        """return doc_no:[nugget_id1, nugget_id2,....],  nugget_id: rating, doc: length"""
        doc_nugget = defaultdict(list)  # doc_no -> nugget list
        nugget_rating = defaultdict(int)  # nugget_id -> rating
        doc_list = defaultdict(list)
        for subtopic_id, subtopic_data in self.truth[topic_id].items():
            for doc_no, doc_data in subtopic_data.items():
                for passage_id, passage_data in doc_data.items():
                    if doc_no not in doc_nugget[doc_no]:
                        doc_nugget[doc_no].append(doc_no)
                    doc_list[doc_no].append(passage_data['rating'])

        for doc_no in doc_list:
            if self.max_doc_rel:
                nugget_rating[doc_no] = max(doc_list[doc_no])
            else:
                nugget_rating[doc_no] = sum(doc_list[doc_no])
        return doc_nugget, nugget_rating, self.doc_length

    def truth4EU_bound_simple(self, topic_id):
        """return nugget_id:[doc_no1, doc_no2, ... ], nugget_id: rating, sorted (doc, length)"""
        nugget_doc = defaultdict(list)  # nugget -> doc_no list
        nugget_rating = defaultdict(int)  # nugget_id -> rating
        doc_list = defaultdict(list)        
        for subtopic_id, subtopic_data in self.truth[topic_id].items():
            for doc_no, doc_data in subtopic_data.items():
                for passage_id, passage_data in doc_data.items():
                    nugget_id = doc_no #passage_data["nugget_id"]
                    if doc_no not in nugget_doc[nugget_id]:
                        nugget_doc[nugget_id].append(doc_no)
                    doc_list[doc_no].append(passage_data['rating'])
        for doc_no in doc_list:
            if self.max_doc_rel:
                nugget_rating[doc_no] = max(doc_list[doc_no])
            else:
                nugget_rating[doc_no] = sum(doc_list[doc_no])

        return nugget_doc, nugget_rating, self.sorted_doc_len

    def stats(self):
        """print the statistic information about the ground truth"""
        topic_num = 0

        subtopic_num = 0

        total_doc = set()
        topic_doc_set = defaultdict(set)
        doc_num = 0
        for topic_id in self.truth:
            topic_num += 1
            topic_doc = set()
            
            for subtopic_id in self.truth[topic_id]:
                subtopic_num += 1
                for doc_no in self.truth[topic_id][subtopic_id]:
                    topic_doc_set[topic_id].add(doc_no)
                    topic_doc.add(doc_no)
                    total_doc.add(doc_no)
            doc_num += len(topic_doc)

        rel_docs = []
        for topic_id in topic_doc_set:
            rel_docs.append(len(topic_doc_set[topic_id]))
        print("Topic num:", topic_num)
        print("Subtopic num:", subtopic_num)
        print("Avg subtopic per topic:", subtopic_num / topic_num)

        print("Total Relevant Documents:", len(total_doc))
        print("Avg doc per topic:", doc_num / topic_num)
        print("Avg doc per topic:", np.mean(rel_docs))
        print("Std doc per topic:", np.std(rel_docs))
        print("Median doc per topic:", np.median(rel_docs))                                                        

if __name__ == '__main__':
    # dd_truth = DDTruth('data/trec_dd_15/truth/dynamic-domain-2015-truth-data-v5.xml')
    dd_truth = DDTruth('data/trec_dd_16/truth/dynamic-domain-2016-truth-data.xml')
    dd_truth.stats()
    # dd_truth.truth_check_4_EU()
    # dd_truth.self_check()
    import pprint

    # pprint.pprint(dd_truth.truth_4_CT('DD16-1'))
    """
    for  i in range(1, 54):
        topic_id = "DD16-"+str(i)
        t, _ = dd_truth.truth_4_CT(topic_id)
        print(len(t))
    """

