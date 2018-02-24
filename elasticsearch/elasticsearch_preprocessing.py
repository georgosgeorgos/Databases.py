from elasticsearch import Elasticsearch
import spacy
import gensim
from gensim.summarization.keywords import keywords
import time
import sys 
import json
import os

def put_body(result, body, ix, ratio=0.5, min_length=20):

    text = body.strip().replace("\\n", "\n").replace("\\r", "\r").lower()
    try:

        keywords = gensim.summarization.keywords(text, ratio=ratio, 
                                           split=True, 
                                           scores=True, pos_filter=['NN', 'JJ', 'VV'], 
                                           lemmatize=True)
        for key, weight in keywords:
            p = parser(key)
            pos = []
            for i in range(len(p)):
                pos.append(p[i].pos_)

            result[ix]["body"].append( { "key": key, "class": " ".join(pos), "weight": weight[0] } )

    except (ValueError, ZeroDivisionError):

        doc = parser(text)  
        for d in doc:
            lemma = d.lemma_
            if ( not d.is_stop and lemma.isalnum() ):
                result[ix]["body"].append( { "key": d.lemma_, "class": d.pos_, "weight": 1 } )
                
    return result

def put_title(result, title, ix):

    text = title.strip().replace("\\n", "\n").replace("\\r", "\r").lower()
    doc = parser(text)  
    for d in doc:
        lemma = d.lemma_
        if ( not d.is_stop and lemma.isalnum() ):
            result[ix]["title"].append( { "key": d.lemma_, "class": d.pos_, "weight": 1 } )
            
    return result

def main(parser, es):

    start = time.time()
    corpus_length = es.count(index="news", doc_type="document")["count"]

    try:
        with open('result.json', 'r') as f:
            result = json.load(f)

        logic = False
        ix = result["ix"]

        for i in range(ix, corpus_length):

            if i not in result or not logic:
                logic = True

                file = es.get(index="news", doc_type="document", id=i)
                source = file["_source"]
                title = source.get("title", "")
                body = source.get("body", "")
                
                result[i] = { "body": [], "title": [] , "body_raw": body, "title_raw": title}

                result = put_title(result, title, i)
                result = put_body(result, body, i)

                if i % 100 == 0:
                    print(i)
                        
                    if i % 2000 == 0:
                        result["ix"] = i
                        with open('result.json', 'w') as f:
                            json.dump(result, f)

        with open('result.json', 'w') as f:
            result["ix"] = i
            json.dump(result, f)
                    

    except KeyboardInterrupt:

        end = time.time()
        print(end - start)
        result["ix"] = i
        print(result["ix"])
        with open('result.json', 'w') as f:
            json.dump(result, f)
            
    return result


def worker(limit):

    result = {}

    start, end = limit

    for i in range(start, end):
        
        file = es.get(index="news", doc_type="document", id=i)
        source = file["_source"]
        title = source.get("title", "")
        body = source.get("body", "")
        
        result[i] = { "body": [], "title": [] , "body_raw": body, "title_raw": title}

        result = put_title(result, title, i)
        result = put_body(result, body, i)

    return result

def parallel(worker, n_pool=4):

    corpus_length = es.count(index="news", doc_type="document")["count"]

    size = corpus_length // n_pool
    limits = []

    for i in range(0,n_pool):

        start = i * size
        end = (i+1) * size
        limits.append((start, end))

    pool = ThreadPool(n_pool)
    results = pool.map(worker, limits)
    pool.close() 
    pool.join()
    
    return results


if __name__ == "__main__":


	file = 'result.json'

	if not os.path.isfile("./" + file): 
		
		result = {}
		result["ix"] = 1
		
		with open(file, 'w') as f:
			json.dump(result, f)


	parser = spacy.load('en')
	es = Elasticsearch([ {'host': host, 'port': 80, 'url_prefix': 'es'} ])

	main(parser, es)
	