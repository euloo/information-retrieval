import json
import pandas as pd
import re

def lil2l(lst):
    lres=[]
    for l in lst:
        if isinstance(l,list):
            lres.extend(lil2l(l))
        else:
            lres.append(l)
    return lres
#%%
with open(r'd:\imdb_spider\imdb_full.json','r') as file:
    data=json.loads(file.read())
    file.close()

#%%
rows=[]
row={}
for d in data:
    if 'id' in d:
        rows.append(row)
        row={}
        items=list(d.items())[0]
        row[items[0]]=items[1]
    else:
        items=list(d.items())[0]
        row[items[0]]=items[1]
rows.append(row)
#%%
df=pd.DataFrame(rows[1:])
#%%
for c in ['id','storyline', 'synopsys']:
    df[c]=df[c].fillna('').apply(lambda x: ';'.join([s for s in lil2l(x) if not 'more credit' in s]))

for c in ['director', 'genres', 'keywords', 'ratingXPath','top_3_cast']:
    df[c]=df[c].fillna('').apply(lambda x: [s for s in lil2l(x) if not 'more credit' in s])

df['releasedates']=df['releasedates'].fillna('').apply(lambda x: [re.sub('\s*','','{} ({})'.format(s[1],s[0])) for s in x])
df['year']=df['year'].astype(float).fillna(0)
df['rating']=df['rating'].astype(float).fillna(0)

df=df.replace({'':None})
#%%
#df.to_excel('imdb_full.xlsx', index=None)
#df.to_csv('imdb_full.csv', sep='|', quoting=1, index=None)
#%%
df=df[['id', 'year','title','releasedates','genres', 'director', 'top_3_cast', 'rating', 'storyline', 'synopsys']]
#%%
import psycopg2
#%%
con = psycopg2.connect(user='', password='', host='', port='', dbname='information_retrieval')
cur = con.cursor()
#%%
n_chunks=16
chunks=[df.values[i::n_chunks] for i in range(n_chunks)]
#%%
for i,chunk in enumerate(chunks):
    print(i)
#%%
    cur.executemany('insert into imdb_movies values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', chunk)
    con.commit()
#%%
cur.execute('update imdb_movies set year = null where year=0')
con.commit()
cur.execute('update imdb_movies set raiting = null where raiting=0')
con.commit()
#%%
cur.close()
con.close()
