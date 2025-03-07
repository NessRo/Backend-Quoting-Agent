import time
from src.app.utils.database import db_functions
from src.app.utils.model_api_requests import post_requests

types_of_requests = ['quote_request','other']


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


                response = post_requests.generate_unstructured_classification(prompt=prompt)

                print(response)

                if response['classification'] in types_of_requests:

                    match response['classification']:
                        case "quote_request":
                                db_functions.store_request(request_type=response['classification'],
                                            status='ready_for_quote',
                                            source='email',
                                            source_id=thread_id,
                                            reply_sent=False)
                                
                                db_functions.update_request_status(status='processed',
                                                                thread_id=thread_id)
                        case "other":
                                db_functions.store_request(request_type=response['classification'],
                                            status='refine_requirements',
                                            source='email',
                                            source_id=thread_id,
                                            reply_sent=False)
                                
                                db_functions.update_request_status(status='processed',
                                                                thread_id=thread_id)
                    
        print('waiting')
        time.sleep(5)






