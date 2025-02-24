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
                  source_id: str):

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
    INSERT INTO transactions.requests (request_type, status, source,source_id)
    VALUES (%s, %s, %s, %s);
    """

    cur.execute(sql, (request_type, status, source, source_id))

    conn.commit()

    cur.close()
    conn.close()

def store_email(sender :str,
                subject: str,
                body: any,
                provider: str,
                thread_id: str,
                msg_id: str,
                status: str):
    
    conn = psycopg2.connect(
        dbname=os.getenv("APPLICATION_DATABASE"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        host=os.getenv("DATABSE_HOST"), 
        port=os.getenv("DATABSE_PORT")
    )
    cur = conn.cursor()

    sql = """
    INSERT INTO transactions.emails (sender, subject, body,provider,thread_id,msg_id,status)
    VALUES (%s, %s, %s, %s,%s,%s,%s);
    """

    cur.execute(sql, (sender, subject, body,provider,thread_id,msg_id, status))

    conn.commit()

    cur.close()
    conn.close()


#functions for transacting agaisnt the source of the requests
def retrieve_request():
    
    conn = psycopg2.connect(
        dbname=os.getenv("APPLICATION_DATABASE"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        host=os.getenv("DATABSE_HOST"), 
        port=os.getenv("DATABSE_PORT")
    )
    cur = conn.cursor()

    sql = """
    SELECT thread_id, msg_id, subject, body
    FROM transactions.emails
    WHERE status = 'new'
    LIMIT 10;
    """

    cur.execute(sql)
    results = cur.fetchall()

    conn.commit()

    cur.close()
    conn.close()

    return results

def update_request_status(status: str,
                          thread_id: str):
    
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


