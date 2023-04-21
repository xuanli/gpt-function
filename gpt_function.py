from functools import wraps
from typing import get_type_hints
import logging
import json
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
                return json.loads(result)
            return result
        return wrapper
    
    return gpt_caller_decorator

def run_gpt_function(func: callable,
                     args: dict,
                     gpt_model = MODEL_GPT35) -> object:
    func_name = "def " + func.__name__ + str(inspect.signature(func))
    description = func.__doc__
    system_prompt = f"""INSTRUCTIONS:
    1. You are this function: {func_name}. 
    2. Function description: {description.strip()}.
    3. Act as {func_name} and respond with json.dumps(<return value>) based on given arguments.
    4. Think step by step and explain your reasoning.
    5. Reflect and critize your answer before you respond.
    6. Output JSON format:
    {{
        "thought": <thoughts>,
        "reasoning": <reasoning>,
        "reflection": <reflection>,
        "return": <result>
    }}
    - STRICTLY FOLLOW ABOVE FORMAT. DO NOT RESPOND WITH ANYTHING ELSE.
    """

    reply = call_chatgpt(system_prompt, "args:" + str(args), model=gpt_model, temperature=0.0)
    try:
        reply_dict = json.loads(reply)
        return reply_dict["return"]
    except json.decoder.JSONDecodeError:
        logging.error(f"Failed to parse reply: {reply}")
    

def call_chatgpt(system_prompt: str, 
                 user_prompt: str, 
                 model: str = MODEL_GPT4, 
                 temperature: float =0.0, **prompt_kwargs) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    retries = 0
    while retries < 3:
        try:
            response = openai.ChatCompletion.create(
                model=model, messages=messages, temperature=temperature, **prompt_kwargs
            )
            reply = response["choices"][0]["message"]["content"]
            return reply
        except RateLimitError:
            retries += 1
            logging.info(f"Encountered RateLimitError. Retrying attempt {retries} of {_MAX_RETRIES}.")
            
    else:
        raise RateLimitError("Failed to complete the API request after 3 retries due to rate limits.")

def _get_type_name(type_hint):
    if type_hint is None:
        return None
    if hasattr(type_hint, '__origin__'):
        return type_hint.__origin__.__name__
    else:
        return type_hint.__name__