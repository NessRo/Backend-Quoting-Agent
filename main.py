import requests
import json
import Utils
import asyncio


prompts = Utils.ingestion_functions.user_text_prompt_ingestion(file_path='./samples/quote_request_samples.txt')

prompt = prompts[0]


response = Utils.post_requests.Generate_unstructured_classification(prompt=prompt)

if response['classification'] == 'quote_request':

    products = response['products']

    array_of_input =[]

    for product in products:
        text_to_embed = f'Category: {product['category']} > {product['subcategory']} \nDescription: {product['name']}'
        array_of_input.append(text_to_embed)

    
    embeddings = asyncio.run(Utils.api_functions.batch_embed_texts(texts=array_of_input))

    for embedding in embeddings:
        internal_products = Utils.db_functions.vector_search(embedding=embedding)
        print(internal_products)
    

elif response['classification'] == 'other':
    print('send communication that what it recieved was not a request it recognizes')





