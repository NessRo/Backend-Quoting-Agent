import requests
import json
import utils
import asyncio



prompts = utils.ingestion_functions.user_text_prompt_ingestion(file_path='./samples/quote_request_samples.txt')

prompt = prompts[0]


response = utils.post_requests.Generate_unstructured_classification(prompt=prompt)

if response['classification'] == 'quote_request':

    products = response['products']


    array_of_input =[]

    for product in products:
        text_to_embed = f'Category: {product['category']} > {product['subcategory']} \nDescription: {product['name']}'
        array_of_input.append(text_to_embed)

    
    embeddings = asyncio.run(utils.api_functions.batch_embed_texts(texts=array_of_input))

    internal_products = []

    for embedding in embeddings:
        internal_products.append(utils.db_functions.vector_search(embedding=embedding))

    for index, product in enumerate(response['products']):
        product['top_X_internal_products'] = [item[0] for item in internal_products[index]]


elif response['classification'] == 'other':
    print('send communication that what it recieved was not a request it recognizes')

utils.db_functions.store_request(data=response,
                                     request_type=response['classification'],
                                     created_by='system',
                                     status = 'initial_origination')

print(response)





