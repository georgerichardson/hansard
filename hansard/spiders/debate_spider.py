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
    name = "debate_spider"
    allowed_domains = ["hansard.parliament.uk"]

    def __init__(self, page_limit=1, debate_limit=None):
        '''
        parameters:
        member_limit - Limit on the number of pages of mps to scrape. Default = 1
        debate_limit - Limit on the number of debate contributions to scrape. Default = 1
        '''
        self.page_limit = page_limit
        self.debate_limit = debate_limit

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

    def parse_debates(self, response):

        next_page = response.xpath('//a[@title="Go to next page"]/@href').extract_first()

        debates = response.xpath('//a[@class="no-underline"]/@href').extract()

        debates = debates[:self.debate_limit]

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

    def parse_spoken(self, response):

        url = response.url

        debate_id = url.split('/')[-2]
        debate_title = response.xpath('//h1[@class="page-title"]/text()').extract_first()
        debate_date = response.xpath('//div[@class = "col-xs-12 debate-date"]/text()').extract_first()
        debate_date = datetime.strptime(debate_date, '%d %B %Y')
        sitting = response.xpath('//ol[@class="breadcrumb hidden-xs"]//text()').extract()
        sitting = [s.strip() for s in sitting if len(s.strip()) > 0][1:-1]
        sitting = ' - '.join(sitting)
        chair = response.xpath('//p["@class=hs_76fChair"][.//em[text()="in the "]]/text()').extract_first()
        if chair:
            chair = chair[1:-1]
        if not chair:
            chair = 'No Chair'

        debate = Debate(
            debate_id = debate_id,
            debate_name=debate_title,
            debate_date=debate_date,
            sitting=sitting
            )
        
        yield debate

        contributions = response.xpath('//li[starts-with(@id,"contribution")]')

        for contribution in contributions:
            contribution_id = contribution.xpath('@id').extract_first()
            member_id = contribution.xpath('.//h2[@class="memberLink"]/a[@class="nohighlight"]/@href').extract_first()
            if member_id:
                member_id = int(member_id.split("=")[-1])
            else:
                member_id = 0
            text = make_text_string(contribution.xpath('.//p'))

            spoken_contribution = SpokenContribution(
                contribution_id = contribution_id,
                text = text,
                member_id = member_id,
                debate_identifier = debate_id
                )

            yield spoken_contribution


