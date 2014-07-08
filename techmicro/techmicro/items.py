# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class techmicroItem(Item):
    url = Field()
    date = Field()
    title = Field()
    keywords = Field()
    tableName = Field()
    pass
