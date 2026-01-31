from openai import OpenAI
import json
from app.schemas.reaction import ReactionParsed
from app.core.config import settings

# Set variables from .env file
PARSER_BACKEND = settings.parser_backend
print(f"Using parser backend: {PARSER_BACKEND}")

OPENAI_API_KEY = settings.openai_api_key
print(f"OpenAI API Key set: {OPENAI_API_KEY}")

client = OpenAI(api_key=OPENAI_API_KEY)


def fake_parse_document(text: str) -> dict:
    return {
        "summary": "Fake parsed reaction",
        "confidence_score": 0.5,
        "parser_version": "fake-1.0",
        "yield_percentage": None,
        "reagents": [],
        "solvents": [],
        "conditions": {},
    }


def _extract_json(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        # Remove ```json and ``` wrappers
        text = text.split("```")[1]
        text = text.replace("json", "", 1)

    return text.strip()


def _add_parser_version(text: str, parser_version: str):
    text_json = json.loads(text)
    text_json["parser_version"] = parser_version
    return json.dumps(text_json)


def openai_parse_document(text: str) -> dict:
    if not settings.openai_api_key:
        raise RuntimeError("OpenAI parsing enabled but no API key configured")

    if len(text) > 15_000:
        raise ValueError("Document too long for OpenAI parsing")

    prompt = f"""
You are a chemistry assistant.

Extract reaction information from the following experimental procedure.
Return raw JSON only.
Do NOT include markdown, code fences, or explanations.

- summary (string)
- confidence_score (number between 0 and 1)
- yield_percentage (number or null)
- reagents (list of strings)
- solvents (list of strings)
- conditions (object with string keys and values)

Experimental text:
{text}
"""

    model = "gpt-4o-mini"
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You extract structured chemistry data."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    raw = response.choices[0].message.content
    json_text = _extract_json(raw)

    if "parser_version" not in text:
        json_text = _add_parser_version(json_text, parser_version=model)

    # Validate + coerce
    parsed = ReactionParsed.model_validate_json(json_text)

    return {
        **parsed.model_dump(),
        "parser_version": "openai-gpt-4o-mini",
    }


def parse_document(text: str) -> dict:
    """
    Main parsing entry point.
    This will later switch between fake / OpenAI parsers.
    """
    if PARSER_BACKEND == "openai":
        return openai_parse_document(text)

    return fake_parse_document(text)
