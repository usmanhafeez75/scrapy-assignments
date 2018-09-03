# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Identity, Compose

class Product(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    category_list = scrapy.Field()
    rating = scrapy.Field()
    ratings_count = scrapy.Field()
    features = scrapy.Field()


def remove_hard_spaces(line):
    return line.replace('\u00A0', '')

def output_price(self, price):
    return ''.join(price)

def output_category_list(self, category_list):
    return category_list[1:-1]

def process_rating(self, rating):
    if rating:
        return '{:.1f}'.format(float(rating[0]) / 20)
    else:
        return '-1'

def process_ratings_count(self, ratings_count):
    if ratings_count:
        return ratings_count[0].strip('()')
    else:
        return '0'


class ProductLoader(ItemLoader):
    default_item_class = Product
    default_input_processor = Identity()
    default_output_processor = TakeFirst()

    title_in = MapCompose(remove_hard_spaces)
    title_out = TakeFirst()
    price_in = MapCompose(remove_hard_spaces)
    price_out = output_price
    category_list_in  = MapCompose(remove_hard_spaces)
    category_list_out = output_category_list
    rating_in = process_rating
    ratings_count_in = process_ratings_count
    features_in = MapCompose(remove_hard_spaces)
    features_out = Identity()