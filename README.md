## Usage
* Write down function's expected behavior via doc string.
* Use gpt_caller() decorator on the function.
* Call gpt function as reuglar python function.
* :warning: gpt function hallucinates from time to time due to it's natural. Use them at at your own risk!

## Example

``` python

import openai
from gpt_function import gpt_caller

#set your openai api key
openai.api_key = os.environ.get("OPENAI_API_KEY") or ""

@gpt_caller()
def get_US_states() -> list[dict]:
    """Get a list of all US states
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

states = get_US_states()
for state in states:
    print(state["name"], state["abbreviation"], state["capital"])
```

## Installation
```
git clone https://github.com/xuanli/gpt-function.git
cd gpt-function
pip install -r requirements.txt
```

## Extra
* The idea is inspired by the Recurrency Hackathon