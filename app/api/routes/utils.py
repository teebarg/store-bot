from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.utils import generate_answer

router = APIRouter(prefix="/utils", tags=["utils"])

# Define a request model
class QueryRequest(BaseModel):
    query: str


@router.get("/health-check/")
async def health_check() -> bool:
    return True

@router.post("/query")
async def answer_query(request: QueryRequest):
    print(request)
    try:
        response = await generate_answer(request.query)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
