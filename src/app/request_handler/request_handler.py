import time
from src.app.utils.database import db_functions
from src.app.utils.model_api_requests import post_requests

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

                try:
                    response = post_requests.generate_llm_response(prompt=prompt,
                                                                request_type='generate-structured-quote')
                    
                    response.setdefault('comments', 'llm failed to structure data')
                    print(response)

                    if response['success'] == False:
                        
                        db_functions.store_request(request_type='other',
                                    status='refine_requirements',
                                    source='email',
                                    source_id=thread_id,
                                    reply_sent=False,
                                    comments=response['comments'])
                        
                        db_functions.update_request_status(status='processed',
                                                        thread_id=thread_id,
                                                        update_type='email_status')
                    elif response['success'] == True:
                            
                            db_functions.store_request(request_type='quote_request',
                                        status='ready_for_quote',
                                        source='email',
                                        source_id=thread_id,
                                        reply_sent=False,
                                        comments=response['comments'])
                            
                            db_functions.update_request_status(status='processed',
                                                            thread_id=thread_id,
                                                            update_type='email_status')
                            
                            #TODO store the quote JSON here using a db_function in the quotes tables
                except KeyError:
                      continue
                        
        print('waiting')
        time.sleep(5)






