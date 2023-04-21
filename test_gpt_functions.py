import os
import openai

from gpt_function import gpt_caller

#set your openai api key
openai.api_key = os.environ.get("OPENAI_API_KEY") or ""

@gpt_caller()
def add_two_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    pass

def test_add_function():
    assert add_two_numbers(1, 2) == 3


@gpt_caller()
def summary_text(text: str) -> str:
    """Summarize a text to 1 sentence"""
    pass

def test_summary_text():
    input = """Artificial intelligence (AI) is intelligence—perceiving, 
    synthesizing, and inferring information—demonstrated by machines, 
    as opposed to intelligence displayed by non-human animals or by humans. 
    Example tasks in which this is done include speech recognition, 
    computer vision, translation between (natural) languages, 
    as well as other mappings of inputs.
    AI applications include advanced web search engines (e.g., Google Search), 
    recommendation systems (used by YouTube, Amazon, and Netflix), 
    understanding human speech (such as Siri and Alexa), self-driving cars (e.g., Waymo), 
    generative or creative tools (ChatGPT and AI art), automated decision-making, 
    and competing at the highest level in strategic game systems (such as chess and Go).
    """
    result = summary_text(input)
    assert len(result) > 0 and len(result) < len(input)

@gpt_caller()
def get_US_states() -> list[dict]:
    """Return a list of all US states
    
    Returns:
        list[dict]: A list of dictionaries containing the name, abbreviation, and capital of each US state. eg:
        [
            {
                "name": "Alabama",
                "abbreviation": "AL",
                "capital": "Montgomery"
            },
            ...
        ]
    """
    pass
    

def test_get_all_US_states():
    states = get_US_states()
    assert len(states) == 50
    assert "name" in states[0] and "abbreviation" in states[0] and "capital" in states[0]
