from graph.neo4j_client import Neo4jClient
from vector.pinecone_client import search
import requests
import os

graph = Neo4jClient()
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def ask_llm(prompt: str):
    r = requests.post(f"{OLLAMA_URL}/api/generate", json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }, timeout=120)
    return r.json()["response"]

def answer_question(user_id: str, question: str, debug: bool = False):
    user = graph.get_user_context(user_id)
    if not user:
        return "User not found.", None

    # Get documents
    results = search(question)

    docs = "\n\n".join([m["metadata"]["text"] for m in results])

    prompt = f"""
You are GlideCloud's HR assistant.

User role: {user["employment_type"]}
User name: {user["name"]}
Manager: {user.get("manager")}
Mentor: {user.get("mentor")}
Department: {user.get("department")}
College: {user.get("college")}

Answer ONLY from the policy text below:

----------------
{docs}
----------------

Question: {question}
"""

    answer = ask_llm(prompt)

    if debug:
        return answer, [m["metadata"]["text"] for m in results]
    else:
        return answer, None