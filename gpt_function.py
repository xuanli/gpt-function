from functools import wraps
import demjson3
from typing import get_type_hints
import logging
import inspect
import openai
from openai.error import RateLimitError

MODEL_GPT35 = "gpt-3.5-turbo"
MODEL_GPT4 = "gpt-4"
_MAX_RETRIES = 3

def gpt_caller(model=MODEL_GPT35):

    def gpt_caller_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            arguments = {**kwargs}
            for i, arg in enumerate(args):
                arguments[func.__code__.co_varnames[i]] = arg
            result = run_gpt_function(func, arguments, model)
            result_type_str = _get_type_name(type(result))
            return_type_hint = _get_type_name(get_type_hints(func).get('return'))
            if result_type_str != return_type_hint and result_type_str == 'str':
                return demjson3.decode(result)
            return result
        return wrapper
    
    return gpt_caller_decorator

def run_gpt_function(func: callable,
                     args: dict,
                     gpt_model = MODEL_GPT35) -> object:
    func_name = "def " + func.__name__ + str(inspect.signature(func))
    description = func.__doc__
    system_msg = fr"""FACTS:
1. You are this function: {func_name}. 
2. Function description: {description.strip()}.
3. Function argument is specified in the "Input" section.

INSTRUCTIONS: 
1. Reply with the json.dumps(return_value) of the function.
2. Think step by step and explain your thought process and reasoning.
3. Reflect and criticize your answer before you respond.
4. Output JSON string format:
{{
    "thought": "<thoughts>",
    "reasoning": "<reasoning>",
    "reflection": "<reflection>",
    "return": "<reply>",
}}
- STRICTLY FOLLOW ABOVE FORMAT. DO NOT RESPOND WITH ANYTHING ELSE.
"""

    default_user_msg = fr"""Input:{args or "None"}
Output:"""

    retries = 0
    last_error = None
    last_reply = None
    while retries < _MAX_RETRIES:
        
        user_msg_with_error = fr"""Last message error:{last_error}
Input: {args or "None"}
Fixed Output:
"""
        
        user_msg = user_msg_with_error if retries > 0 else default_user_msg
        
        reply = call_chatgpt(system_msg, 
                             user_msg, 
                             last_reply, 
                             model=gpt_model, 
                             temperature=0.0, 
                             use_stream=False)
        last_reply = reply
        try:
            reply = _strip_json(reply)
            reply_dict = demjson3.decode(reply)
            return reply_dict["return"]
        except demjson3.JSONDecodeError as e:
            retries += 1
            last_error = "JSONDecodeError:" + str(e)
            logging.error(f"Failed to parse reply: {reply}")
            logging.error(f"GPT JSON Parsing error. Retrying attempt of {retries} of {_MAX_RETRIES}")
        except ValueError as e:
            retries += 1
            last_error = "ValueError:" + str(e)
            logging.error(f"Failed to parse reply: {reply}")
            logging.error(f"GPT JSON Parsing error. Retrying attempt of {retries} of {_MAX_RETRIES}")
            

def call_chatgpt(system_msg: str, 
                 user_msg: str, 
                 assistant_msg: str, 
                 model: str = MODEL_GPT4, 
                 temperature: float =0.0, 
                 max_tokens: int = 2048,
                 use_stream: bool = False,
                 **prompt_kwargs) -> str:
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "assistant", "content": assistant_msg or ""},
        {"role": "user", "content": user_msg or ""},
    ]

    retries = 0
    while retries < _MAX_RETRIES:
        try:
            if use_stream:
                result = []
                for response in openai.ChatCompletion.create(
                    model=model, 
                    messages=messages, 
                    temperature=temperature, 
                    max_tokens=max_tokens, 
                    stream=True,
                    frequency_penalty=0,
                    presence_penalty=0,
                    **prompt_kwargs
                ):
                    reply = response["choices"][0].get("delta", {}).get("content")
                    if reply is not None:
                        result.append(reply)
                return "".join(result)
            else:
                response = openai.ChatCompletion.create(
                    model=model, 
                    messages=messages, 
                    temperature=temperature, 
                    max_tokens=max_tokens, 
                    stream=False,
                    frequency_penalty=0,
                    presence_penalty=0,
                    **prompt_kwargs
                )
                reply = response["choices"][0]["message"]["content"]
                return reply
        except RateLimitError:
            retries += 1
            logging.info(f"Encountered RateLimitError. Retrying attempt {retries} of {_MAX_RETRIES}.")
    else:
        raise RateLimitError(f"Failed to complete the API request after {_MAX_RETRIES} retries due to rate limits.")

def _strip_json(response: str) -> str:
      try:
        start = response.index("{")
        end = response.rindex("}")
        return response[start:end+1]
      except ValueError:
            raise ValueError("Failed to strip JSON from curly braces")

def _get_type_name(type_hint):
    if type_hint is None:
        return None
    if hasattr(type_hint, '__origin__'):
        return type_hint.__origin__.__name__
    else:
        return type_hint.__name__