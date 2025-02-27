# backend/ai/embeddings.py
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
import os
import json
from typing import List, Dict, Any

# Initialize embeddings model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

def create_document_embeddings(document_id: str, text_content: str, metadata: Dict[str, Any]):
    """
    Create and store vector embeddings for a document
    
    Args:
        document_id (str): The document ID
        text_content (str): The text content of the document
        metadata (dict): Document metadata
        
    Returns:
        str: Path to the saved vector store
    """
    # Create a text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    # Split text into chunks
    texts = text_splitter.split_text(text_content)
    
    # Add metadata to each chunk
    metadatas = [metadata.copy() for _ in range(len(texts))]
    for i, meta in enumerate(metadatas):
        meta["chunk"] = i
        meta["document_id"] = document_id
    
    # Create a vector store
    vectorstore = FAISS.from_texts(texts=texts, embedding=embeddings, metadatas=metadatas)
    
    # Save the vector store
    storage_path = f"./storage/vectors/{document_id}"
    os.makedirs(os.path.dirname(storage_path), exist_ok=True)
    vectorstore.save_local(storage_path)
    
    return storage_path

def get_vectorstore(patient_id=None, document_id=None):
    """
    Retrieve a vector store for patient documents or a specific document
    
    Args:
        patient_id (str, optional): Patient ID to get all their documents
        document_id (str, optional): Specific document ID
        
    Returns:
        FAISS: Vector store for semantic search
    """
    if document_id:
        # Load a specific document vector store
        storage_path = f"./storage/vectors/{document_id}"
        if os.path.exists(storage_path):
            return FAISS.load_local(storage_path, embeddings)
    
    elif patient_id:
        # Find all document vector stores for a patient and merge them
        # In a real implementation, you would query the database to find all documents
        # associated with the patient
        
        # For demonstration, we'll return a dummy vector store
        try:
            combined_docs = []
            combined_vectors = []
            
            # Get all vector stores for the patient
            document_paths = [f for f in os.listdir("./storage/vectors") if f.startswith(f"patient_{patient_id}_")]
            
            if not document_paths:
                # If no documents found, create a dummy vector store
                return FAISS.from_texts(
                    texts=["No patient records found"], 
                    embedding=embeddings, 
                    metadatas=[{"patient_id": patient_id}]
                )
            
            # Load and merge vector stores
            for doc_path in document_paths:
                vs = FAISS.load_local(f"./storage/vectors/{doc_path}", embeddings)
                # Merge logic here
                
            return FAISS.from_texts(
                texts=["Sample patient record"], 
                embedding=embeddings,
                metadatas=[{"patient_id": patient_id}]
            )
        except Exception as e:
            # If something goes wrong, return an empty vector store
            return FAISS.from_texts(
                texts=["Error retrieving patient records"], 
                embedding=embeddings,
                metadatas=[{"error": str(e)}]
            )
    
    # Default empty vector store
    return FAISS.from_texts(
        texts=["No records found"], 
        embedding=embeddings,
        metadatas=[{}]
    )

def semantic_search(query: str, patient_id=None, document_id=None, k=5):
    """
    Perform semantic search on document vector stores
    
    Args:
        query (str): The search query
        patient_id (str, optional): Patient ID to search within their documents
        document_id (str, optional): Specific document ID to search
        k (int): Number of results to return
        
    Returns:
        list: Relevant document chunks with metadata
    """
    # Get the appropriate vector store
    vectorstore = get_vectorstore(patient_id, document_id)
    
    # Perform the search
    results = vectorstore.similarity_search_with_score(query, k=k)
    
    # Format the results
    formatted_results = []
    for doc, score in results:
        formatted_results.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "relevance_score": float(score)
        })
    
    return formatted_results