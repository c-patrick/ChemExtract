import time


def fake_parse_document(text: str) -> dict:
    """A fake document parser that simulates parsing delay."""
    time.sleep(1)  # Simulate time-consuming parsing
    return {
        "summary": "This is a summary of the document.",
        "confidence_score": 0.95,
        "parser_version": "1.0.0",
    }
