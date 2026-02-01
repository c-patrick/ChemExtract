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
        "confidence_score": 0.9,
        "parser_version": "fake-1.0",
        "yield_percentage": None,
        "reagents": [],
        "solvents": [],
        "conditions": {},
    }


def _extract_json(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        text = text.split("```")[1]
        if text.lstrip().startswith("json"):
            text = text.lstrip()[4:]

    return text.strip()


def _add_parser_version(text: str, parser_version: str) -> str:
    data = json.loads(text)
    data["parser_version"] = parser_version
    return json.dumps(data)


def call_openai_raw(text: str, model: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You extract structured chemistry data."},
            {"role": "user", "content": text},
        ],
        temperature=0,
    )

    return response.choices[0].message.content


def parse_openai_json(raw: str, model: str) -> ReactionParsed:
    json_text = _extract_json(raw)

    if "parser_version" not in json_text:
        json_text = _add_parser_version(json_text, parser_version=model)

    return ReactionParsed.model_validate_json(json_text)


def openai_parse_document(text: str) -> ReactionParsed | None:
    if not settings.openai_api_key:
        raise RuntimeError("OpenAI parsing enabled but no API key configured")

    if len(text) > 15_000:
        raise ValueError("Document too long for OpenAI parsing")

    model = "gpt-4o-mini"

    prompt = f"""
You are a chemistry assistant.

Extract reaction information from the following experimental procedure.
Return raw JSON only.
Do NOT include markdown, code fences, or explanations.

- summary (string, this is a brief description of the reaction)
- confidence_score (number between 0 and 1)
- yield_percentage (number or null)
- reagents (list of strings)
- solvents (list of strings)
- conditions (object with string keys and values)

Experimental text:
{text}
"""

    raw = call_openai_raw(prompt, model)
    parsed = parse_openai_json(raw, model)

    if parsed.confidence_score < settings.min_parse_confidence:
        return None  # <-- important change

    return parsed


def parse_document(text: str) -> dict:
    """
    Main parsing entry point.
    This will later switch between fake / OpenAI parsers.
    """
    print(f"Parsing document with backend: {settings.parser_backend}")

    if settings.parser_backend == "openai":
        parsed = openai_parse_document(text)
        if parsed is not None:
            return parsed.model_dump()

    return fake_parse_document(text)
