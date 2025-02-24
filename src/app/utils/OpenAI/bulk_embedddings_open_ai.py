import psycopg2
import asyncio
import time
import os


from src.app.utils.OpenAI import api_functions

# Database Connection
conn = psycopg2.connect(
        dbname=os.getenv("VECTOR_DATABSE"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        host=os.getenv("DATABSE_HOST"),  # Change if your database is hosted remotely
        port=os.getenv("DATABSE_PORT")
    )
cur = conn.cursor()

dbname = 'products'

for i in range(7000):

    cur.execute(f"SELECT product_id, product_category_l1, product_category_l2, product_category_l3, sku_description FROM {dbname} WHERE embedding IS NULL LIMIT 1000;")
    rows = cur.fetchall()


    array_of_input = []
    array_of_id = []
    for row in rows:
        product_id = row[0]
        text_to_embed = f"Category: {row[1]} > {row[2]} > {row[3]} \nDescription: {row[4]}"
        array_of_input.append(text_to_embed)
        array_of_id.append(product_id)

    embeddings = asyncio.run(api_functions.batch_embed_texts(texts=array_of_input))


    for product_id, emb in zip(array_of_id, embeddings):
        # emb is a list of 1536 floats
        sql = """
            UPDATE products
            SET embedding = %s::float8[]::vector(1536)
            WHERE product_id = %s
        """
        cur.execute(sql, (emb, product_id))

        conn.commit()

    counter = (i * 1000) + 1000

    print(counter)
    time.sleep(10)                                                 