import scrapy

from time import sleep
from urllib.parse import urlparse
from urllib.parse import urljoin
from datetime import datetime

from hansard.items import Member, Party

def get_dates_and_constituency(constituency_date):
    constituency_date = constituency_date.strip()
    c = constituency_date.split('(')
    constituency = c[0][:-1]
    dates = constituency_date.split(' ')
    start_date = dates[-3].strip('(')
    end_date = dates[-1].strip(')')
    #end_date = dates.replace(start_date + ' - ', '')
    #end_date = end_date.replace(')', '')
    return constituency, int(start_date), end_date

class MemberSpider(scrapy.Spider):
    name = "hansard_members"
    allowed_domains = ["hansard.parliament.uk"]

    def __init__(self, member_limit=None, member_page_limit=201):
        '''
        parameters:
        member_limit - Limit on the number of pages of mps to scrape. Default = 1
        debate_limit - Limit on the number of debate contributions to scrape. Default = 1
        '''
        self.member_limit = member_limit
        self.member_page_limit = member_page_limit

    def start_requests(self, commons=True, lords=True, current_members=True, former_members=True):

        if commons and lords:
            house = ''
        if commons and not lords:
            house = '&house=Commons'
        if lords and not commons:
            house = '&house=Lords'
        if current_members and former_members:
            members = 'Members?currentFormerFilter=0'
        if current_members and not former_members:
            members = 'Members?currentFormerFilter=1'
        if former_members and not current_members:
            members = 'Members?currentFormerFilter=2'
        if not commons and not lords:
            print("You're not selecting any members!")
        if not current_members and not former_members:
            print("You're not selecting any members!")

        url = 'https://hansard.parliament.uk/search/' + members + house

        yield scrapy.Request(url=url, callback=self.parse_members)

    def parse_members(self, response):

        next_page = response.xpath('//a[@title="Go to next page"]/@href').extract_first()

        members = response.xpath('//a[@class="no-underline"]')

        if self.member_limit:
            members = members[:self.member_limit]

        for member in members:
            member_url = member.xpath('@href').extract_first()

            constituency_date = member.xpath('.//div[@class="information constituency-date"]/text()').extract_first()
            self.constituency_last, self.start_year, self.end_year = get_dates_and_constituency(constituency_date)
            self.name = member.xpath('.//span/text()').extract_first()
            self.house = member.xpath('.//div[@class="information house"]/text()').extract_first()
            self.party = member.xpath('.//div[@class="information party"]/text()').extract_first()
            
            party = Party(
                    party=self.party
                    )
            yield party

            member = Member(
                    name = self.name,
                    start_year = self.start_year,
                    end_year = self.end_year,
                    constituency_last = self.constituency_last,
                    member_identifier = int(member_url.split('=')[-2][:-5]),
                    house = self.house,
                    party = party,
                    member_url = member_url
                    )

            yield member

        if next_page:
            print("PAGE", int(next_page.split('=')[-1]))
            if self.member_page_limit:
                if int(next_page.split('=')[-1]) <= self.member_page_limit:
                    yield scrapy.Request(response.urljoin(next_page),
                                        callback=self.parse_members)
            else:
                yield scrapy.Request(response.urljoin(next_page),
                                        callback=self.parse_members)

