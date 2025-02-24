import time
from src.app.utils.database import db_functions
from src.app.utils.model_api_requests import post_requests

types_of_requests = ['quote_request','other']


while True:
        
        print('polling')
        
        requests_ = db_functions.retrieve_request()
        
        if requests_:

            for request in requests_:
    
                thread_id = request[0]
                msg_id = request[1]
                subject = request[2]
                body = request[3]
                prompt = f'subject: {subject} n\
                            body: {body}'


                response = post_requests.generate_unstructured_classification(prompt=prompt)

                if response['classification'] in types_of_requests:

                    db_functions.store_request(request_type=response['classification'],
                                            status='new',
                                            source='email',
                                            source_id=thread_id)

                    db_functions.update_request_status(status='processed',
                                                    thread_id=thread_id)
        print('waiting')
        time.sleep(5)






