#!/home/mars/anaconda3/bin/python3.6

import sys
import lucene
import os
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, IntPoint, TextField, Field, StringField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory

import sqlite3
import pandas as pd
PATH = ''

if __name__ == "__main__":

    PATH = os.getcwd()
    lucene.initVM()
    indexDir = SimpleFSDirectory(Paths.get('index'))
    writerConfig = IndexWriterConfig(StandardAnalyzer())
    writer = IndexWriter(indexDir, writerConfig)

    print("%d docs in index" % writer.numDocs())
    print("Reading lines from sys.stdin...")

    con = sqlite3.connect(PATH + '/imdb.db')
    df = pd.read_sql('select * from movies', con)
    con.close()
    for v in df.values:
        doc = Document()
        doc.add(StringField("id", str(v[0]), Field.Store.YES))
        doc.add(TextField("name", v[1], Field.Store.YES))
        doc.add(StringField("year", str(v[2]), Field.Store.YES))
        writer.addDocument(doc)
    print("Indexed %d lines from stdin (%d docs in index)" % (df.shape[0], writer.numDocs()))
    print("Closing index of %d docs..." % writer.numDocs())
    writer.close()
