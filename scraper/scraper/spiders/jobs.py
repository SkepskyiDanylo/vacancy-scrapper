import scrapy


class JobsSpider(scrapy.Spider):
    name = "jobs"
    allowed_domains = ["linkedin.com"]
    start_urls = ["https://www.linkedin.com/jobs/search?"]

    def parse(self, response):
        pass
