from app.services.parser import _extract_json
from app.schemas.reaction import ReactionParsed


def test_markdown_wrapped_json_is_parsed():
    wrapped = """```json
    {"summary":"ok","confidence_score":0.9,"parser_version":"x","yield_percentage":null,
     "reagents":[],"solvents":[],"conditions":{}}
    ```"""

    json_text = _extract_json(wrapped)
    print(json_text)
    parsed = ReactionParsed.model_validate_json(json_text)
    assert parsed.summary == "ok"
