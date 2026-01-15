from fastapi import APIRouter
from graph.neo4j_client import Neo4jClient

router = APIRouter()
graph = Neo4jClient()

@router.get("/list_by_role")
def list_by_role(role: str):
    data = graph.list_people_by_role(role)
    return {"items": data}
