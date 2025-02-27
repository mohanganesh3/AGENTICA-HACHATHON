# backend/app/schemas.py
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    full_name: str
    role: str  # "doctor", "admin", "staff"
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class DocumentMetadata(BaseModel):
    document_type: str  # "blood_report", "radiology", "prescription", etc.
    patient_id: str
    patient_name: str
    doctor_name: Optional[str] = None
    date_of_report: Optional[datetime] = None
    medical_values: Dict[str, Any] = {}  # Extracted medical values
    summary: Optional[str] = None

class Document(BaseModel):
    id: Optional[str] = None
    filename: str
    file_path: str
    upload_date: datetime = Field(default_factory=datetime.now)
    metadata: DocumentMetadata
    processed: bool = False
    tags: List[str] = []
    
    class Config:
        populate_by_name = True

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ChatSession(BaseModel):
    id: Optional[str] = None
    doctor_id: str
    patient_id: str
    messages: List[ChatMessage] = []
    related_documents: List[str] = []  # Document IDs
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True