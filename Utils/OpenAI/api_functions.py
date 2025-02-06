from openai import AsyncOpenAI
import os
import asyncio
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Access the environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(api_key=openai_api_key)


async def get_embedding(text):
    """Send a single request to OpenAI for embedding."""
    response = await client.embeddings.create( 
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding  # Extract embedding

async def batch_embed_texts(texts):
    """Send multiple embedding requests in parallel."""
    tasks = [get_embedding(text) for text in texts]  # Create async tasks
    embeddings = await asyncio.gather(*tasks)  # Run tasks concurrently
    return embeddings


def structure_embedding_postgres(embeddings):
    embedding_str = [f"[{', '.join(map(str, vec))}]" for vec in embeddings]
    return embedding_str