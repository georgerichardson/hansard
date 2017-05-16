# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class Member(Item):
    name = Field()
    start_year = Field()
    end_year = Field()
    constituency_last = Field()
    member_identifier = Field()
    house = Field()
    party = Field()
    member_url = Field()

class Debate(Item):
    debate_identifier = Field()
    debate_url = Field()
    debate_name = Field()
    debate_date = Field()
    sitting = Field()
    #mps = Field()
    #spoken_contributions = Field()

class SpokenContribution(Item):
    contribution_identifier = Field()
    text = Field()
    #time = Field()
    member_identifier = Field()
    debate_identifier = Field()
    debate = Field()
    member = Field()

class Party(Item):
    party = Field()

