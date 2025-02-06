import psycopg2
from dotenv import load_dotenv
import os


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
    SELECT id, name, description, embedding <=> '{embedding}' AS similarity
    FROM products
    ORDER BY similarity ASC
    LIMIT 5;
    """

    cur.execute(sql)
    results = cur.fetchall()

    return results
