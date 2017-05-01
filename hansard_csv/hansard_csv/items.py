# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import six
from scrapy import Item, Field
from collections import OrderedDict

class OrderedItem(Item):
    def __init__(self, *args, **kwargs):
        self._values = OrderedDict()
        if args or kwargs:  # avoid creating dict for most common case
            for k, v in six.iteritems(dict(*args, **kwargs)):
                self[k] = v

class SpokenContribution(OrderedItem):
    mp = Field()
    text = Field()
    time = Field()
    date = Field()
    debate = Field()

class Text(Item):
    spoken_contribution = Field()
