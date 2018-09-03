from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from DarazPK.items import ProductLoader


class DarazSpider(CrawlSpider):
    name = 'daraz'
    allowed_domains = ['daraz.pk']
    start_urls = ['https://www.daraz.pk/']

    rules = (
        Rule(LinkExtractor(allow=('https://www.daraz.pk/.*',), deny=('[.]html$', '/ur/'), allow_domains=('daraz.pk'),
                           restrict_css=('ul.menu-items', 'div.page-sub-category col-sm-2 hidden-sm hidden-xs',
                                         'section.products'),
                           restrict_xpaths=('ul[@class="osh-pagination -horizontal"]'))),
        Rule(LinkExtractor(allow=('[.]html$'), deny=('/ur/'), allow_domains=('daraz.pk')),
             callback='parse_item'),
    )

    def __init__(self, start_urls=None, allowed_domains=None, *args, **kwargs):
        super(DarazSpider, self).__init__(*args, **kwargs)
        if start_urls:
            self.start_urls = start_urls.split(',')
        if allowed_domains:
            self.allowed_domains = allowed_domains.split(',')

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
