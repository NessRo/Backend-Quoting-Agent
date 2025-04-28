from src.app.utils.database import db_functions
from src.app.utils.model_api_requests import post_requests
import time

while True:
        
    print('polling')
        
    requests_ = db_functions.retrieve_request(retrieval_type='new_emails')
        
    if requests_:
        
        for request in requests_:
    
                thread_id = request[0]
                subject = request[1]
                body = request[2]
                prompt = f'subject: {subject} n\
                            body: {body}'
    

                response = post_requests.generate_llm_response(prompt=prompt,
                                                               request_type='generate-structured-quote')
                
                print(response)
    
    time.sleep(5)


# if response['classification'] == 'quote_request':

#     products = response['products']


#     array_of_input =[]

#     for product in products:
#         text_to_embed = f'Category: {product['category']} > {product['subcategory']} \nDescription: {product['name']}'
#         array_of_input.append(text_to_embed)

    
#     embeddings = asyncio.run(utils.api_functions.batch_embed_texts(texts=array_of_input))

#     internal_products = []

#     for embedding in embeddings:
#         internal_products.append(utils.db_functions.vector_search(embedding=embedding))

#     for index, product in enumerate(response['products']):
#         product['top_X_internal_products'] = [item[0] for item in internal_products[index]]


# elif response['classification'] == 'other':
#     print('send communication that what it recieved was not a request it recognizes')

# utils.db_functions.store_request(data=response,
#                                      request_type=response['classification'],
#                                      created_by='system',
#                                      status = 'initial_origination')

# print(response)