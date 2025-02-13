from app.models import ChatbotResponse, Question
from app.utils import SimpleFAQChatbot
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    # generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Initialize chatbot as a global variable
chatbot = None

@app.on_event("startup")
async def startup_event():
    """Initialize chatbot when the app starts"""
    global chatbot
    chatbot = SimpleFAQChatbot()

@app.post("/api/chat", response_model=ChatbotResponse)
async def chat(question: Question):
    """
    Get an answer to a question
    """
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")

    try:
        answer = chatbot.get_faq_answer(question.query)
        return ChatbotResponse(
            answer=answer,
            relevant_faqs=[]
        )
        # answer, relevant_faqs = chatbot.generate_answer(question.query)
        # return ChatbotResponse(
        #     answer=answer,
        #     relevant_faqs=[FAQItem(**faq) for faq in relevant_faqs]
        # )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(api_router, prefix=settings.API_V1_STR)
