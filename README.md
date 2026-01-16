# 🤖 Onboarding Buddy - AI HR Assistant

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Prerequisites](#prerequisites)
5. [Installation Guide](#installation-guide)
6. [Environment Setup](#environment-setup)
7. [Running the Application](#running-the-application)
8. [Testing](#testing)
9. [API Documentation](#api-documentation)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

**Onboarding Buddy** is an intelligent HR assistant that helps new employees get quick answers about company policies. It uses:
- **AI/LLM** (Ollama Llama3) for natural language understanding
- **Vector Database** (Pinecone) for semantic policy search
- **Knowledge Graph** (Neo4j) for employee & organizational data
- **RAG System** to retrieve accurate policy information

### Key Benefit
Employees don't need to search through PDFs or contact HR—they ask questions naturally and get instant, accurate policy answers!

---

## ✨ Features

✅ **Role-Based Access** - Separate policies for interns vs full-time employees  
✅ **Semantic Search** - Finds relevant policies even with different wording  
✅ **Personalized Context** - Knows user's name, role, department, manager  
✅ **Debug Mode** - Shows which policy chunks were used to answer  
✅ **Fast Responses** - Local LLM + optimized retrieval  
✅ **Data Privacy** - All data stays on-premises (no cloud dependency)  

---

## 📁 Project Structure

```
Capstone1 (Onboarding Buddy)/
│
├── frontend/
│   └── app.py                    # Streamlit UI
│
├── backend/
│   ├── main.py                   # FastAPI app entry point
│   ├── test.py                   # Unit tests (15 test cases)
│   │
│   ├── api/
│   │   ├── chat.py              # POST /chat endpoint
│   │   └── users.py             # GET /list_by_role endpoint
│   │
│   ├── rag/
│   │   └── orchestrator.py       # RAG pipeline orchestration
│   │
│   ├── graph/
│   │   └── neo4j_client.py       # Neo4j database client
│   │
│   ├── vector/
│   │   └── pinecone_client.py    # Pinecone vector DB client
│   │
│   ├── ingestion/
│   │   └── ingest_docs.py        # Document ingestion script
│   │
│   └── data/
│       ├── documents/            # Policy documents (.txt files)
│       │   ├── coc-policy.txt
│       │   ├── inssurance-policy.txt
│       │   ├── leave-policy.txt
│       │   └── wfh-policy.txt
│       └── graph/
│           └── org_structure     # Org chart data
│
├── requirements.txt              # Python dependencies
├── README.md                      # This file
└── Output_screenshots/            # Demo screenshots
```

---

## 🔧 Prerequisites

Before you start, make sure you have:

### Required Software
- **Python 3.9+** ([Download](https://www.python.org/downloads/))
- **Git** (optional, for cloning)
- **Ollama** (for LLM inference) ([Download](https://ollama.ai/))
- **Neo4j** (Graph Database) ([Download](https://neo4j.com/download/))

### Required Accounts/APIs
- **Pinecone API Key** ([Sign up](https://www.pinecone.io/))

### System Requirements
- RAM: 8GB minimum (16GB recommended)
- Storage: 10GB free space
- Internet: For downloading models initially

---

## 📦 Installation Guide

### Step 1: Install Python Dependencies

Open Command Prompt or PowerShell and run:

```bash
pip install -r requirements.txt
```

This installs:
- `fastapi` - Backend API framework
- `streamlit` - Frontend UI framework
- `neo4j` - Graph database driver
- `pinecone-client` - Vector database client
- `requests` - HTTP library
- `python-dotenv` - Environment variable management
- `uvicorn` - ASGI server
- `pytest` - Testing framework

### Step 2: Install & Setup Ollama

**Download and Install:**
- Visit [ollama.ai](https://ollama.ai/) and download for your OS
- Run the installer and follow prompts

**Pull Required Models:**

```bash
ollama pull llama3
ollama pull nomic-embed-text
```

These models are used for:
- `llama3` - Main language model for generating answers
- `nomic-embed-text` - Embedding model for semantic search

**Verify Ollama is Running:**
```bash
curl http://localhost:11434/api/tags
```

You should see a JSON response with available models.

### Step 3: Install & Setup Neo4j

**Download and Install:**
- Visit [neo4j.com/download](https://neo4j.com/download/)
- Download Neo4j Desktop (easier for local development)
- Install and create a new database

**Start Neo4j:**
- Open Neo4j Desktop
- Click "Start" on your database
- Default credentials: `neo4j` / `password`

**Verify Neo4j Connection:**
```bash
curl -u neo4j:password http://localhost:7687
```

### Step 4: Get Pinecone API Key

1. Go to [pinecone.io](https://www.pinecone.io/)
2. Sign up for free account
3. Create an index named `onboarding-buddy`
4. Get your API key from dashboard

---

## 🔐 Environment Setup

### Create `.env` File

In the project root directory, create a file named `.env` with:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX=onboarding-buddy
```

**Replace:**
- `your_pinecone_api_key_here` - With your actual Pinecone API key

### Verify `.env` is in Right Place

```
Capstone1/
├── .env                 ← Should be here
├── backend/
├── frontend/
├── requirements.txt
└── README.md
```

---

## 🚀 Running the Application

### Option 1: Run Everything (Complete Setup)

**Terminal 1 - Start Ollama:**
```bash
ollama serve
```
(Keep this running in background)

**Terminal 2 - Start Neo4j:**
- Use Neo4j Desktop to start your database
- Or run: `neo4j start`

**Terminal 3 - Start FastAPI Backend:**
```bash
cd backend
uvicorn main:app --reload
```

**Terminal 4 - Ingest Documents (One-time):**
```bash
cd backend
python ingestion/ingest_docs.py
```

**Terminal 5 - Start Streamlit Frontend:**
```bash
cd frontend
streamlit run app.py
```

The UI will open at `http://localhost:8501`

---

### Option 2: Quick Start (Using Batch File)

Create `run.bat` in project root with:

```batch
@echo off
start cmd /k "cd backend && uvicorn main:app --reload"
start cmd /k "cd frontend && streamlit run app.py"
```

Then run:
```bash
run.bat
```

---

## 🧪 Testing

### Run All Tests

```bash
cd backend
python -m pytest test.py -v
```

### Run Specific Test

```bash
python -m pytest test.py::test_health_check -v
```

### Or Run Direct Test Script

```bash
cd backend
python test.py
```

### Test Coverage

The test suite includes **15 test cases** covering:

1. **Health Check** - API is running
2. **List Intern Users** - Fetch intern list
3. **List Full-Time Users** - Fetch full-time list
4. **Chat with Valid Request** - Answer questions
5. **Chat with Debug** - Show retrieved context
6. **Missing User ID** - Input validation
7. **Missing Question** - Input validation
8. **Get User Context** - Neo4j retrieval
9. **Answer Question Success** - Full RAG pipeline
10. **Handle User Not Found** - Error handling
11. **Embed Function** - Text to vector
12. **Search Function** - Vector similarity search
13. **Answer with Debug** - Context retrieval
14. **Invalid Role** - Edge case handling
15. **Response Structure** - API response format

**Expected Output:**
```
==================================================
🧪 RUNNING ONBOARDING BUDDY TEST SUITE
==================================================

✅ TEST 1 PASSED: Health check working
✅ TEST 2 PASSED: List intern users
✅ TEST 3 PASSED: List full-time users
...
==================================================
✅ ALL 15 TESTS PASSED!
==================================================
```

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoint 1: Health Check

**Request:**
```bash
curl http://localhost:8000/
```

**Response:**
```json
{
  "status": "ok"
}
```

---

### Endpoint 2: List Users by Role

**Request:**
```bash
curl "http://localhost:8000/list_by_role?role=intern"
```

**Parameters:**
- `role` (string): `"intern"` or `"full_time"`

**Response:**
```json
{
  "items": [
    {
      "id": "EMP001",
      "name": "John Doe"
    },
    {
      "id": "EMP002",
      "name": "Jane Smith"
    }
  ]
}
```

---

### Endpoint 3: Chat (Ask Question)

**Request:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "EMP001",
    "question": "How many leave days do I get?",
    "debug": false
  }'
```

**Parameters:**
- `user_id` (string): Employee ID
- `question` (string): Question about policies
- `debug` (boolean): Show retrieved context (optional, default: false)

**Response (debug=false):**
```json
{
  "answer": "As a full-time employee, you are entitled to 20 days of leave per year."
}
```

**Response (debug=true):**
```json
{
  "answer": "As a full-time employee, you are entitled to 20 days of leave per year.",
  "context": [
    "Full-time employees get 20 days of annual leave...",
    "Leave policy includes sick leave, vacation days..."
  ]
}
```

---

## 🐛 Troubleshooting

### Issue 1: "Connection refused" on localhost:8000

**Solution:**
```bash
# Make sure FastAPI is running
cd backend
uvicorn main:app --reload
```

### Issue 2: Ollama models not found

**Solution:**
```bash
# Pull required models
ollama pull llama3
ollama pull nomic-embed-text

# Verify
ollama list
```

### Issue 3: Neo4j connection error

**Check Connection:**
```bash
# Test Neo4j port
netstat -an | find "7687"
```

**Start Neo4j (if stopped):**
- Open Neo4j Desktop and click "Start"
- Or run: `neo4j start` (if installed via command line)

### Issue 4: Pinecone API key error

**Solution:**
- Verify `.env` file exists
- Check API key is correct (no spaces, quotes)
- Restart backend: `uvicorn main:app --reload`

### Issue 5: "No users found for this role"

**Check Database:**
- Open Neo4j Browser at `http://localhost:7474`
- Run query:
```cypher
MATCH (e:Employee) RETURN e
```

If no results, you need to load employee data into Neo4j.

### Issue 6: Streamlit not showing anything

**Solution:**
```bash
# Kill all python processes
taskkill /F /IM python.exe

# Start fresh
cd frontend
streamlit run app.py
```

### Issue 7: "Ingestion failed" error

**Check document path:**
```bash
# Verify policy files exist
ls backend/data/documents/
```

Should show:
- `coc-policy.txt`
- `inssurance-policy.txt`
- `leave-policy.txt`
- `wfh-policy.txt`

---

## 📊 Example Workflow

### Step 1: Select Employee
- Open Streamlit UI at `http://localhost:8501`
- Select Role: **Intern**
- Select Person: **John Doe (EMP001)**

### Step 2: Ask Question
```
Type: "How many days of leave do I get as an intern?"
Click: "Ask"
```

### Step 3: View Answer
```
Answer: "As an intern, you are entitled to 10 days of leave 
during your internship period, subject to manager approval."
```

### Step 4: View Context (Optional)
- Check "Show retrieved context (debug)"
- See policy chunks used to answer

---

## 🔄 Data Flow Diagram

```
User Question
    ↓
[Streamlit Frontend] sends user_id + question
    ↓
[FastAPI Backend] receives request
    ↓
[Neo4j] fetches user context (name, role, dept)
    ↓
[Pinecone] searches for relevant policies
    ↓
[Ollama LLM] generates answer from context + policies
    ↓
[FastAPI] returns answer + optional context
    ↓
[Streamlit] displays answer to user
```

---

## 📚 Requirements File

The `requirements.txt` includes:

```
fastapi==0.104.1
uvicorn==0.24.0
streamlit==1.28.1
requests==2.31.0
python-dotenv==1.0.0
neo4j==5.14.0
pinecone-client==3.0.0
pytest==7.4.3
```

All dependencies are automatically installed when you run:
```bash
pip install -r requirements.txt
```

---

## 🚀 Performance Tips

1. **Cache Policy Embeddings** - Pre-embed all policies to avoid repeated embedding
2. **Batch Ingestion** - Process documents in batches for faster indexing
3. **Monitor Ollama Memory** - Reduce model size if RAM is low
4. **Index Optimization** - Configure Pinecone index for your query patterns

---

## 📞 Support

**If you encounter issues:**

1. Check [Troubleshooting](#troubleshooting) section
2. Verify all services are running (Ollama, Neo4j, Pinecone)
3. Check `.env` file is correct
4. Review logs in terminal windows
5. Run tests to isolate the problem:
```bash
cd backend
python test.py
```

---

## 📄 License

This project is part of GlideCloud's onboarding initiative.

---


