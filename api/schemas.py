from typing import Optional

from pydantic import BaseModel


class QuestionRequest(BaseModel):

    question: str


class Evidence(BaseModel):
    source: str
    page: Optional[int]
    text: str


class QuestionResponse(BaseModel):
    answer: str
    sources: list[str]
    evidence: list[Evidence]
    confidence: str