import time
from src.app.utils.database import db_functions
from src.app.utils.model_api_requests import post_requests
from src.app.email import gmail_functions
from dotenv import load_dotenv
import uuid
import os

load_dotenv()

EMAIL_USER =  os.getenv("EMAIL_USER")


while True:
        
        print('polling')
        
        requests_ = db_functions.retrieve_request(retrieval_type='replies-refine-other')
        
        if requests_:

            for request in requests_:
    
                thread_id = request[0]
                subject = request[1]
                body = request[2]
                latest_msg = request[3]
                latest_participants = request[5]
                prompt = f'respond as the assistant in this conversation exchange, do not address the response to me: {body}'
    

                response = post_requests.generate_llm_response(prompt=prompt,
                                                               request_type='refine_requirement_reply')
                
                msg_id = f"<{uuid.uuid4()}@gmail.com>"
                
                #store the email.
                db_functions.store_email(sender=EMAIL_USER,
                                         subject=subject,
                                         body=response,
                                         provider='gmail',
                                         thread_id=thread_id,
                                         msg_id=None,
                                         status='new',
                                         message_id_rfc822=msg_id,
                                         in_reply_to_rfc822=latest_msg,
                                         references_rfc822=None,
                                         email_type='outbound',
                                         participants= latest_participants )
                
                #send the email.
                gmail_functions.send_reply(to_address=latest_participants,
                                           original_subject=subject,
                                           original_message_id=latest_msg,
                                           reply_body=response,
                                           message_id=msg_id)
                
                #update email status
                db_functions.update_request_status(status='processed',
                                                   thread_id=thread_id,
                                                   update_type='email_status')
                
                #update request status
                db_functions.update_request_status(status='true',
                                                   thread_id=thread_id,
                                                   update_type='request_reply_status')


                print(f'prompt was:{prompt} \n response was: {response}')

        #         if response['classification'] in types_of_requests:

        #             match response['classification']:
        #                 case "quote_request":
        #                         db_functions.store_request(request_type=response['classification'],
        #                                     status='ready_for_quote',
        #                                     source='email',
        #                                     source_id=thread_id,
        #                                     reply_sent=False)
                                
        #                         db_functions.update_request_status(status='processed',
        #                                                         thread_id=thread_id)
        #                 case "other":
        #                         db_functions.store_request(request_type=response['classification'],
        #                                     status='refine_requirements',
        #                                     source='email',
        #                                     source_id=thread_id,
        #                                     reply_sent=False)
                                
        #                         db_functions.update_request_status(status='processed',
        #                                                         thread_id=thread_id)
                    
        print('waiting')
        time.sleep(5)






