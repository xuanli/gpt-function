import pytest
from gpt_function import gpt_caller, _strip_json, _get_type_name


@gpt_caller()
def add_two_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    pass


def test_add_function(monkeypatch):
    def fake_call(*args, **kwargs):
        return '{"thought": "", "reasoning": "", "reflection": "", "return": 3}'

    monkeypatch.setattr("gpt_function.call_chatgpt", fake_call)
    assert add_two_numbers(1, 2) == 3


@gpt_caller()
def summary_text(text: str) -> str:
    """Summarize a text to 1 sentence"""
    pass


def test_summary_text(monkeypatch):
    summary = "AI is intelligence shown by machines."

    def fake_call(*args, **kwargs):
        return (
            '{"thought": "", "reasoning": "", "reflection": "", "return": ' + repr(summary) + "}"
        )

    monkeypatch.setattr("gpt_function.call_chatgpt", fake_call)
    input_text = "some long input"
    assert summary_text(input_text) == summary


@gpt_caller(model="gpt-3.5-turbo")
def get_US_states(region: str = "All") -> list[dict]:
    """Return a list of dictionaries containing the name, abbreviation, and capital of each US state filtered by region."""
    pass


def test_get_US_states(monkeypatch):
    mocked_return = [
        {"name": "California", "abbreviation": "CA", "capital": "Sacramento"},
        {"name": "Oregon", "abbreviation": "OR", "capital": "Salem"},
        {"name": "Washington", "abbreviation": "WA", "capital": "Olympia"},
    ]

    def fake_call(*args, **kwargs):
        return '{"thought": "", "reasoning": "", "reflection": "", "return": ' + repr(mocked_return) + "}"

    monkeypatch.setattr("gpt_function.call_chatgpt", fake_call)
    states = get_US_states(region="West_Coast_Mainland")
    assert states == mocked_return


def test_strip_json():
    raw = "prefix {\"a\": 1} suffix"
    assert _strip_json(raw) == '{"a": 1}'


def test_strip_json_error():
    with pytest.raises(ValueError):
        _strip_json("no json here")


def test_get_type_name_list():
    assert _get_type_name(list[str]) == "list"
