from fastapi import APIRouter
from pydantic import BaseModel
from rag.orchestrator import answer_question

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: str
    question: str
    debug: bool = False

@router.post("/chat")
def chat(req: ChatRequest):
    answer, context = answer_question(req.user_id, req.question, debug=req.debug)

    response = {
        "answer": answer
    }

    if req.debug:
        response["context"] = context

    return response