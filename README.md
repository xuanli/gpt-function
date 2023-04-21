## Usage
* Specify expected behavior via python function doc string. Use `gpt_caller()` decorator on the function to indicate a gpt function.
* Uses `gpt-3.5-turbo` by default. You can also use switch to other models like `gpt-4` via `gpt_caller(model="gpt-4")`
* Call gpt functions as reuglar python functions.
* :warning: gpt functions could hallucinate due to its natural. Use them at your own risk!
* :rocket: unlock maximum potential by utilizing GPT functions and GitHub Copilot together.

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

* The idea is inspired from [Recurrency](https://www.recurrency.com/) AI Hackathon
