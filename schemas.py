"""
Data schemas and type definitions for Resume Analyzer
Contains all Pydantic models and TypedDict definitions
"""

from typing import TypedDict
from pydantic import BaseModel, Field


class Analyzer(TypedDict):
    """Main state object for the resume analysis workflow"""
    text: str
    user_id: str
    formatting: str
    clarity: str
    skills: str
    score: float
    suggested_fixes: str
    pdf_path: str
    feedback: str
    justification: str


class StructuredScore(BaseModel):
    """Structured output for resume scoring"""
    score: float = Field(..., ge=0, le=10, description="Resume score from 0 to 10")
    justification: str = Field(..., description="Explanation for the score")
    key_fixes_required: str = Field(..., description="The suggestions used to fix the resume")


class MemoryText(BaseModel):
    """Individual memory item"""
    text: str = Field(description='Atomic details about the user')
    is_there: bool = Field(description='Whether the user detail is present or not')


class MemoryOutput(BaseModel):
    """Output structure for memory operations"""
    should_write: bool = Field(description='Whether there is relevant text to store')
    memories: list[MemoryText] = Field(default_factory=list, description='List of memory items')