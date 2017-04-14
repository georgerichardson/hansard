import scrapy

from time import sleep
from urllib.parse import urlparse
from urllib.parse import urljoin
from datetime import datetime

from hansard.items import MP, Debate, SpokenContribution, Party


def get_dates_and_constituency(constituency_date):
    constituency_date = constituency_date.strip()
    l = constituency_date.split('(')
    constituency = l[0][:-1]
    dates = l[1]
    start_date = dates[:4]
    end_date = dates.replace(start_date + ' - ', '')
    end_date = end_date.replace(')', '')
    return constituency, int(start_date), end_date


class MPsSpider(scrapy.Spider):
    name = "mps"
    allowed_domains = ["hansard.parliament.uk"]

    def __init__(self, mp_limit=1, mp_page_limit=1, contribution_limit=12, spoken_page_limit=1):
        '''
        parameters:
        mp_limit - Limit on the number of pages of mps to scrape. Default = 1
        debate_limit - Limit on the number of debate contributions to scrape. Default = 1
        '''
        self.mp_limit = mp_limit
        self.mp_page_limit = mp_page_limit
        self.contribution_limit = contribution_limit
        self.spoken_page_limit = spoken_page_limit

    def start_requests(self):
        urls = [
        "https://hansard.parliament.uk/search/Members?house=commons&currentFormerFilter=1"
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_mps)

    def parse_mps(self, response):

        next_page = response.xpath('//a[@title="Go to next page"]/@href').extract_first()

        sleep(1)

        mps = response.xpath('//a[@class="no-underline"]')
        mps = mps[:self.mp_limit]

        for mp in mps:
            mp_url = mp.xpath('@href').extract_first()

            constituency_date = mp.xpath('.//div[@class="information constituency-date"]/text()').extract_first()
            self.constituency_last, self.start_year, self.end_year = get_dates_and_constituency(constituency_date)
            self.name = mp.xpath('.//span/text()').extract_first()
            self.house = mp.xpath('.//div[@class="information house"]/text()').extract_first()
            self.party = mp.xpath('.//div[@class="information party"]/text()').extract_first()
            
            party = Party(
                    party=self.party
                    )
            yield party

            mp = MP(
                    name = self.name,
                    start_year = self.start_year,
                    end_year = self.end_year,
                    constituency_last = self.constituency_last,
                    house = self.house,
                    party = party
                    )

            self.mp = mp
            yield mp 

            yield scrapy.Request(response.urljoin(mp_url),
                          callback=self.parse_spoken)

        if next_page:
            if int(next_page.split('=')[-1]) <= self.mp_page_limit:
                yield scrapy.Request(response.urljoin(next_page),
                                    callback=self.parse_mps)

    def parse_spoken(self, response):

        next_page = response.xpath('//a[@title="Go to next page"]/@href').extract_first()

        sleep(1)

        contributions = response.xpath('//a[@class="no-underline"]')
        contributions = contributions[:self.contribution_limit]

        for contribution in contributions:
            contribution_url = contribution.xpath('@href').extract_first()
            #self.contribution_url = contribution_url

            yield scrapy.Request(response.urljoin(contribution_url), callback=self.parse_contribution, 
                meta={'contribution_url': contribution_url}, dont_filter=True)

        if next_page:
            if (int(next_page.split('=')[-1])) <= self.spoken_page_limit:
                yield scrapy.Request(response.urljoin(next_page),
                                    callback=self.parse_spoken)

    def parse_contribution(self, response):

        sleep(1)
        contribution_url = response.meta.get('contribution_url')

        def make_text_string(path):
            string = ''
            for text in path.xpath('.//text()').extract():
                string += text
            return string

        #import pdb; pdb.set_trace()
        #debate_id = self.contribution_url.split('/')[-2]
        debate_id = contribution_url.split('/')[-2]
        debate_title = response.xpath('//h1[@class="page-title"]/text()').extract_first()
        debate_date = response.xpath('//div[@class = "col-xs-12 debate-date"]/text()').extract_first()
        debate_date = datetime.strptime(debate_date, '%d %B %Y')
        #contribution_id = self.contribution_url.split('#')[-1]
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

        debate = Debate(
                        debate_id = debate_id,
                        debate_name = debate_title,
                        debate_date = debate_date
                        )

        spoken_contribution = SpokenContribution(
                                        contribution_id = contribution_id,
                                        text = contribution_text,
                                        time = contribution_time,
                                        mp = self.mp,
                                        debate = debate
                                        )
        yield debate
        yield spoken_contribution
