import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import uic, QtWidgets, QtCore, QtGui
import psycopg2
import pandas as pd
import sqlite3

import lucene
import os
import resources

from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory

Qt = QtCore.Qt
PATH = ''
LIMIT = 10



class PandasModel(QtGui.QStandardItemModel):
    def __init__(self, data, parent=None):
        QtGui.QStandardItemModel.__init__(self, parent)
        self._data = data

        for row in data.values.tolist():
            data_row = [QtGui.QStandardItem(x) for x in row]
            self.appendRow(data_row)
        return

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def headerData(self, x, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[x]
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return self._data.index[x]
        return None


class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()


        self.ui = uic.loadUi(PATH + "/design.ui", self)

        self.ui.pushButton.clicked.connect(self.btnClicked)
        self.ui.comboBox.currentTextChanged.connect(self.onChange)

        self._layout = self.layout()
        self.movie = QtGui.QMovie(':/images/spinner.gif', QtCore.QByteArray(), self)
        self.movie_screen = QtWidgets.QLabel()
        self.movie_screen.setAlignment(Qt.AlignCenter)
        self.ui.verticalLayout.addWidget(self.movie_screen)
        self.setLayout(self.ui.verticalLayout)
        self.movie_screen.setMovie(self.movie)
        self.movie.start()
        self.movie.loopCount()

    def btnClicked(self):

        substring = self.ui.lineEdit.text()
        mode = self.ui.comboBox.currentText()
        if not self.ui.radioButton_3.isChecked():
            if mode == 'Полное совпадение':
                query_string = """name ilike '{}'""".format(substring)
            if mode == 'Частичное совпадение':
                query_string = """name ilike '%{}%'""".format(substring)
            if mode == 'Полное совпадение + Год':
                year_substring = self.ui.lineEdit_2.text()
                year_substring = '= ' + year_substring if year_substring != '' else ' is null'
                query_string = """name ilike '{}' and year {}""".format(substring, year_substring)
            if mode == 'Частичное совпадение + Год':
                year_substring = self.ui.lineEdit_2.text()
                year_substring = '= ' + year_substring if year_substring != '' else ' is null'
                query_string = """name ilike '%{}%' and year {}""".format(substring, year_substring)

            if self.ui.radioButton.isChecked():
                con = psycopg2.connect(user='developer', password='rtfP@ssw0rd', host='84.201.147.162',
                                       dbname='information_retrieval')
            else:
                con = sqlite3.connect(PATH + '/imdb.db')
            df = pd.read_sql('select * from movies where ' + query_string, con).head(LIMIT)
            con.close()
            df = df.fillna('').astype(str)
            df['year'] = df['year'].apply(lambda x: x.replace('.0', ''))
        else:
            lucene.initVM()
            indexDir = SimpleFSDirectory(Paths.get('index'))
            reader = DirectoryReader.open(indexDir)
            searcher = IndexSearcher(reader)

            if mode == 'Полное совпадение':
                query_string = 'name:"{}"'.format(substring)
            if mode == 'Частичное совпадение':
                query_string = 'name:{}'.format(substring)
            if mode == 'Полное совпадение + Год':
                year_substring = self.ui.lineEdit_2.text()
                query_string = 'name:"{}" AND year:"{}"'.format(substring, year_substring)
            if mode == 'Частичное совпадение + Год':
                year_substring = self.ui.lineEdit_2.text()
                query_string = 'name:{} AND year:"{}"'.format(substring, year_substring)

            query = QueryParser("defaultField", StandardAnalyzer()).parse(query_string)
            hits = searcher.search(query, LIMIT)

            df = pd.DataFrame()
            for hit in hits.scoreDocs:
                doc = searcher.doc(hit.doc)
                df = df.append([[doc.get('id'), doc.get('name'), doc.get('year')]], ignore_index=True)
            if not df.empty:
                df.columns = ['id', 'name', 'year']

        model = PandasModel(df)
        self.tableView.setModel(model)

    def onChange(self, value):
        if 'Год' in value:
            self.ui.lineEdit_2.setEnabled(True)
        else:
            self.ui.lineEdit_2.setEnabled(False)


if __name__ == '__main__':
    PATH = os.getcwd()
    app = QApplication([])
    application = mywindow()
    application.show()

    sys.exit(app.exec_())
