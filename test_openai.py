import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

try:
    client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': 'test'}]
    )
    print('Success')
except Exception as e:
    print('Error:', type(e), e)
