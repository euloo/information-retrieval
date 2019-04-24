import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QMessageBox
from PyQt5 import uic, QtWidgets, QtCore, QtGui
import psycopg2
import pandas as pd
import sqlite3
import time
import lucene
import os
import logging
import hashlib
from IR_PandasModel import PandasModel

from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory

Qt = QtCore.Qt
PATH = ''
LIMIT = 10

logging.basicConfig(filename="search.log", level=logging.INFO)


class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()

        self.ask_password()

        self.ui = uic.loadUi(PATH + "/design.ui", self)
        self.statusBar().showMessage('Ready')

        self.ui.radioButton_SQLite.setEnabled(False)

        self.ui.pushButton_search.clicked.connect(self.button_search_clicked)
        self.ui.comboBox.currentTextChanged.connect(self.on_change)

        self._layout = self.layout()
    
    def ask_password(self):
        try:
            text, okPressed = QInputDialog.getText(self, "Authentication","Enter your 'developer' password ;-)", QLineEdit.Password, "")
            if hashlib.md5(text.encode('utf8')).hexdigest() == 'b8b2f3f552b8ee1465ad4c30f466f51b':
                self.db_password=text
            else:
                raise Exception()
        except:
            QMessageBox.question(self, 'Authentication', "YOU SHALL NOT PASS!", QMessageBox.Ok)
            sys.exit()
    
    def button_search_clicked(self):
        t1 = time.time()
        title_substring = self.ui.lineEdit_title.text()
        mode = self.ui.comboBox.currentText()

        # SQLite/PostgreSQL
        if not self.ui.radioButton_Lucene.isChecked():
            if mode == 'Полное совпадение':
                params={'title':title_substring}
                query_string = """select * from movies where name ilike %(title)s"""

            if mode == 'Частичное совпадение':
                params={'title':title_substring}
                query_string = """select * from movies where name ilike '%%'||%(title)s||'%%'"""

            if mode == 'Частичное совпадение по словам':
                params={'title'+str(i):v for i, v in enumerate(title_substring.split())}
                query_string = """select * from movies where """+' or '.join(["""name ilike '%%'||%({})s||'%%'""".format(t) for t in params.keys()])

            if mode == 'Полное совпадение + Год':
                year_substring = self.ui.lineEdit_year.text()
                year_substring = year_substring if year_substring != '' else None
                params={'title':title_substring, 'year':year_substring}
                query_string = """select * from movies where name ilike %(title)s and year = %(year)s"""

            if mode == 'Частичное совпадение + Год':
                year_substring = self.ui.lineEdit_year.text()
                year_substring = year_substring if year_substring != '' else None
                params={'title':title_substring, 'year':year_substring}
                query_string = """select * from movies where name ilike '%%'||%(title)s||'%%' and year = %(year)s"""

            if mode == 'Частичное совпадение по словам + Год':
                year_substring = self.ui.lineEdit_year.text()
                year_substring = year_substring if year_substring != '' else None
                params={'title'+str(i):v for i, v in enumerate(title_substring.split())}
                query_string = ' or '.join(["""name ilike '%%'||%({})s||'%%'""".format(t) for t in params.keys()])
                params.update({'year':year_substring})
                query_string = 'select * from movies where ({}) and year = %(year)s'.format(query_string,year_substring)

            # PostgreSQL connection
            if self.ui.radioButton_PostgreSQL.isChecked():
                con = psycopg2.connect(user='developer', password=self.db_password, host='db.mirvoda.com', port='5454', dbname='information_retrieval')
                se = 'PostgreSQL'

            # SQLite connection
            else:
                con = sqlite3.connect(PATH + '/imdb.db')
                se = 'SQLite'

            df = pd.read_sql(query_string, con, params=params).head(LIMIT)
            con.close()
            df = df.fillna('').astype(str)
            df['year'] = df['year'].apply(lambda x: x.replace('.0', ''))

        # Lucene
        else:
            lucene.initVM()
            index_dir = SimpleFSDirectory(Paths.get('index'))
            reader = DirectoryReader.open(index_dir)
            searcher = IndexSearcher(reader)
            query_string = ''
            se = 'Lucene'
            if mode == 'Полное совпадение':
                query_string = 'name:"{}"'.format(title_substring)

            if mode == 'Частичное совпадение':
                query_string = 'name:{}'.format(title_substring)

            if mode == 'Частичное совпадение по словам':
                query_string = ' or '.join(["""name:{}""".format(ss) for ss in title_substring.split()])

            if mode == 'Полное совпадение + Год':
                year_substring = self.ui.lineEdit_year.text()
                query_string = 'name:"{}" AND year:"{}"'.format(title_substring, year_substring)

            if mode == 'Частичное совпадение + Год':
                year_substring = self.ui.lineEdit_year.text()
                query_string = 'name:{} AND year:"{}"'.format(title_substring, year_substring)

            if mode == 'Частичное совпадение по словам + Год':
                year_substring = self.ui.lineEdit_year.text()
                query_string = ' or '.join(["""name:{}""".format(ss) for ss in title_substring.split()])
                query_string = '({}) and year:"{}"'.format(query_string, year_substring)

            query = QueryParser("defaultField", StandardAnalyzer()).parse(query_string)
            hits = searcher.search(query, LIMIT)

            df = pd.DataFrame()
            for hit in hits.scoreDocs:
                doc = searcher.doc(hit.doc)
                df = df.append([[doc.get('id'), doc.get('name'), doc.get('year')]], ignore_index=True)
            if not df.empty:
                df.columns = ['id', 'name', 'year']

        pandas_model = PandasModel(df)
        self.tableView.setModel(pandas_model)
        self.tableView.horizontalHeader().setSectionResizeMode(1)

        t2 = time.time()
        self.statusBar().showMessage('Searched [{}] with {} for {} s'.format(query_string, se, str(t2 - t1)))

        logging.info('Searched [{}] with {} for {} s'.format(query_string, se, str(t2 - t1)))
        logging.info(df)
        logging.info('---------------------------------------------------------')

    def on_change(self, value):
        if 'Год' in value:
            self.ui.lineEdit_year.setEnabled(True)
        else:
            self.ui.lineEdit_year.setEnabled(False)


if __name__ == '__main__':
    PATH = os.getcwd()
    app = QApplication([])
    application = MyWindow()
    application.show()

    sys.exit(app.exec_())
