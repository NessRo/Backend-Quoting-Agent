import psycopg2
from dotenv import load_dotenv
import os
import json


load_dotenv()


def vector_search(embedding):

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname=os.getenv("VECTOR_DATABSE"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        host=os.getenv("DATABSE_HOST"),  # Change if your database is hosted remotely
        port=os.getenv("DATABSE_PORT")
    )
    cur = conn.cursor()

    sql = f"""
    SELECT product_id, sku_description, embedding <=> '{embedding}' AS similarity
    FROM products
    ORDER BY similarity ASC
    LIMIT 5;
    """

    cur.execute(sql)
    results = cur.fetchall()

    cur.close()
    conn.close()

    return results

def store_request(request_type: str,
                  status: str, 
                  source: str,
                  source_id: str,
                  reply_sent: bool,
                  comments: str):

    """
    Inserts a new record into the transactions.requests table.
    
    Parameters:
    - request_type (str): Type of request.
    - source (str): User who created the request.
    - status (str): indicates the state of the request
    - source_id (str): id of the source

    """

    conn = psycopg2.connect(
        dbname=os.getenv("APPLICATION_DATABASE"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        host=os.getenv("DATABSE_HOST"),  # Change if your database is hosted remotely
        port=os.getenv("DATABSE_PORT")
    )
    cur = conn.cursor()

    sql = """
    INSERT INTO transactions.requests (request_type, status, source, source_id,reply_sent, comments)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT ON CONSTRAINT requests_source_id_key
        DO UPDATE
        SET request_type = EXCLUDED.request_type,
            status      = EXCLUDED.status,
            reply_sent = EXCLUDED.reply_sent,
            comments = EXCLUDED.comments;

    """

    cur.execute(sql, (request_type, status, source, source_id,reply_sent,comments))

    conn.commit()

    cur.close()
    conn.close()

def store_email(sender :str,
                
                subject: str,
                body: any,
                provider: str,
                thread_id: str,
                msg_id: str,
                status: str,
                message_id_rfc822: str,
                in_reply_to_rfc822: str,
                references_rfc822: str,
                email_type:str,
                participants: list):
    
    conn = psycopg2.connect(
        dbname=os.getenv("APPLICATION_DATABASE"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        host=os.getenv("DATABSE_HOST"), 
        port=os.getenv("DATABSE_PORT")
    )
    cur = conn.cursor()

    sql = """
    INSERT INTO transactions.emails (sender, subject, body,provider,thread_id,msg_id,status,message_id_rfc822,in_reply_to_rfc822,references_rfc822,email_type,participants)
    VALUES (%s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s, %s);
    """

    cur.execute(sql, (sender, subject, body,provider,thread_id,msg_id, status,message_id_rfc822,in_reply_to_rfc822,references_rfc822,email_type,participants))

    conn.commit()

    cur.close()
    conn.close()


#functions for transacting agaisnt the source of the requests
def retrieve_request(retrieval_type:str):
    
    conn = psycopg2.connect(
        dbname=os.getenv("APPLICATION_DATABASE"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        host=os.getenv("DATABSE_HOST"), 
        port=os.getenv("DATABSE_PORT")
    )
    cur = conn.cursor()

    match retrieval_type:

        case "new_emails":

            sql = """
            WITH new_emails AS (
            SELECT thread_id
                FROM transactions.emails
                WHERE status = 'new' and email_type = 'inbound'
                GROUP BY thread_id
                LIMIT 10
            ),

            numbered_rows AS (
                SELECT
                    thread_id,
                    body,
                    subject,
                    ROW_NUMBER() OVER (PARTITION BY thread_id ORDER BY timestamp) AS rn,
                    FIRST_VALUE(subject) OVER (PARTITION BY thread_id ORDER BY timestamp) AS earliest_subject
                FROM transactions.emails
            ),

            email_history as (
                SELECT numbered_rows.thread_id,
                        MAX(earliest_subject) AS subject,
                        jsonb_object_agg(
                            CONCAT('msg', rn),
                            body
                        ORDER BY rn ) AS message_history
                FROM numbered_rows
                INNER JOIN new_emails ON new_emails.thread_id = numbered_rows.thread_id
                GROUP BY numbered_rows.thread_id
                
            )
            select *
            from email_history;
            """

        case "replies-refine-other":

            sql = """
            WITH new_replies AS (
            SELECT source_id
                FROM transactions.requests
                WHERE reply_sent = false AND status = 'refine_requirements'
                GROUP BY source_id
                LIMIT 10
            ),

            numbered_rows AS (
                SELECT
                    thread_id,
                    body,
                    subject,
					message_id_rfc822,
					in_reply_to_rfc822,
					CASE WHEN email_type = 'outbound' THEN 'Assistant_response' ELSE 'User_response' END AS role,
                    ROW_NUMBER() OVER (PARTITION BY thread_id ORDER BY timestamp) AS rn,
                    FIRST_VALUE(subject) 
				      OVER (
				        PARTITION BY thread_id 
				        ORDER BY timestamp 
				        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
				      ) AS earliest_subject,
				    LAST_VALUE(message_id_rfc822) 
				      OVER (
				        PARTITION BY thread_id 
				        ORDER BY timestamp 
				        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
				      ) AS latest_msg,
				    LAST_VALUE(in_reply_to_rfc822) 
				      OVER (
				        PARTITION BY thread_id 
				        ORDER BY timestamp 
				        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
				      ) AS latest_reply_to,
					LAST_VALUE(participants) 
				      OVER (
				        PARTITION BY thread_id 
				        ORDER BY timestamp 
				        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
				      ) AS latest_participants
                FROM transactions.emails
            ),

            email_history as (
                SELECT numbered_rows.thread_id,
                       MAX(earliest_subject) AS subject,
                        jsonb_object_agg(
                            CONCAT(role, rn),
                            body
                        ORDER BY rn ) AS message_history,
						MAX(latest_msg) AS latest_msg,
						MAX(latest_reply_to) AS latest_reply_to,
						MAX(latest_participants) AS latest_participants
                FROM numbered_rows
                INNER JOIN new_replies ON new_replies.source_id = numbered_rows.thread_id
                GROUP BY numbered_rows.thread_id
                
            )
            select *
            from email_history;
            """

        case "ready-for-quote":

            sql = """
            WITH quote_requests AS (
            SELECT source_id
                FROM transactions.requests
                WHERE reply_sent = false AND status = 'ready_for_quote'
                GROUP BY source_id
                LIMIT 10
            ),

            numbered_rows AS (
                SELECT
                    thread_id,
                    body,
                    subject,
					message_id_rfc822,
					in_reply_to_rfc822,
					CASE WHEN email_type = 'outbound' THEN 'Assistant_response' ELSE 'User_response' END AS role,
                    ROW_NUMBER() OVER (PARTITION BY thread_id ORDER BY timestamp) AS rn,
                    FIRST_VALUE(subject) 
				      OVER (
				        PARTITION BY thread_id 
				        ORDER BY timestamp 
				        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
				      ) AS earliest_subject,
				    LAST_VALUE(message_id_rfc822) 
				      OVER (
				        PARTITION BY thread_id 
				        ORDER BY timestamp 
				        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
				      ) AS latest_msg,
				    LAST_VALUE(in_reply_to_rfc822) 
				      OVER (
				        PARTITION BY thread_id 
				        ORDER BY timestamp 
				        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
				      ) AS latest_reply_to,
					LAST_VALUE(participants) 
				      OVER (
				        PARTITION BY thread_id 
				        ORDER BY timestamp 
				        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
				      ) AS latest_participants
                FROM transactions.emails
            ),

            email_history as (
                SELECT numbered_rows.thread_id,
                       MAX(earliest_subject) AS subject,
                        jsonb_object_agg(
                            CONCAT(role, rn),
                            body
                        ORDER BY rn ) AS message_history,
						MAX(latest_msg) AS latest_msg,
						MAX(latest_reply_to) AS latest_reply_to,
						MAX(latest_participants) AS latest_participants
                FROM numbered_rows
                INNER JOIN quote_requests ON quote_requests.source_id = numbered_rows.thread_id
                GROUP BY numbered_rows.thread_id
                
            )
            select *
            from email_history;
            """


    cur.execute(sql)
    results = cur.fetchall()

    conn.commit()

    cur.close()
    conn.close()

    return results

def update_request_status(status: str,
                          thread_id: str,
                          update_type: str):
    
    match update_type:

        case 'email_status':
    
            conn = psycopg2.connect(
                dbname=os.getenv("APPLICATION_DATABASE"),
                user=os.getenv("DATABASE_USER"),
                password=os.getenv("DATABASE_PASSWORD"),
                host=os.getenv("DATABSE_HOST"), 
                port=os.getenv("DATABSE_PORT")
            )
            cur = conn.cursor()

            sql = """
            UPDATE transactions.emails
            SET status = %s
            WHERE thread_id = %s;
            """

            cur.execute(sql, (status,thread_id))

            conn.commit()

            cur.close()
            conn.close()

        case 'request_reply_status':
            conn = psycopg2.connect(
                dbname=os.getenv("APPLICATION_DATABASE"),
                user=os.getenv("DATABASE_USER"),
                password=os.getenv("DATABASE_PASSWORD"),
                host=os.getenv("DATABSE_HOST"), 
                port=os.getenv("DATABSE_PORT")
            )
            cur = conn.cursor()

            sql = """
            UPDATE transactions.requests
            SET reply_sent = %s
            WHERE source_id = %s;
            """

            cur.execute(sql, (status,thread_id))

            conn.commit()

            cur.close()
            conn.close()



#functions related to model context
def retrieve_model_context(context_type: str):
    conn = psycopg2.connect(
        dbname=os.getenv("MASTER_DATABASE"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        host=os.getenv("DATABSE_HOST"), 
        port=os.getenv("DATABSE_PORT")
    )
    cur = conn.cursor()

    sql = """
        SELECT context_value
        FROM public.model_context
        WHERE context_type = %s
    """

    cur.execute(sql, (context_type,))
    results = cur.fetchall()

    conn.commit()

    cur.close()
    conn.close()

    return results[0][0]

if __name__ == "__main__":
    response = retrieve_model_context(context_type="request_handler")
    print(response)


