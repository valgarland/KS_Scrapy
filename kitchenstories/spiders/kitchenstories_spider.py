from scrapy import Spider, Request
from kitchenstories.items import KitchenstoriesItem
from collections import Counter
import re

class kitchenstoriesSpider(Spider):
    name = 'kitchenstories_spider'
    start_urls = ['https://www.kitchenstories.com/en/categories/dinner?page=1']
    allowed_urls = ['https://www.kitchenstories.com']



    def parse(self, response):
        num_pages = int(response.xpath('//ul[@class="pagination"]/li')[-1].xpath('./a/@href').\
                        extract()[0].split('=')[-1])

        url_list = [f'https://www.kitchenstories.com/en/categories/dinner?page={i+1}'\
                    for i in range(num_pages)]

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
        
        try:
            dish_name = response.xpath('//h1[@class="main-headline recipe-title main-headline"]/text()').extract()
        except:
            print('***** No dish name given *****')
            print(f'Offending URL: {response.url}')
            dish_name = None


        #RATING 

        try:
            stars = response.xpath('//div[@class="rating__stars"]/div/@class').extract()

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
            print('***** No rating given for dish *****')
            print(f'Offending URL: {response.url}')
            rating = None

        
        #REVIEWS FOR RATING

        try:
            reviews_for_rating = int(response.xpath('//div[@class="rating__text"]/text()').extract()[0].split()[-2])
        except:
            print('***** No reviews for rating found *****')
            print(f'Offending URL: {response.url}')
            reviews_for_rating = None


        #USER LIKES

        try:
            likes = response.xpath('//div[@class="recipe-information__buttons u-no-print"]').extract()
            user_likes = int(likes[0].split()[4].split('"')[1])
        except:
            print('***** No user likes found *****')
            print(f'Offending URL: {response.url}')
            user_likes = None


        #AUTHOR

        try:
            author = response.xpath('//p[@class="author-information__name"]/a/text()').extract_first()
        except:
            print('***** No author found *****')
            print(f'Offending URL: {response.url}')
            author = None            


        #AUTHOR TYPE

        try:
            author_type = response.xpath('//p[@class="author-information__occupation"]/text()').extract_first()
        except:
            print('***** No author type found *****')
            print(f'Offending URL: {response.url}')
            author_type = None


        #DESCRIPTION

        try:
            dish_description = response.xpath('//p[@class="author-information__text"]/text()').extract_first()
            dish_description = dish_description.replace('“','').replace('”','')
        except:
            print('***** No description provided *****')
            print(f'Offending URL: {response.url}')
            dish_description = None


        #DIFFICULTY

        try:
            difficulty = response.xpath('//div[@class="recipe-difficulty"]/span/text()').extract_first().split()[0]
        except:
            print('***** No difficulty level found *****')
            print(f'Offending URL: {response.url}')
            difficulty = None


        #PREP / BAKE / REST TIMES
        #This whole section uses the same div class 'time-container'

        try:
            times = response.xpath('//div[@class="time-container"]').extract()

            index = 0
            for i in times:
                times[index] = int(re.findall(r'\d+', i)[0])
                index +=1

            #Defining a local class to have all of the data cleaning within the class should the time units
            #be different; also becomes easy to call and evaluate where values are coming from 

            class Times:
                def __init__(self, response):
                    self.prep = response[0]
                    self.bake = response[1]
                    self.rest = response[2]    

            cooking_times = Times(times)

            prep_time = cooking_times.prep
            bake_time = cooking_times.bake
            rest_time = cooking_times.rest
        except:
            print('***** No cooking times found *****')
            print(f'Offending URL: {response.url}')
            prep_time = None
            bake_time = None
            rest_time = None        

        
        #SERVINGS

        try:
            servings = int(response.xpath('//span[@class="stepper-value"]/text()').extract_first())
        except:
            print('***** No serving number found *****')
            print(f'Offending URL: {response.url}')
            servings = None            

        
        #INGREDIENT LIST

        try:
            ingredient_list = response.xpath('//td[@class="ingredients__col-2"]/text()').extract()
            
            #new
            #ingredient_list = ingredient_list.split(',')

            ingredient_quantity = response.xpath('//td[@class="ingredients__col-1 js-col-1"]/@data-amount').extract()
            [float(i) for i in ingredient_quantity]

            ingredient_unit = response.xpath('//td[@class="ingredients__col-1 js-col-1"]/@data-unit').extract()

            if len(ingredient_quantity) != len(ingredient_list):
                condiment_quantity = ['0'] * (len(ingredient_list) - len(ingredient_quantity))
                ingredient_quantity.extend(condiment_quantity)
                ingredient_quantity = [float(i) for i in ingredient_quantity]

            condiment_unit = [''] * (len(ingredient_list) - len(ingredient_unit))
            ingredient_unit.extend(condiment_unit)
            
        except:
            print('***** No ingredients found *****')
            print(f'Offending URL: {response.url}')
            ingredient_list = None
            ingredient_quantity = None
            ingredient_unit = None


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
            
            nutr_info_values = [int(i.split(' ')[0]) for i in nutr_info[1::2]]
    
            nutr_info_units = list(map(lambda i: i[1], [i.split(' ') for i in nutr_info[1::2]]\
                [1:len(nutr_info)]))
            
            #Defining a class to have all of the data cleaning within the class; also becomeseasy to call  
            #and evaluate where the values are coming from

            class Nutrition:
                def __init__(self, response1, response2):
                    
                    self.calories = response1[0]
                    self.protein = response1[1]
                    self.fat = response1[2]
                    self.carb = response1[3]

                    self.protein_u = response2[0]
                    self.fat_u = response2[1]
                    self.carb_u = response2[2]
        
            nutrition = Nutrition(nutr_info_values, nutr_info_units)

            calories = nutrition.calories
            protein = nutrition.protein
            fat = nutrition.fat
            carb = nutrition.carb
            
            protein_u = nutrition.protein_u
            fat_u = nutrition.fat_u
            carb_u = nutrition.carb_u        

        except:
            print('***** No nutritional information found *****')
            print(f'Offending URL: {response.url}')
            calories = None
            protein = None
            fat = None
            carb = None
            protein_u = None
            fat_u = None
            carb_u = None


        #STEPS REQUIRED

        try:
            total_steps = int(response.xpath('//li[@class="step"]/h2/text()').extract_first().split('/')[-1])
        except:
            print('***** No steps found *****')
            print(f'Offeding URL: {response.url}')
            total_steps = None


        #IMAGES LISTED

        try:
            gallery = response.xpath('//div[@class="detail-page-content js-comment-wrapper"]').extract()
            image_count = int(gallery[0].split('"')[-2])
        except:
            print('***** No images found *****')
            print(f'Offending URL: {response.url}')
            image_count = None            


        #Pulling all data into defined Scrapy items
        
        #Item listing

        item = KitchenstoriesItem()
        item['dish_name'] = dish_name
        item['rating'] = rating
        item['reviews_for_rating'] = reviews_for_rating
        item['user_likes'] = user_likes
        item['author'] = author
        item['author_type'] = author_type
        item['dish_description'] = dish_description
        item['difficulty'] = difficulty
        item['prep_time'] = prep_time
        item['bake_time'] = bake_time
        item['rest_time'] = rest_time
        item['servings'] = servings
        item['ingredient_list'] = ingredient_list
        item['ingredient_quantity'] = ingredient_quantity
        item['ingredient_unit'] = ingredient_unit
        item['utensils'] = utensils
        item['calories'] = calories
        item['protein'] = protein
        item['fat'] = fat
        item['carb'] = carb
        item['protein_u'] = protein_u
        item['fat_u'] = fat_u
        item['carb_u'] = carb_u
        item['total_steps'] = total_steps
        item['image_count'] = image_count

        yield item
