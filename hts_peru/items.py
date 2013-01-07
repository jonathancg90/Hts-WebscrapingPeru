# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field


class Hts(Item):
    code = Field()
    hs = Field()
    name = Field()
    country = Field()
    quantity = Field()
    tariff = Field()
    tariff_all = Field()
    count = Field()


class Hs(Item):
    code = Field()
    name = Field()


