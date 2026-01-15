import os
import sys
import uuid

# -------------------------------
# Fix import path (no __init__.py needed)
# -------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, BACKEND_DIR)

# -------------------------------
# Imports
# -------------------------------
from vector.pinecone_client import embed, index
from graph.neo4j_client import Neo4jClient

# -------------------------------
# Paths
# -------------------------------
DOCS_PATH = os.path.join(BACKEND_DIR, "data", "documents")

# -------------------------------
# Config
# -------------------------------
CHUNK_SIZE = 50
CHUNK_OVERLAP = 25

# -------------------------------
# Chunking
# -------------------------------
def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    words = text.split()
    chunks = []
    i = 0

    while i < len(words):
        chunk = " ".join(words[i:i + size])
        chunks.append(chunk)
        i += size - overlap

    return chunks

# -------------------------------
# Ingestion
# -------------------------------
def ingest_all_documents():
    vectors = []
    graph = Neo4jClient()

    for filename in os.listdir(DOCS_PATH):
        if not filename.lower().endswith(".txt"):
            continue

        file_path = os.path.join(DOCS_PATH, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text)

        policy_type = filename.replace(".txt", "")

        print(f"📄 {filename} → {len(chunks)} chunks")

        # Create document node in Neo4j
        graph.create_document_node(
            policy_type=policy_type,
            filename=filename
        )

        for chunk in chunks:
            vectors.append({
                "id": str(uuid.uuid4()),
                "values": embed(chunk),
                "metadata": {
                    "source_file": filename,
                    "policy_type": policy_type,
                    "text": chunk
                }
            })

    print(f"🚀 Uploading {len(vectors)} chunks to Pinecone...")
    index.upsert(vectors=vectors)

    print("✅ Ingestion complete!")

# -------------------------------
# Entry
# -------------------------------
if __name__ == "__main__":
    ingest_all_documents()
