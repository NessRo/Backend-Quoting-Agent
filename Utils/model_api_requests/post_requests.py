import requests
import json
from Utils.Generic import ingestion_functions
import os
import asyncio
from dotenv import load_dotenv
import json

load_dotenv()

def Generate_unstructured_classification(prompt):
    end_point = os.getenv("MODEL_GENERATE_END_POINT")

    data = {
    "model": "deepseek-r1:32b",  # Ensure this matches your Ollama model name
    "system": ingestion_functions.model_context_ingestion(
        file_path='./Model_context/request_classification_context.txt',
        context_type = 'request_classification'
    ),
    "prompt":  prompt,
    "format": "json",
    "stream": False  # Set to True for streaming responses
    }

    headers = {"Content-Type": "application/json"}

    # Send the request
    response = requests.post(end_point, headers=headers, data=json.dumps(data))

    # Print the response
    if response.status_code == 200:
        return json.loads(response.json()['response'].strip())
    else:
        return json.loads(response.text)