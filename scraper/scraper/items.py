import scrapy


class VacancyItem(scrapy.Item):
    company_name = scrapy.Field()
    position = scrapy.Field()
    vacancy_location = scrapy.Field()
    location = scrapy.Field()
    skills = scrapy.Field()
    experience = scrapy.Field()
    description = scrapy.Field()
    company_url = scrapy.Field()
    vacancy_link = scrapy.Field()
