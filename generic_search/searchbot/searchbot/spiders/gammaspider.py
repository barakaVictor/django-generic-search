from urllib.parse import urlparse
from bs4 import BeautifulSoup
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from django.conf import settings
from ..items import HtmlPage

class GammaSpider(CrawlSpider):
    name = 'gammaspider'
    allowed_domains = settings.SPYDER_CONFIG[name]['allowed_domains']
    start_urls = settings.SPYDER_CONFIG[name]['start_urls']

    rules = (
        Rule(LinkExtractor(unique=True), callback='parse_item', follow=True),
    )

    def parse_item(self, response, **kwargs):
        page = HtmlPage()
        page['title'] = ' '.join(response.xpath('//title/text()').get().replace("\n", " ").split()) if response.xpath('//title/text()').get() else None
        page['description'] = ' '.join(response.xpath('//meta[@name="description"]/@content').get().replace("\n", " ").split()) if response.xpath('//meta[@name="description"]/@content').get() else None
        page['keywords'] = ' '.join(response.xpath('//meta[@name="keywords"]/@content').get().replace("\n", " ").split()) if response.xpath('//meta[@name="keywords"]/@content').get() else None
        page['url'] = response.url
        page['links'] = [response.urljoin(x) for x in response.xpath('//a/@href').extract() if not bool(urlparse(x).netloc)]
        page['contents'] = ' '.join(BeautifulSoup(response.text, 'html.parser').get_text().replace("\n", " ").split())
        yield page
