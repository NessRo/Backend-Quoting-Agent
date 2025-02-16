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

def store_request(data,request_type,created_by, status):

    """
    Inserts a new record into the my_schema.requests table.
    
    Parameters:
    - data (dict): JSON-compatible dictionary to store in the data column.
    - request_type (str): Type of request.
    - created_by (str): User who created the request.
    - status (str): indicates the state of the request

    Returns:
    - The inserted record's ID (UUID)
    """

    conn = psycopg2.connect(
        dbname=os.getenv("APPLICATION_DATABSE"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        host=os.getenv("DATABSE_HOST"),  # Change if your database is hosted remotely
        port=os.getenv("DATABSE_PORT")
    )
    cur = conn.cursor()

    data_json = json.dumps(data)

    sql = """
    INSERT INTO transactions.requests (data, request_type, created_by,status)
    VALUES (%s, %s, %s, %s);
    """

    cur.execute(sql, (data_json, request_type, created_by, status))

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
        dbname=os.getenv("APPLICATION_DATABSE"),
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