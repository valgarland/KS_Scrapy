# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class KitchenstoriesItem(scrapy.Item):
    dish_name = scrapy.Field()
    rating = scrapy.Field()
    rating_based_on_reviews = scrapy.Field()
    author = scrapy.Field()
    author_type = scrapy.Field()
    dish_description = scrapy.Field()
    difficulty = scrapy.Field()
    prep_time = scrapy.Field()
    bake_time = scrapy.Field()
    rest_time = scrapy.Field()
    servings = scrapy.Field()
    ingredient_list = scrapy.Field()
    utensils = scrapy.Field()
    calories = scrapy.Field()
    protein = scrapy.Field()
    fat = scrapy.Field()
    carb = scrapy.Field()
    total_steps = scrapy.Field()
    num_comments = scrapy.Field()
