import scrapy
import re
import itertools

class ImdbSpider(scrapy.Spider):
    name = 'imdbspider'
    
    start_urls=['https://www.imdb.com/title/tt4154756']
    
    def parse(self, response):
        yield {'id': re.findall('https://www.imdb.com/title/tt(\d*)/',response.url)}
        
        for title in response.css('.title_wrapper>h1'):
            yield {'title': title.css('h1 ::text').get().replace(u'\xa0', u'')}
            yield {'year': title.css('a ::text').get()}

        for rating in response.css('.ratingValue>strong>span'):
            yield {'rating': rating.css('span ::text').get()}
            yield {'ratingXPath': rating.xpath('string(.)').extract()}

        directors=[]
        for creds in response.css('a[href*="tt_ov_dr"]'):
            directors.append(creds.xpath('text()').extract())
        yield {'director': directors}

        genres=[]
        for genre in response.css('div.subtext>a[href*="genres"]'):
            genres.append(genre.xpath('text()').extract())
        yield {'genres': genres}

        for rating in response.css('#titleStoryLine > div:nth-child(3) > p > span'):
            yield {'storyline': rating.xpath('text()').extract()}
              
        top_3_cast=[]
        for i, cast in enumerate(response.css('#titleCast>table').css('a[href*="name"][href*="/?ref_=tt_cl_t"]')):
            top_3_cast.append(cast.xpath('text()').extract())
            if i == 2:
                break
        yield {'top_3_cast': top_3_cast}
        
        for plot_page in response.css('a[href*="/synopsis?ref_=tt_stry_pl"]'):
            yield response.follow(plot_page, self.parseSyno)
        
        for keywords_page in response.css('a[href*="/keywords?ref_=tt_stry_kw"]'):
            yield response.follow(keywords_page, self.parseKeywords)
            
        for rd_page in response.css('a[href*="releaseinfo?ref_=tt_dt_dt"]'):
            yield response.follow(rd_page, self.parseReleaseDate)
        
    def parseSyno(self, response):
        for syno in response.css('#plot-synopsis-content>li'):
            yield {'synopsys': syno.xpath('text()').extract()}
            
    def parseKeywords(self, response):
        kwds=[]
        for keyword in response.css('div.sodatext>a'):
            kwds.append(keyword.xpath('text()').extract())
        yield {'keywords':kwds}
    
    def parseReleaseDate(self, response):
        rd=[]
        for tr in response.css('tr.ipl-zebra-list__item.release-date-item'):
            a=tr.css('a').xpath('text()').extract()
            tds=[td.xpath('text()').extract() for td in tr.css('td')]
            rd.append([a[0], ' '.join(itertools.chain.from_iterable(tds))])
        yield {'releasedates':rd}

from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.signalmanager import dispatcher

def crawler_results(signal, sender, item, response, spider):
    results.append(item)

if __name__ == '__main__':
    results = []

    dispatcher.connect(crawler_results, signal=signals.item_passed)

    process = CrawlerProcess(get_project_settings())
    process.crawl(ImdbSpider)
    process.start()
