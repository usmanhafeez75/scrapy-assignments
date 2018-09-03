# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
from scrapy.exceptions import DropItem

class ProductPipeline(object):

    def __init__(self):
        self.titles_seen = set()

    def open_spider(self, spider):
        self.file_name = 'products_' + spider.name + '.json'
        self.file = open(self.file_name, 'w+')
        self.file.write('[\n')

    def close_spider(self, spider):
        self.file.write(']')
        self.file.close()

    def process_item(self, item, spider):
        if 'title' not in item.fields:
            raise DropItem('Invalid Item! title field not found')
        if item['title'] in self.titles_seen:
            raise DropItem('Duplicate Item found')
        else:
            self.titles_seen.add(item['title'])
        line = json.dumps(dict(item)) + ',\n'
        self.file.write(line)
        return item
