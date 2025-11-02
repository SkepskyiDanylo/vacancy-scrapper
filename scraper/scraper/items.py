import scrapy


class VacancyItem(scrapy.Item):
    company_name = scrapy.Field()
    position = scrapy.Field()
    city = scrapy.Field()
    region = scrapy.Field()
    country = scrapy.Field()
    skills = scrapy.Field()
    experience = scrapy.Field()
    description = scrapy.Field()
    company_url = scrapy.Field()
    vacancy_link = scrapy.Field()
