import psycopg2
import pandas as pd
import re

df = pd.read_csv('IMDB Movie Titles.csv', encoding='1251')
df['Movie Year'] = df[' Movie Name'].apply(lambda x: ';'.join(re.findall('\((\d{4})\)', x))).replace({'':pd.np.nan}).astype(float)
df[' Movie Name'] = df[' Movie Name'].apply(lambda x: re.sub(' \(.*', '', x).strip())
df['Movie Year'] = df['Movie Year'].fillna(0)

# con = psycopg2.connect(user='developer', password='rtfP@ssw0rd', host='84.201.147.162', dbname='information_retrieval')
# cur = con.cursor()
#
# cur.executemany('insert into movies values(%s, %s, %s)', df.values)
# con.commit()
#
# cur.close()
# con.close()
#cmd + /


#~ local sqlite db
import sqlite3
con = sqlite3.connect('/Users/euloo/imdb.db')
cur = con.cursor()

cur.execute("""create table movies (id integer, name char, year integer)""")

cur.executemany('insert into movies values(:0, :1, :2)', df.values)
con.commit()

cur.close()
con.close()
