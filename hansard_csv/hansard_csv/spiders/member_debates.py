# -*- coding: utf-8 -*-
import scrapy
from time import sleep
from urllib.parse import urlparse
from urllib.parse import urljoin
from datetime import datetime

from hansard_csv.items import SpokenContribution, Text


def make_text_string(path):
            string = ''
            for text in path.xpath('.//text()').extract():
                string += ' '
                string += text
            return string

class MemberDebatesSpider(scrapy.Spider):
    def __init__(self, contribution_limit=None, spoken_page_limit=None):
        self.contribution_limit = contribution_limit
        self.spoken_page_limit = spoken_page_limit

    name = "member_debates"
    allowed_domains = ["hansard.parliament.uk"]    

    def start_requests(self):
        start_urls = ['https://hansard.parliament.uk/search/MemberContributions?memberId=1541&type=Spoken']

        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_spoken)

    def parse_spoken(self, response):
        next_page = response.xpath('//a[@title="Go to next page"]/@href').extract_first()

        #sleep(1)

        contributions = response.xpath('//a[@class="no-underline"]')

        if self.contribution_limit:
            contributions = contributions[:self.contribution_limit]

        for contribution in contributions:
            contribution_url = contribution.xpath('@href').extract_first()
            print("CONTRIBUTION URL:", contribution_url)

            yield scrapy.Request(response.urljoin(contribution_url), 
                callback=self.parse_contribution,
                meta={'contribution_url': contribution_url},
                dont_filter=True)

        if next_page:
            print("NEXT PAGE", next_page)
            if self.spoken_page_limit:
                if (int(next_page.split('=')[-1])) <= self.spoken_page_limit:
                    yield scrapy.Request(response.urljoin(next_page),
                                        callback=self.parse_spoken)
            else:
                yield scrapy.Request(response.urljoin(next_page),
                                        callback=self.parse_spoken)

    def parse_contribution(self, response):
        contribution_url = response.meta.get('contribution_url')
        member = 'Nia Griffith'
        debate_title = response.xpath('//h1[@class="page-title"]/text()').extract_first()
        debate_date = response.xpath('//div[@class = "col-xs-12 debate-date"]/text()').extract_first()
        debate_date = datetime.strptime(debate_date, '%d %B %Y')
        contribution_id = contribution_url.split('#')[-1]
        contribution_box = response.xpath('//li[@id="{}"]/div[@class="inner"]//div[@class="contribution col-md-9"]'
                                            .format(contribution_id))
        contribution_text = make_text_string(contribution_box)
        contribution_text = contribution_text.strip().split('\r')[0].strip()
        time = response.xpath('//li[@id="{}"]/preceding::div[1]/p/time'
                                            .format(contribution_id))
        contribution_time = time.xpath('@datetime').extract_first()
        if contribution_time:
            contribution_time = datetime.strptime(contribution_time, '%d/%m/%Y %H:%M:%S')

        spoken_contribution = SpokenContribution()
        spoken_contribution['mp'] = member
        spoken_contribution['text'] = contribution_text
        spoken_contribution['time'] = contribution_time
        spoken_contribution['date'] = debate_date
        spoken_contribution['debate'] = debate_title

        #text = Text(spoken_contribution=contribution_text)
        #yield text
        yield spoken_contribution
