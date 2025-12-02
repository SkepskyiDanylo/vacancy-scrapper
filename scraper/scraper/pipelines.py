from scraper.data_extractor import AsyncExtractor
from scraper.settings import OPENAI_API_KEY


class AsyncOpenAIPipeline:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.extractor = AsyncExtractor(api_key=OPENAI_API_KEY)


    async def process_item(self, item, spider):
        spider.logger.info(f"Processing {item} skills")
        description = item.get("description")
        skills = item.get("skills")
        if description and not skills:
            try:
                data = await self.extractor.extract(description, translate_to="en")
                item["skills"] = data.get("skills", None)
                item["experience"] = data.get("experience", None)
            except Exception as e:
                spider.logger.warning(f"Unable to fetch skills via openAPI: {e}")
                item["skills"] = ""
        return item
