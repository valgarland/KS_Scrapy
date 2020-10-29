from scrapy import Spider, Request
from kitchenstories.items import KitchenstoriesItem

class kitchenstoriesSpider(Spider):
    name = 'kitchenstories_spider'
    start_urls = ['https://www.kitchenstories.com/en/categories/dinner?page=1']
    allowed_urls = ['https://www.kitchenstories.com']


    def parse(self, response):
        num_pages = int(response.xpath('//ul[@class="pagination"]/li')[-1].xpath('./a/@href').\
                        extract()[0].split('=')[-1])

        url_list = [f'https://www.kitchenstories.com/en/categories/dinner?page={i+1}'\
                    for i in range(3)] #range(num_pages)]

        for url in url_list:

            #Testing to see whether urls print out correctly

            print('*'*30)
            print(url)
            print('*'*30)

            yield Request(url = url, callback = self.parse_dinner_page)


    def parse_dinner_page(self, response):
        dishes = response.xpath('//a[@class="archive-tile__link link--covers-container"]/@href').extract()

        dish_urls = [f'https://www.kitchenstories.com{url}' for url in dishes]

        for url in dish_urls:

            #Testing to see whether urls print out correctly

            print('*'*30)
            print(url)
            print('*'*30)
            
            yield Request(url = url, callback = self.parse_dish_page)


    def parse_dish_page(self, response):
        
        try:
            dish_name = response.xpath('//h1[@class="main-headline recipe-title main-headline"]/text()').extract()

        except:
            print('***** No dish name found - null dish name provided *****')
            print(f'Offending URL: {response.url}')
            dish_name = None


