import datetime
import os
from typing import Any, AsyncGenerator, Generator

import scrapy
from scrapy import Request, Spider
from scrapy.http import Response
from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from scrapy.utils.log import logger
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper.items import VacancyItem
from scraper.settings import EMAIL, PASSWORD, RAW_DATA_FOLDER
import urllib.parse


class VacancySpider(scrapy.Spider):
    name = "vacancy"
    allowed_domains = ["linkedin.com"]
    start_urls = ["https://www.linkedin.com/jobs/search?"]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs) -> Spider:
        """
        Automatic save in csv file to the data directory.
        """
        spider = super().from_crawler(crawler, *args, **kwargs)

        region = kwargs.get("location", "Germany").lower().replace(" ", "_").strip()
        role = kwargs.get("keywords", "Python").lower().replace(" ", "_").strip()

        filename = (
            RAW_DATA_FOLDER
            / f"{region}_{role}_vacancies_{datetime.datetime.now():%Y-%m-%d_%H-%M}.csv"
        )

        crawler.settings.set(
            "FEEDS",
            {
                filename: {
                    "format": "csv",
                    "encoding": "utf8",
                    "overwrite": True,
                }
            },
        )
        return spider

    def __init__(
        self,
        keywords: str = "Python",
        location: str = "Germany",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.keywords = keywords.strip()
        self.location = location.strip()

        self.count = 0
        # Time Posted Range, adjust if needed
        self.tpr = "r2592000"

        # Selenium is used to get vacancy 'skills' section if available
        # Otherwise OpenAI will be used to get them from description
        # Skills are usually not reachable without an account
        use_selenium = all((EMAIL, PASSWORD))
        if use_selenium:
            self.driver = None
            self.selenium_status = False
            self.selenium_init()

            try:
                self.log_in()
                self.selenium_status = True
            except WebDriverException as e:
                logger.warning(f"Unable to log in to account: {e}")

    def selenium_init(self) -> None:
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        # options.add_argument("--headless")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36"
        )
        self.driver = webdriver.Chrome(options=options)

    def log_in(self) -> None:
        url = "https://www.linkedin.com/login/"
        driver = self.driver
        if not driver:
            return
        driver.get(url)
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")

        username_input.send_keys(EMAIL)
        password_input.send_keys(PASSWORD)
        button.click()

    def start_requests(self) -> Generator[Request, None, None]:
        keywords = self.keywords
        location = self.location

        query = {
            "keywords": keywords,
            "location": location,
            "f_tpr": self.tpr,
        }

        for url in self.start_urls:
            full_url = url + urllib.parse.urlencode(query)
            yield scrapy.Request(url=full_url, callback=self.parse)

    def parse_skills_selenium(self, url: str) -> list[str | None]:
        if not self.selenium_status:
            self.logger.info("Selenium is unavailable.")
            return []

        self.logger.info("Start parsing skills via selenium.")

        try:
            driver = self.driver
            driver.get(url)

            button = driver.find_element(
                By.CSS_SELECTOR, 'button svg[data-test-icon="skills-small"]'
            )

            parent_button = button.find_element(By.XPATH, "./ancestor::button")
            parent_button.click()

            wait = WebDriverWait(driver, 5)
            popup = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.artdeco-modal__content")
                )
            )

            skills = popup.find_elements(
                By.CSS_SELECTOR, "span.skill-name, div.pvs-list__item--line-clamp"
            )
            skills = [skill.text.strip() for skill in skills if skill.text]
            return skills
        except WebDriverException as e:
            logger.warning(f"Error while parsing skills via selenium: {e}")
        return []

    def parse_detail(
        self, response: Response, **kwargs
    ) -> Generator[VacancyItem, None, None]:
        self.logger.info(
            f"Parsing vacancy: {kwargs.get("position")} at {kwargs.get("company_name")}, url={response.url}"
        )
        description = response.css("div.show-more-less-html__markup")
        description_parts = description.xpath(".//text()").getall()
        self.logger.info(f"Parsing {description_parts}")

        description_text = " ".join(
            [part.strip() for part in description_parts if part.strip()]
        )

        skills = self.parse_skills_selenium(response.url)
        self.count += 1
        yield VacancyItem(
            description=description_text,
            skills=skills,
            **kwargs,
        )

    async def parse(self, response, **kwargs) -> AsyncGenerator[Request, Any]:

        vacancies = response.css("div.base-card")
        self.logger.info(f"Found {len(vacancies)} vacancies")

        for vacancy in vacancies:

            vacancy_link = (
                vacancy.css("a.base-card__full-link::attr(href)")
                .get(default="N/A")
                .strip()
            )
            company_element = vacancy.css("h4.base-search-card__subtitle")
            company_name = company_element.css("a::text").get(default="N/A").strip()
            company_url = (
                company_element.css("a::attr(href)").get(default="N/A").strip()
            )

            position = (
                vacancy.css("h3.base-search-card__title::text")
                .get(default="N/A")
                .strip()
            )

            location = (
                vacancy.css("span.job-search-card__location::text")
                .get(default="N/A")
                .strip()
            )

            location = location.replace("None", "").strip(", ")

            yield scrapy.Request(
                url=vacancy_link,
                callback=self.parse_detail,
                cb_kwargs={
                    "company_name": company_name,
                    "position": position,
                    "vacancy_location": location,
                    "location": self.location,
                    "company_url": company_url,
                    "vacancy_link": vacancy_link,
                },
            )
