# backend/app/routes/documents.py
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import shutil
from datetime import datetime
import uuid

from ..schemas import Document, DocumentMetadata
from ..database import get_document_collection
from ..auth import get_current_user
from ...ai.crew import MedicalDocumentCrew
from ...ai.embeddings import create_document_embeddings

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    patient_name: str = Form(...),
    notes: Optional[str] = Form(None),
    current_user = Depends(get_current_user)
):
    """
    Upload a medical document for processing
    """
    # Create storage directory if it doesn't exist
    os.makedirs("./storage/documents", exist_ok=True)
    
    # Generate a unique document ID
    document_id = str(uuid.uuid4())
    
    # Save the file
    file_extension = os.path.splitext(file.filename)[1]
    file_path = f"./storage/documents/{document_id}{file_extension}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Initial metadata
    metadata = DocumentMetadata(
        document_type="unprocessed",
        patient_id=patient_id,
        patient_name=patient_name,
        doctor_name=current_user.get("full_name", "Unknown"),
        date_of_report=datetime.now(),
        medical_values={},
        summary=notes
    )
    
    # Create the document record
    document = Document(
        id=document_id,
        filename=file.filename,
        file_path=file_path,
        upload_date=datetime.now(),
        metadata=metadata,
        processed=False,
        tags=["unprocessed"]
    )
    
    # Save to database
    doc_collection = await get_document_collection()
    await doc_collection.insert_one(document.dict(by_alias=True))
    
    # Process document asynchronously
    # In a production environment, this would be a background task
    # For demonstration, we'll do it synchronously
    
    return JSONResponse(
        status_code=202,
        content={
            "message": "Document uploaded and processing started",
            "document_id": document_id,
            "status": "processing"
        }
    )

@router.get("/{document_id}/process")
async def process_document(
    document_id: str,
    current_user = Depends(get_current_user)
):
    """
    Process a previously uploaded document
    """
    # Get the document from the database
    doc_collection = await get_document_collection()
    document_data = await doc_collection.find_one({"_id": document_id})
    
    if not document_data:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Convert to Document object
    document = Document(**document_data)
    
    # Read the document content
    # In a real implementation, you would use appropriate document loaders
    # based on file type (PDF, DOCX, etc.)
    try:
        with open(document.file_path, "r") as f:
            document_text = f.read()
    except:
        # If we can't read the file directly (e.g., it's a binary format)
        document_text = "Sample document text for processing"
    
    # Initialize the AI crew
    document_crew = MedicalDocumentCrew(os.getenv("OPENAI_API_KEY"))
    
    # Process the document
    result = document_crew.process_document(document_text, document.filename)
    
    # Extract the results
    try:
        # Parse AI crew results
        classification_result = result.get("classification", {})
        extraction_result = result.get("extraction", {})
        compliance_result = result.get("compliance", {})
        
        # Update document metadata
        updated_metadata = DocumentMetadata(
            document_type=classification_result.get("document_type", "unknown"),
            patient_id=document.metadata.patient_id,
            patient_name=document.metadata.patient_name,
            doctor_name=extraction_result.get("doctor_name", document.metadata.doctor_name),
            date_of_report=document.metadata.date_of_report,
            medical_values=extraction_result.get("medical_values", {}),
            summary=extraction_result.get("summary", document.metadata.summary)
        )
        
        # Update tags
        tags = [updated_metadata.document_type]
        if not compliance_result.get("compliant", True):
            tags.append("compliance_issue")
        
        # Create document embeddings for semantic search
        create_document_embeddings(
            document_id=document_id,
            text_content=document_text,
            metadata={
                "document_type": updated_metadata.document_type,
                "patient_id": updated_metadata.patient_id,
                "patient_name": updated_metadata.patient_name,
                "date": updated_metadata.date_of_report.isoformat()
            }
        )
        
        # Update the document in the database
        await doc_collection.update_one(
            {"_id": document_id},
            {
                "$set": {
                    "metadata": updated_metadata.dict(),
                    "processed": True,
                    "tags": tags
                }
            }
        )
        
        return {
            "message": "Document processed successfully",
            "document_id": document_id,
            "document_type": updated_metadata.document_type,
            "tags": tags
        }
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": "Error processing document",
                "error": str(e)
            }
        )

@router.get("/patient/{patient_id}")
async def get_patient_documents(
    patient_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get all documents for a specific patient
    """
    doc_collection = await get_document_collection()
    documents = await doc_collection.find({"metadata.patient_id": patient_id}).to_list(length=100)
    
    return {
        "patient_id": patient_id,
        "document_count": len(documents),
        "documents": documents
    }

@router.get("/{document_id}")
async def get_document(
    document_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get a specific document by ID
    """
    doc_collection = await get_document_collection()
    document = await doc_collection.find_one({"_id": document_id})
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document