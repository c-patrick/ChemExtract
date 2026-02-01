import json
from unittest.mock import patch
from app.services.parser import openai_parse_document


@patch("app.services.parser.call_openai_raw")
def test_openai_low_confidence_returns_none(mock_call):
    mock_call.return_value = json.dumps(
        {
            "summary": "Something",
            "confidence_score": 0.2,
            "yield_percentage": None,
            "reagents": [],
            "solvents": [],
            "conditions": {},
        }
    )

    result = openai_parse_document("text")

    assert result is None


@patch("app.services.parser.call_openai_raw")
def test_openai_valid_parse(mock_call):
    mock_call.return_value = json.dumps(
        {
            "summary": "Reaction",
            "confidence_score": 0.9,
            "yield_percentage": 85,
            "reagents": ["A", "B"],
            "solvents": ["THF"],
            "conditions": {"temp": "25 C"},
        }
    )

    parsed = openai_parse_document("text")

    assert parsed is not None
    assert parsed.yield_percentage == 85
