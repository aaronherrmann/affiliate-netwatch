import logging
import scrapy
import json
import datetime
from affiliate_netwatch.items import Network,Offer

class AffbankSpider(scrapy.Spider):
    name = 'affbank'
    allowed_domains = ['affbank.com']
    start_urls = ['http://affbank.com/']

    def parse(self, response):
        pass
