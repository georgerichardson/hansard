import scrapy

from time import sleep
from urllib.parse import urlparse
from urllib.parse import urljoin
from datetime import datetime

from hansard.items import Debate, SpokenContribution

def make_text_string(path):
            string = ''
            for text in path.xpath('.//text()').extract():
                string += ' '
                string += text
            return string

class DebateSpider(scrapy.Spider):
    name = "hansard_members"
    allowed_domains = ["hansard.parliament.uk"]

    def __init__(self, page_limit=1):
        '''
        parameters:
        member_limit - Limit on the number of pages of mps to scrape. Default = 1
        debate_limit - Limit on the number of debate contributions to scrape. Default = 1
        '''
        self.page_limit = page_limit

    def start_requests(self, commons=True, lords=True):

        if commons and not lords:
            house = '?house=Commons'
        if lords and not commons:
            house = '?house=Lords'
        if commons and lords:
            house = ''
        if not commons and not lords:
            print("You haven't selected any houses! Defaulting to both.")

        url = 'https://hansard.parliament.uk/search/Debates' + house

        yield scrapy.Request(url=url, callback=self.parse_debates)

    def parse_debates(self):

        next_page = response.xpath('//a[@title="Go to next page"]/@href').extract_first()

        debates = response.xpath('//a[@class="no-underline"]/@href').extract()

        for debate in debates:
            yield scrapy.Request(response.urljoin(debate), callback=self.parse_spoken)

        if next_page:
            if self.page_limit:
                if (int(next_page.split('=')[-1])) <= self.page_limit:
                    yield scrapy.Request(response.urljoin(next_page),
                                        callback=self.parse_debates)
            else:
                yield scrapy.Request(response.urljoin(next_page),
                                        callback=self.parse_debates)



    def parse_spoken(self):

        url = response.url

        debate_id = url.split('/')[-2]
        debate_title = response.xpath('//h1[@class="page-title"]/text()').extract_first()
        debate_date = response.xpath('//div[@class = "col-xs-12 debate-date"]/text()').extract_first()
        debate_date = datetime.strptime(debate_date, '%d %B %Y')
        sitting = response.xpath('//ol[@class="breadcrumb hidden-xs"]//text()').extract()
        sitting = [s.strip() for s in sitting if len(s.strip()) > 0][1:-1]
        sitting = ' - '.join(sitting)
        chair = response.xpath('//p["@class=hs_76fChair"][.//em[text()="in the "]]/text()').extract_first()[1:-1]
        if not chair:
            chair = 'No Chair'

        contributions = response.xpath('//li[starts-with(@id,"contribution")]')

        #for contribution in contributions:
            #contribution_id

        #for contributors in contributors:
            #get names of contributors and their info

