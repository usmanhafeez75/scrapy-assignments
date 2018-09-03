import scrapy
from DarazPK.items import ProductLoader

class DarazQuerySpider(scrapy.Spider):
    name = 'darazquery'
    allowed_domains = ['daraz.pk']

    url = 'https://www.daraz.pk/catalog/?q='
    query = 'laptops'

    def __init__(self, query=None, *args, **kwargs):
        super(DarazQuerySpider, self).__init__(*args, **kwargs)
        if query:
            self.query = query

    def start_requests(self):
        return [scrapy.Request(url=self.url+self.query, callback=self.parse)]

    def parse(self, response):
        for url in response.css('section.products').xpath('.//div[@class="sku -gallery"]/a/@href').extract():
            yield scrapy.Request(url=url, callback=self.parse_item)
        next_url = response.xpath('.//a[@title="Next"]/@href').extract_first()
        if next_url is not None:
            yield scrapy.Request(url=next_url, callback=self.parse)

    def parse_item(self, response):
        container_class = 'osh-container'
        category_class = 'osh-breadcrumb'
        details_classes = ['sku-detail', 'details-wrapper', 'details -validate-size']
        title_class = 'title'
        rating_super_class = 'rating-stars'
        rating_classes = ['stars-container', 'stars']
        ratings_count_class = 'total-ratings'
        feature_classes = ['detail-features', 'list -features -compact -no-float']
        price_classes = ['details-footer', 'price-box', 'price']

        loader = ProductLoader(response=response)
        container = loader.nested_css('main.{}'.format(container_class))
        details = container.nested_css('section.{} div.{}'.format(*details_classes[:-1])). \
            nested_xpath('.//div[@class="{}"]'.format(details_classes[-1]))

        details.add_xpath('title', './/span/h1[@class="{}"]/text()'.format(title_class))
        details.nested_css('div.{} div.{} div span.{}'.format(*price_classes)).add_xpath(
            'price', './span/text()')
        container.nested_css('nav.{}'.format(category_class)).add_xpath('category_list', './/ul/li/a/text()')
        details.add_css('rating', 'div.{} div.{} div.{}::attr(style)'.format(rating_super_class, *rating_classes),
                        re='width: (\d+[.]?\d+)%')
        details.add_css('ratings_count', 'div.{} div.{}::text'.format(rating_super_class, ratings_count_class))
        details.nested_css('div.{}'.format(feature_classes[0])).add_xpath('features',
            './/div[@class="{}"]/ul/li//text()'.format(feature_classes[1]))
        return  loader.load_item()