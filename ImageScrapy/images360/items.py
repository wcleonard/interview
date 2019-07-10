# -*- coding: utf-8 -*-
import scrapy


class Images360Item(scrapy.Item):
    # define the fields for your item here like:
    collection = table = 'images'
    id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    thumb = scrapy.Field()
