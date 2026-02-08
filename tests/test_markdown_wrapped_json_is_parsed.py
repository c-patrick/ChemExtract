from app.services.parser import _extract_json, _add_metadata
from app.schemas.reaction import ReactionParsed


def test_markdown_wrapped_json_is_parsed():
    wrapped = """```json
    {"summary":"ok","confidence_score":0.9,"parser_version":"x","yield_percentage":null,
     "reagents":[],"solvents":[],"conditions":{}}
    ```"""

    json_text = _extract_json(wrapped)
    updated_json = _add_metadata(
        json_text,
        {
            "parser_backend": "fake",
            "model_name": "None",
            "parser_version": "v1",
        },
    )
    print(updated_json)
    parsed = ReactionParsed.model_validate_json(updated_json)
    assert parsed.summary == "ok"
