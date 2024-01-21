# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field
from dataclasses import dataclass

class Network(Item):
    """This class represents an affiliate network"""
    id = Field()
    name = Field()
    description = Field()
    url = Field()
    min_payout = Field()
    commission_type = Field()
    payment_frequency = Field()
    payment_method = Field()
    email = Field()
    phone = Field()
    rating = Field()
    tracker = Field()

class Manager(Item):
    """This class represents an individual who manages an affiliate network"""
    name = Field()
    email = Field()
    phone = Field()
    skype = Field()
    telegram = Field()

class Offer(Item):
    """This class represents an affiliate offer"""
    id = Field()
    name = Field()
    description = Field()
    offer_url = Field()
    network = Field()
    payout = Field()
    categories = Field()
    type = Field()
    countries = Field()
    landing_page_url = Field()
    file_urls = Field()
    files = Field()
    last_updated = Field()
    created_at = Field()