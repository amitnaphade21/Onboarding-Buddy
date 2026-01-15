import pytest
import requests
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from rag.orchestrator import answer_question
from graph.neo4j_client import Neo4jClient
from vector.pinecone_client import embed, search

# =====================================
# Setup
# =====================================
client = TestClient(app)

# =====================================
# TEST 1: Health Check
# =====================================
def test_health_check():
    """Test that the API health endpoint works"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    print("✅ TEST 1 PASSED: Health check working")

# =====================================
# TEST 2: List Users by Role - Intern
# =====================================
@patch('api.users.Neo4jClient.list_people_by_role')
def test_list_by_role_intern(mock_list):
    """Test listing intern users"""
    mock_list.return_value = [
        {"id": "EMP001", "name": "John Doe"},
        {"id": "EMP002", "name": "Jane Smith"}
    ]
    
    response = client.get("/list_by_role?role=intern")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["items"][0]["id"] == "EMP001"
    print("✅ TEST 2 PASSED: List intern users")

# =====================================
# TEST 3: List Users by Role - Full Time
# =====================================
@patch('api.users.Neo4jClient.list_people_by_role')
def test_list_by_role_fulltime(mock_list):
    """Test listing full-time users"""
    mock_list.return_value = [
        {"id": "EMP003", "name": "Alice Johnson"},
        {"id": "EMP004", "name": "Bob Wilson"}
    ]
    
    response = client.get("/list_by_role?role=full_time")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["items"][0]["name"] == "Alice Johnson"
    print("✅ TEST 3 PASSED: List full-time users")

# =====================================
# TEST 4: Chat Endpoint - Valid Request
# =====================================
@patch('api.chat.answer_question')
def test_chat_valid_request(mock_answer):
    """Test chat endpoint with valid request"""
    mock_answer.return_value = ("You get 20 days of leave as a full-time employee.", None)
    
    response = client.post("/chat", json={
        "user_id": "EMP001",
        "question": "How many leave days do I get?",
        "debug": False
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "leave" in data["answer"].lower()
    print("✅ TEST 4 PASSED: Chat with valid request")

# =====================================
# TEST 5: Chat Endpoint - With Debug
# =====================================
@patch('api.chat.answer_question')
def test_chat_with_debug(mock_answer):
    """Test chat endpoint with debug enabled"""
    mock_context = ["Policy chunk 1", "Policy chunk 2"]
    mock_answer.return_value = ("Sample answer", mock_context)
    
    response = client.post("/chat", json={
        "user_id": "EMP001",
        "question": "What is the leave policy?",
        "debug": True
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "context" in data
    assert len(data["context"]) == 2
    print("✅ TEST 5 PASSED: Chat with debug mode")

# =====================================
# TEST 6: Chat Endpoint - Missing Fields
# =====================================
def test_chat_missing_user_id():
    """Test chat endpoint with missing user_id"""
    response = client.post("/chat", json={
        "question": "What is the leave policy?"
    })
    
    assert response.status_code == 422  # Validation error
    print("✅ TEST 6 PASSED: Missing user_id validation")

# =====================================
# TEST 7: Chat Endpoint - Missing Question
# =====================================
def test_chat_missing_question():
    """Test chat endpoint with missing question"""
    response = client.post("/chat", json={
        "user_id": "EMP001"
    })
    
    assert response.status_code == 422  # Validation error
    print("✅ TEST 7 PASSED: Missing question validation")

# =====================================
# TEST 8: Get User Context
# =====================================
@patch('graph.neo4j_client.GraphDatabase.driver')
def test_get_user_context(mock_driver):
    """Test retrieving user context from Neo4j"""
    mock_session = MagicMock()
    mock_driver.return_value.session.return_value.__enter__.return_value = mock_session
    
    mock_record = MagicMock()
    mock_record.__getitem__.side_effect = lambda x: {
        "name": "John Doe",
        "employment_type": "full_time",
        "department": "Engineering",
        "manager": "Alice Manager",
        "mentor": "Bob Mentor",
        "college": "MIT"
    }[x]
    mock_session.run.return_value.single.return_value = mock_record
    
    graph = Neo4jClient()
    user = graph.get_user_context("EMP001")
    
    assert user is not None
    assert user["name"] == "John Doe"
    print("✅ TEST 8 PASSED: Get user context")

# =====================================
# TEST 9: Answer Question - User Found
# =====================================
@patch('rag.orchestrator.graph.get_user_context')
@patch('rag.orchestrator.search')
@patch('rag.orchestrator.ask_llm')
def test_answer_question_success(mock_llm, mock_search, mock_user):
    """Test successful question answering"""
    mock_user.return_value = {
        "name": "John Doe",
        "employment_type": "full_time",
        "department": "Engineering",
        "manager": "Alice",
        "mentor": "Bob",
        "college": "MIT"
    }
    
    mock_search.return_value = [
        {
            "metadata": {
                "text": "Full-time employees get 20 days of leave per year."
            }
        }
    ]
    
    mock_llm.return_value = "You get 20 days of leave as a full-time employee."
    
    answer, context = answer_question("EMP001", "How many leave days?", debug=False)
    
    assert "20 days" in answer
    assert context is None  # Debug is False
    print("✅ TEST 9 PASSED: Answer question successfully")

# =====================================
# TEST 10: Answer Question - User Not Found
# =====================================
@patch('rag.orchestrator.graph.get_user_context')
def test_answer_question_user_not_found(mock_user):
    """Test when user is not found"""
    mock_user.return_value = None
    
    answer, context = answer_question("INVALID_ID", "How many leave days?", debug=False)
    
    assert answer == "User not found."
    assert context is None
    print("✅ TEST 10 PASSED: Handle user not found")

# =====================================
# TEST 11: Embed Function
# =====================================
@patch('vector.pinecone_client.requests.post')
def test_embed_function(mock_post):
    """Test text embedding"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
    }
    mock_post.return_value = mock_response
    
    embedding = embed("Test text")
    
    assert len(embedding) == 5
    assert embedding[0] == 0.1
    print("✅ TEST 11 PASSED: Embed function")

# =====================================
# TEST 12: Search Function
# =====================================
@patch('vector.pinecone_client.embed')
@patch('vector.pinecone_client.index.query')
def test_search_function(mock_query, mock_embed_func):
    """Test vector search"""
    mock_embed_func.return_value = [0.1, 0.2, 0.3]
    
    mock_query.return_value = {
        "matches": [
            {
                "id": "chunk1",
                "metadata": {"text": "Leave policy text", "source_file": "leave-policy.txt"}
            },
            {
                "id": "chunk2",
                "metadata": {"text": "Another policy text", "source_file": "coc-policy.txt"}
            }
        ]
    }
    
    results = search("What is the leave policy?")
    
    assert len(results) == 2
    assert results[0]["metadata"]["source_file"] == "leave-policy.txt"
    print("✅ TEST 12 PASSED: Search function")

# =====================================
# TEST 13: Answer With Debug Context
# =====================================
@patch('rag.orchestrator.graph.get_user_context')
@patch('rag.orchestrator.search')
@patch('rag.orchestrator.ask_llm')
def test_answer_with_debug_context(mock_llm, mock_search, mock_user):
    """Test question answering with debug context"""
    mock_user.return_value = {
        "name": "Jane Smith",
        "employment_type": "intern",
        "department": "HR",
        "manager": "Charlie",
        "mentor": "Diana",
        "college": "Stanford"
    }
    
    mock_search.return_value = [
        {
            "metadata": {
                "text": "Intern policy chunk 1"
            }
        },
        {
            "metadata": {
                "text": "Intern policy chunk 2"
            }
        }
    ]
    
    mock_llm.return_value = "Interns get 10 days of leave."
    
    answer, context = answer_question("EMP002", "How many leave days as intern?", debug=True)
    
    assert context is not None
    assert len(context) == 2
    assert context[0] == "Intern policy chunk 1"
    print("✅ TEST 13 PASSED: Answer with debug context")

# =====================================
# TEST 14: Invalid Role
# =====================================
@patch('api.users.Neo4jClient.list_people_by_role')
def test_list_by_invalid_role(mock_list):
    """Test listing users with invalid role"""
    mock_list.return_value = []
    
    response = client.get("/list_by_role?role=invalid_role")
    assert response.status_code == 200
    assert response.json()["items"] == []
    print("✅ TEST 14 PASSED: Handle invalid role")

# =====================================
# TEST 15: Chat Response Structure
# =====================================
@patch('api.chat.answer_question')
def test_chat_response_structure(mock_answer):
    """Test that chat response has correct structure"""
    mock_answer.return_value = ("Sample answer text", None)
    
    response = client.post("/chat", json={
        "user_id": "EMP001",
        "question": "Test question?",
        "debug": False
    })
    
    data = response.json()
    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert len(data) == 1  # No context when debug=False
    print("✅ TEST 15 PASSED: Chat response structure correct")

# =====================================
# Run All Tests
# =====================================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("🧪 RUNNING ONBOARDING BUDDY TEST SUITE")
    print("="*50 + "\n")
    
    test_health_check()
    test_list_by_role_intern()
    test_list_by_role_fulltime()
    test_chat_valid_request()
    test_chat_with_debug()
    test_chat_missing_user_id()
    test_chat_missing_question()
    test_get_user_context()
    test_answer_question_success()
    test_answer_question_user_not_found()
    test_embed_function()
    test_search_function()
    test_answer_with_debug_context()
    test_list_by_invalid_role()
    test_chat_response_structure()
    
    print("\n" + "="*50)
    print("✅ ALL 15 TESTS PASSED!")
    print("="*50 + "\n")
