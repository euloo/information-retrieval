import scrapy
import re
  
class ImdbSpider(scrapy.Spider):
    name = 'imdbspider'
    
    def __init__(self, filename=None):
        if filename:
            with open(filename, 'r') as file:
                self.start_urls=file.read().split('\n')
                file.close()
    
    def parse(self, response):
        yield {'id': re.findall('https://www.imdb.com/title/tt(\d*)/',response.url)[0]}
        
        for title in response.css('.title_wrapper>h1'):
            yield {'title': title.css('h1 ::text').get().replace(u'\xa0', u'')}
            yield {'year': title.css('a ::text').get()}

        for rating in response.css('.ratingValue>strong>span'):
            yield {'rating': rating.css('span ::text').get()}

        directors=[]
        for creds in response.css('a[href*="tt_ov_dr"]'):
            directors.append(creds.xpath('text()').get())
        yield {'director': directors}

        genres=[]
        for genre in response.css('div.subtext>a[href*="genres"]'):
            genres.append(genre.xpath('text()').get())
        yield {'genres': genres}

        for rating in response.css('#titleStoryLine > div:nth-child(3) > p > span'):
            yield {'storyline': rating.xpath('text()').get()}
              
        top_3_cast=[]
        for i, cast in enumerate(response.css('#titleCast>table').css('a[href*="name"][href*="/?ref_=tt_cl_t"]')):
            top_3_cast.append(cast.xpath('text()').get())
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
            yield {'synopsys': syno.xpath('text()').get()}
            
    def parseKeywords(self, response):
        kwds=[]
        for keyword in response.css('div.sodatext>a'):
            kwds.append(keyword.xpath('text()').get())
        yield {'keywords':kwds}
    
    def parseReleaseDate(self, response):
        rd=[]
        for tr in response.css('tr.ipl-zebra-list__item.release-date-item'):
            a=tr.css('a').xpath('text()').get()
            tds=[td.xpath('text()').get() for td in tr.css('td') if td.xpath('text()').get()]
            rd.append([a, ' '.join(tds)])
        yield {'releasedates':rd}
