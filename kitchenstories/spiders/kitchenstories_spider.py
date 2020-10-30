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

        #RATING 

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

        
        #REVIEWS FOR RATING

        try:
            reviews_for_rating = int(response.xpath('//div[@class="rating__text"]/text()').extract()[0].split()[-2])
        except:
            print('***** Rating based on 0 reviews - returning 0 *****')
            print(f'Offending URL: {response.url}')
            reviews_for_rating = None


        #USER LIKES

        try:
            user_likes = response.xpath('//div[@class="recipe-information__buttons u-no-print"]').extract()
            user_likes = int(like[0].split()[4].split('"')[1])
        except:
            print('***** No user likes found *****')
            print(f'Offending URL: {response.url}')
            user_likes = None


        #AUTHOR
        #Author always available, hence no try/except

        author = response.xpath('//p[@class="author-information__name"]/a/text()').extract_first()


        #AUTHOR TYPE
        #Autor type always available, hence no try/except

        author_type = response.xpath('//p[@class="author-information__occupation"]/text()').extract_first()


        #DESCRIPTION

        try:
            description = response.xpath('//p[@class="author-information__text"/text()').extract_first()
        except:
            print('***** No description provided *****')
            print(f'Offending URL: {response.url}')
            description = None


        #DIFFICULTY

        try:
            difficulty = response.xpath('//h2[@class="sub-headline"]/text()').extract_first()
        except:
            print('***** No difficulty level found *****')
            print(f'Offending URL: {response.url}')
            difficulty = None


        #PREP / BAKE / REST TIMES
        #This whole section uses the same div class 'time-container'
        #Defining a local class to have all of the data cleaning within the class; also becomes
        #easy to call and evaluate where values are coming from 

        times = response.xpath('//div[@class="time-container"]').extract()

        index = 0
        for i in times:
            times[index] = int(re.findall(r'\d+', i)[0])
            index +=1

        prep_time = times[0]
        bake_time = time[1]
        rest_time = time[2]

        
        #SERVINGS

        servings = int(response.xpath('//span[@class="stepper-value"]/text()').extract_first())

        
        #INGREDIENT LIST

        ingredients = response.xpath('//td[@class="ingredients__col-2"]/text()').extract()


        #UTENSILS

        try:
            utensils = response.xpath('//ul[@class="comma-separated-list"]/li/text()').extract()
        except:
            print('***** No utensils found *****')
            print(f'Offending URL: {response.url}')
            utensils = None


        #NUTRITIONAL INFORMATION
        #This whole section uses the same div class 'recipe-nutrition__information'

        try:
            nutr_info = response.xpath('//div[@class="recipe-nutrition__information"]/div/span/text()').extract()

            #Defining a class to have all of the data cleaning within the class; also becomeseasy to call  
            #and evaluate where the values are coming from

            class Nutrition:
                def __init__(self, nutr_info):
                    nutr_info = [int(i.split(' ')[0]) for i in nutr_info[1::2]]
                    self.cal = nutr_info[0]
                    self.protein = nutr_info[1]
                    self.fat = nutr_info[2]
                    self.carb = nutr_info[3]
        
            nutrition = Nutrition(nutr_info)

            cal = Nutrition.cal
            protein = Nutrition.protein
            fat = Nutrition.fat
            carb = Nutrition.carb

        except:
            print('***** No nutritional information found *****')
            print(f'Offending URL: {response.url}')
            cal = None
            protein = None
            fat = None
            carb = None


        #STEPS REQUIRED

        try:
            steps = int(response.xpath('//li[@class="step"]/h2/text()').extract_first().split('/')[-1])
        except:
            print('***** No steps found *****')
            print(f'Offeding URL: {response.url}')
            steps = 0            


        #Item listing
        item = KitchenstoriesItem()
        item['dish_name'] = dish_name
        item['rating'] = rating
        item['reviews_for_rating'] = reviews_for_rating
        item['author'] = author
        item['author_type'] = author_type
        item['description'] = description
        item['difficulty'] = difficulty
        item['prep_time'] = prep_time
        item['bake_time'] = bake_time
        item['rest_time'] = rest_time
        item['servings'] = servings
        item['ingredient_list'] = ingredient_list
        item['utensils'] = utensils
        item['cal'] = cal
        item['protein'] = protein
        item['fat'] = fat
        item['carb'] = carb
        item['total_steps'] = total_steps

        yield item

