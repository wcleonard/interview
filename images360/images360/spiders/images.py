# -*- coding: utf-8 -*-
import json
from urllib.parse import urlencode
from scrapy import Spider, Request
import scrapy
from ..items import Images360Item


class ImagesSpider(scrapy.Spider):
    name = 'images'
    allowed_domains = ['images.so.com']
    start_urls = ['http://images.so.com/']

    def parse(self, response):
        result = json.loads(response.text)
        for image in result.get(list):
            item = Images360Item()
            item['id'] = image.get('imageid')
            item['url'] = image.get('qhimg_url')
            item['title'] = image.get('group_title')
            item['thumb'] = image.get('qhimg_thumb_url')
            yield item

    def start_requests(self):
        data = {'ch': 'photography', 'listtype':'new'}
        base_url = 'https://image.so.com/zj?'
        for page in range(1, self.settings.get('MAX_PAGE')+1):
            data['sn'] = page * 30
            params = urlencode(data)
            url = base_url + params
            yield Request(url, self.parse)