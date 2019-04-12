import requests
from bs4 import BeautifulSoup
import psycopg2
import pandas as pd
import re

con = psycopg2.connect(user='developer', password='rtfP@ssw0rd', host='db.mirvoda.com', port='5454', dbname='information_retrieval')
df=pd.read_sql('select * from imdb_movies',con)
con.close()
df['kinopoisk_id']=''
#%%
for i in df.index:
    print(i)
    try:
        res=requests.get('https://www.kinopoisk.ru/index.php?kp_query='+df['title'][i].replace(' ','+'))
        if 'film' in res.url:
            df.at[i,'kinopoisk_id']=re.findall('https://www.kinopoisk.ru/film/(\d*)/',res.url)[0]
        else:
            soup=BeautifulSoup(res.text, 'lxml')
            df.at[i,'kinopoisk_id']=soup.find('a',{'data-id':True})['data-id']
    except:
        pass
#%%
df=df[['id', 'title', 'kinopoisk_id']]
df=df.fillna('')
#%%
import psycopg2
#%%
con = psycopg2.connect(user='developer', password='rtfP@ssw0rd', host='db.mirvoda.com', port='5454', dbname='information_retrieval')
cur = con.cursor()
#%%
n_chunks=16
chunks=[df.values[i::n_chunks] for i in range(n_chunks)]
#%%
for i,chunk in enumerate(chunks):
    print(i)
    cur.executemany('insert into imdb_kinopoisk values(%s, %s, %s)', chunk)
    con.commit()
#%%
cur.close()
con.close()