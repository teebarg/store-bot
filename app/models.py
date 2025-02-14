from typing import List
from pydantic import BaseModel


# Generic message
class Message(BaseModel):
    message: str

class Question(BaseModel):
    query: str

class Answer(BaseModel):
    answer: str

class FAQItem(BaseModel):
    question: str
    answer: str

class ChatbotResponse(BaseModel):
    answer: str
    relevant_faqs: List[FAQItem]
