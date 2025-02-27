# backend/app/routes/chat.py
from fastapi import APIRouter, Depends, HTTPException, Body
import os
from datetime import datetime
import uuid

from ..schemas import ChatSession, ChatMessage
from ..database import get_chat_collection, get_document_collection
from ..auth import get_current_user
from ...ai.crew import DoctorAssistantCrew
from ...ai.embeddings import semantic_search

router = APIRouter()

@router.post("/sessions")
async def create_chat_session(
    patient_id: str = Body(...),
    current_user = Depends(get_current_user)
):
    """
    Create a new chat session for doctor-patient interaction
    """
    # Ensure the user is a doctor
    if current_user.get("role") != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can create chat sessions")
    
    # Create a new session
    session_id = str(uuid.uuid4())
    session = ChatSession(
        id=session_id,
        doctor_id=current_user.get("id"),
        patient_id=patient_id,
        messages=[],
        related_documents=[]
    )
    
    # Save to database
    chat_collection = await get_chat_collection()
    await chat_collection.insert_one(session.dict(by_alias=True))
    
    return {
        "message": "Chat session created",
        "session_id": session_id
    }

@router.get("/sessions/{doctor_id}")
async def get_doctor_sessions(
    doctor_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get all chat sessions for a specific doctor
    """
    # Ensure the user is accessing their own sessions
    if current_user.get("id") != doctor_id and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    chat_collection = await get_chat_collection()
    sessions = await chat_collection.find({"doctor_id": doctor_id}).to_list(length=100)
    
    return {
        "doctor_id": doctor_id,
        "session_count": len(sessions),
        "sessions": sessions
    }

@router.get("/session/{session_id}")
async def get_chat_session(
    session_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get a specific chat session
    """
    chat_collection = await get_chat_collection()
    session = await chat_collection.find_one({"_id": session_id})
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Ensure the user has access to this session
    if current_user.get("id") != session.get("doctor_id") and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    return session

@router.post("/session/{session_id}/message")
async def send_message(
    session_id: str,
    content: str = Body(...),
    current_user = Depends(get_current_user)
):
    """
    Send a message in a chat session and get AI response
    """
    # Get the session
    chat_collection = await get_chat_collection()
    session = await chat_collection.find_one({"_id": session_id})
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Ensure the user has access to this session
    if current_user.get("id") != session.get("doctor_id") and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    # Add user message
    user_message = ChatMessage(
        role="user",
        content=content,
        timestamp=datetime.now()
    )
    
    # Get patient information and context
    doc_collection = await get_document_collection()
    patient_documents = await doc_collection.find(
        {"metadata.patient_id": session.get("patient_id")}
    ).to_list(length=100)
    
    # Perform semantic search to get relevant context
    search_results = semantic_search(
        query=content,
        patient_id=session.get("patient_id"),
        k=3
    )
    
    # Format context for the AI
    context = "\n\n".join([
        f"Document: {result['metadata'].get('document_type', 'Unknown')} - {result['metadata'].get('date', 'Unknown date')}\n" +
        f"Content: {result['content']}"
        for result in search_results
    ])
    
    # Initialize the AI assistant
    assistant_crew = DoctorAssistantCrew(os.getenv("OPENAI_API_KEY"))
    
    # Get AI response
    try:
        ai_response = assistant_crew.answer_query(
            query=content,
            patient_id=session.get("patient_id"),
            doctor_id=session.get("doctor_id")
        )
        
        # Create assistant message
        assistant_message = ChatMessage(
            role="assistant",
            content=ai_response,
            timestamp=datetime.now()
        )
        
        # Update session with both messages
        await chat_collection.update_one(
            {"_id": session_id},
            {
                "$push": {
                    "messages": {
                        "$each": [user_message.dict(), assistant_message.dict()]
                    }
                },
                "$set": {
                    "updated_at": datetime.now()
                }
            }
        )
        
        return {
            "user_message": user_message.dict(),
            "assistant_message": assistant_message.dict()
        }
    
    except Exception as e:
        # If AI fails, still save the user message
        await chat_collection.update_one(
            {"_id": session_id},
            {
                "$push": {
                    "messages": user_message.dict()
                },
                "$set": {
                    "updated_at": datetime.now()
                }
            }
        )
        
        return {
            "user_message": user_message.dict(),
            "error": str(e)
        }