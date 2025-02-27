# backend/ai/agents/document_processor.py
from langchain.tools import Tool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import os

class DocumentClassifier:
    """Tool for classifying medical documents"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        
        self.classification_prompt = PromptTemplate(
            input_variables=["document_text"],
            template="""
            You are a medical document classification expert. Analyze the following document text and classify it into one of these categories:
            - Blood Test Report
            - Radiology Report (X-ray, MRI, CT scan, etc.)
            - Doctor's Note / Progress Note
            - Prescription
            - Medical History
            - Discharge Summary
            - Pathology Report
            - Surgical Report
            - Immunization Record
            - Other (specify)
            
            For the classified document type, extract any relevant identifiers or dates.
            
            Document Text:
            {document_text}
            
            Classification:
            """
        )
        
        self.classification_chain = LLMChain(
            llm=self.llm,
            prompt=self.classification_prompt
        )
    
    def classify_document(self, document_text):
        """
        Classify a medical document based on its content
        
        Args:
            document_text (str): The text content of the document
            
        Returns:
            dict: Classification results with confidence scores
        """
        classification = self.classification_chain.run(document_text=document_text[:4000])  # Limit to first 4000 chars
        
        # Extract document type and any identifiers
        # This is a simple implementation - in a real system you'd want to parse the response more carefully
        return {
            "result": classification.strip(),
            "confidence": 0.85  # Placeholder for a real confidence score
        }
        
    def get_tool(self):
        return Tool(
            name="DocumentClassifier",
            func=self.classify_document,
            description="Classifies medical documents by type (blood test, radiology, etc.)"
        )