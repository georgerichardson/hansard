# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class MP(Item):
    name = Field()
    start_year = Field()
    end_year = Field()
    constituency_last = Field()
    house = Field()
    party = Field()

class Debate(Item):
    debate_id = Field()
    debate_name = Field()
    debate_date = Field()
    #mps = Field()
    #spoken_contributions = Field()

class SpokenContribution(Item):
    contribution_id = Field()
    text = Field()
    time = Field()
    mp = Field()
    debate = Field()

class Party(Item):
    party = Field()

