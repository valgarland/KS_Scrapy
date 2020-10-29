from scrapy import Spider, Request
from kitchenstories.items import KitchenstoriesItem
from collections import Counter

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
        
        #DISH NAME
        #NOTE: Did not use try/except since dish name is always present - otherwise dish wouldn't exist
        dish_name = response.xpath('//h1[@class="main-headline recipe-title main-headline"]/text()').extract()

        #RATING SCRAPE

        try:
            rating = 0
            index = 0

            for i in stars:
                i = i.split('--')[-1]
                stars[index] = i
                index +=1

            #NOTE: .count() could've been used to count the number of filled/half-filled stars, but that would
            #       require going through the list twice. If this were a large list, it would technically be 
            #       slower, hence the choice of using dictionaries   

            stars = Counter(stars)
            stars['half-filled']=stars['half-filled']/2

            for k, v in stars.items():
                if k == 'filled' or k == 'half-filled':
                    rating = v + rating
        except:
            print('***** No rating given for dish - assuming 0 stars *****')
            print(f'Offending URL: {response.url}')
            rating = None

        
        #REVIEWS FOR RATING SCRAPE

        try:
            reviews_for_rating = int(response.xpath('//div[@class="rating__text"]/text()').extract()[0].split()[-2])
        except:
            print('***** Rating based on 0 reviews - returning 0 *****')
            print(f'Offending URL: {response.url}')
            reviews_for_rating = None




