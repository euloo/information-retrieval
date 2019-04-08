import requests
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd
import re
import multiprocessing as mp
import time
import fake_useragent
import random

#%%
def proxy_request(proxy_gen, ua, **kwargs):
    try:
        proxy_head=kwargs['headers']
        proxy_head.update({'user-agent':ua.random})
        kwargs.update({'headers':proxy_head})
    except:
        pass
    try:
        proxied_res=requests.get(**kwargs, timeout=5)
        if proxied_res.status_code!=200:
            raise Exception(proxied_res.status_code)
    except:
        next_proxy=next(proxy_gen)
        kwargs.update({'proxies':{'http':next_proxy,'https':next_proxy}})
        return proxy_request(proxy_gen, ua, **kwargs)
    else:
        return proxied_res

def get_imdb(chnks, data, prx):
    head={
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'referer': 'https://www.imdb.com/',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
   
    ua=fake_useragent.UserAgent()
    
    prx_gen=iter(prx)
    next_prx=next(prx_gen)
        
    for chnk in chnks:
        time.sleep(5)
        row={'id':chnk[0],'name':chnk[1],'year':chnk[2]}
        try:             
            url='https://www.imdb.com/title/tt{}'.format(chnk[0].zfill(7))
            
            res=proxy_request(prx_gen, ua, url=url, headers=head, proxies={'http':next_prx,'https':next_prx})
            soup=BeautifulSoup(res.text, 'lxml')
            
            h1=soup.find('h1')
            row['h1Title']='' if h1 is None else str(h1.contents[0])
            
            originalTitle=soup.find('div',{'class':'originalTitle'})
            row['originalTitle']='' if originalTitle is None else str(originalTitle.contents[0])
            
            synopsis=soup.find('div',{'class':'inline canwrap'})
            synopsis='' if synopsis.find('span') is None else synopsis.find('span').text
            row['synopsis']=re.sub('\s+',' ',synopsis).strip()
            
            for txtblck in soup.find_all('div',{'class':['txt-block','see-more inline canwrap']}):
                h4=txtblck.find('h4')
                if h4:
                    value=txtblck.get_text('\n').replace(h4.text,'')
                    value=re.sub('\s+',' ',value).strip()
                    header=re.sub('\s+',' ',h4.text).strip()
                    header=re.sub('[:]+',' ',header).strip()
                    row[header]= value
            
            url='https://www.imdb.com/title/tt{}/keywords'.format(chnk[0].zfill(7))
            
            res=proxy_request(prx_gen, ua, url=url, headers=head, proxies={'http':next_prx,'https':next_prx})
            soup=BeautifulSoup(res.text, 'lxml')
            
            keywords_content=soup.find('div',{'id':'keywords_content'})
            keywords_content=keywords_content.find_all('div',{'class':'sodatext'}) if keywords_content else ['']
            
            keywords=';'.join([re.sub('\s+',' ',kw.text).strip() for kw in keywords_content])
            
            row['keywords']=keywords
            
        except StopIteration:
            row['error']='proxy list is empty'
            break
        except KeyboardInterrupt as ki:
            raise ki
        except Exception as e:
            row['error']=str(e)
        data.append(row)

#%%     
if __name__ == '__main__':
    con=sqlite3.connect('movies.db')
    movies=pd.read_sql('select * from movies',con).astype(str).sample(1000)
    con.close()
    
    with open('D:\\proxieslist.txt', 'r') as prx:
        proxies_list=prx.read().split('\n')
        prx.close()
       
    mgr=mp.Manager()
    shared_list=mgr.list()
    
    n_chunks=50
    chunks=[movies.values[i::n_chunks] for i in range(n_chunks)]
    
    random.shuffle(proxies_list)
    proxies=[proxies_list[i::n_chunks] for i in range(n_chunks)]
    
    prcs=[]
    for chunk,proxy in zip(chunks, proxies):
        p=mp.Process(target=get_imdb, args=(chunk,shared_list, proxy))
        prcs.append(p)
        p.start()
    
    for p in prcs:
        p.join()
    
    df=pd.DataFrame(list(shared_list)).fillna('')
    df=df.applymap(lambda x: x.replace(' See more »',''))