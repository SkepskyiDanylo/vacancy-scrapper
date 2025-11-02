import json
import logging

import openai


class AsyncExtractor:
    INSTRUCTION = """
    You are an assistant for extracting structured data from a job description.
    1. If the text is not in English, translate it to {translate_to}.
    2. Extract a list of skills, without any explanations.
    3. Extract the required experience in years (just the bottom number), e.g., 
   2-3 years → 2, 5+ years → 5. If not specified, use N/A.
    4. Respond ONLY in the following JSON format:

    {{ 
  "skills": ["skill1", "skill2", ...],
  "experience": "3"
    }}
    """

    TOOLS = [
    {
        "type": "function",
        "name": "get_vacancy_data",
        "description": "Extract required skills and years of experience from a vacancy description.",
        "parameters": {
            "type": "object",
            "properties": {
                "skills": {"type": "array", "items": {"type": "string"}, "description": "Return all skills as lowercase, unique values."},
                "experience": {
                    "type": ["integer", "string"],
                    "description": (
                        "Number of years required."
                        "Bottom if range given, e.g. 1-3 = 1"
                        "N/A if not found"
                    ),
                },
            },
            "required": ["skills", "experience"],
            "additionalProperties": False,
        },
    "strict" : True,
    },
]

    def __init__(self, api_key: str = None):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing OpenAI Extractor")

        self.is_active = bool(api_key)
        if not self.is_active:
            self.logger.error("Please add a valid OpenAI API key to .env. Status is unactive.")

        self.client = openai.AsyncOpenAI(api_key=api_key)

    async def extract(self, description: str, translate_to: str = "en") -> dict:
        data = {"skills": [], "experience": "N/A"}

        if not self.is_active:
            self.logger.warning("OpenAI status is unactive.")
            return data

        try:
            self.logger.info("OpenAI starting to extract data.")
            response = await self.client.responses.create(
                model="gpt-4.1-mini",
                instructions=self.INSTRUCTION.format(translate_to=translate_to),
                input=description,
                tools=self.TOOLS,
            )
        except openai.RateLimitError:
            self.logger.warning("OpenAI got 429 while trying to fetch data.")
            self.is_active = False
            return data

        for out in response.output:
            if out.type == "function_call":
                try:
                    return json.loads(out.arguments)
                except (json.decoder.JSONDecodeError, json.JSONDecodeError) as e:
                    self.logger.warning(f"Error parsing JSON. {e}", )
        return data
