import scrapy
import re

class KinopoiskSpider(scrapy.Spider):
    name = 'kinopoiskspider'
    
    def __init__(self, filename=None):
        if filename:
            with open(filename, 'r') as file:
                self.start_urls=file.read().split('\n')
                file.close()
    
    def parse(self, response):
        yield {'id': re.findall('https://www.kinopoisk.ru/film/(\d*)/',response.url)}
        
        info={}
        for tr in response.css('#infoTable>table').css('tr'):
            tds=tr.css('td')
            info[' '.join(tds[0].xpath('text()').get()).strip()]=' '.join(tds[1].xpath('.//text()').get()).strip()
        
        yield {'year': info.get('год', '')}
        yield {'release_date': info.get('премьера (мир)', '')}
        yield {'genres': info.get('жанр', '')}
        yield {'director': info.get('режиссер', '')}
        
        yield {'title':response.css('#headerFilm > h1').xpath('text()').get()}
        yield {'en_title':response.css('#headerFilm > span').xpath('text()').get()}
        
        top_3_cast=[]
        for i, li in enumerate(response.css('li[itemprop="actors"]>a[href*="name"]')):
            top_3_cast.append(li.xpath('text()').get())
            if i == 2:
                break
        yield {'top_3_cast':top_3_cast}

        yield {'storyline':response.css('div[itemprop="description"]').xpath('text()').get()}
        
        for kws in response.css('a.wordLinks[href*="keywords"]'):
            yield response.follow(kws, self.parseKeywords)
        
    def parseKeywords(self, response):
        keywords=[]
        for kwds in response.css('a[href*="lists/m_act%5Bkeyword%5D"]'):
            keywords.append(kwds.xpath('text()').get())
        yield {'keywords': keywords}