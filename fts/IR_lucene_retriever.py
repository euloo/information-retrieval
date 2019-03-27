import sys
import lucene

from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory

import pandas as pd

if __name__ == "__main__":
    lucene.initVM()
    indexDir = SimpleFSDirectory(Paths.get('index'))
    reader = DirectoryReader.open(indexDir)
    searcher = IndexSearcher(reader)

    query = QueryParser("name", StandardAnalyzer()).parse("Dead")
    MAX = 10
    hits = searcher.search(query, MAX)

    print("Found %d document(s) that matched query '%s':" % (hits.totalHits, query))
    df = pd.DataFrame()
    for hit in hits.scoreDocs:
        print(hit.score, hit.doc, hit.toString())
        doc = searcher.doc(hit.doc)
        df = df.append([[doc.get('id'), doc.get('name'), doc.get('year')]], ignore_index=True)
    df.columns = ['id', 'name', 'year']
    print(df)
