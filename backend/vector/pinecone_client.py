from pinecone import Pinecone
import requests
import os
from dotenv import load_dotenv
load_dotenv()


pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index = pc.Index(os.getenv("PINECONE_INDEX"))
print("PINECONE_API_KEY =", os.getenv("PINECONE_API_KEY"))


def embed(text: str):
    r = requests.post(
        os.getenv("OLLAMA_BASE_URL") + "/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text}
    )
    return r.json()["embedding"]

def search(query: str, filters: dict | None = None):
    vec = embed(query)

    if filters:
        res = index.query(
            vector=vec,
            top_k=5,
            include_metadata=True,
            filter=filters
        )
    else:
        res = index.query(
            vector=vec,
            top_k=5,
            include_metadata=True,
            include_values=False
        )

    return res["matches"]
