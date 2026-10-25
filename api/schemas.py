from typing import Optional

from pydantic import BaseModel, Field


class ConversationTurn(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    answer: str = Field(min_length=1, max_length=3000)


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    history: list[ConversationTurn] = Field(default_factory=list, max_length=3)


class Evidence(BaseModel):
    citation_id: int
    source: str
    page: Optional[int]
    text: str


class QuestionResponse(BaseModel):
    answer: str
    sources: list[str]
    evidence: list[Evidence]
    evidence_match: str
