# backend/ai/agents/medical_extractor.py
from langchain.tools import Tool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
import json
import re

class MedicalDataExtractor:
    """Tool for extracting structured data from medical documents"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        
        self.extraction_prompts = {
            "blood_test": PromptTemplate(
                input_variables=["document_text"],
                template="""
                Extract the following information from this Blood Test Report:
                - Patient Name
                - Patient ID/MRN
                - Date of Collection
                - Ordering Physician
                - All test results with reference ranges
                - Any flagged values (High, Low, Abnormal)
                - Any notes or interpretations
                
                Format the output as a JSON object.
                
                Blood Test Report:
                {document_text}
                
                JSON Output:
                """
            ),
            "radiology": PromptTemplate(
                input_variables=["document_text"],
                template="""
                Extract the following information from this Radiology Report:
                - Patient Name
                - Patient ID/MRN
                - Date of Examination
                - Radiologist
                - Referring Physician
                - Type of Imaging (X-ray, MRI, CT, etc.)
                - Body Part Examined
                - Clinical Indication
                - Findings
                - Impression/Conclusion
                
                Format the output as a JSON object.
                
                Radiology Report:
                {document_text}
                
                JSON Output:
                """
            ),
            "prescription": PromptTemplate(
                input_variables=["document_text"],
                template="""
                Extract the following information from this Prescription:
                - Patient Name
                - Patient ID/MRN
                - Prescribing Doctor
                - Date Prescribed
                - All medications with:
                  - Name
                  - Dosage
                  - Frequency
                  - Duration
                  - Refills
                - Special Instructions
                
                Format the output as a JSON object.
                
                Prescription:
                {document_text}
                
                JSON Output:
                """
            ),
            "default": PromptTemplate(
                input_variables=["document_text", "document_type"],
                template="""
                Extract all relevant medical information from this {document_type}.
                Include patient details, dates, medical professionals involved, and all medical data.
                
                Format the output as a JSON object with clearly labeled fields.
                
                Document:
                {document_text}
                
                JSON Output:
                """
            )
        }
    
    def extract_medical_data(self, document_text, document_type="default"):
        """
        Extract structured medical data from document text
        
        Args:
            document_text (str): The text content of the document
            document_type (str): Type of document (blood_test, radiology, prescription, etc.)
            
        Returns:
            dict: Structured medical data extracted from the document
        """
        # Select the appropriate prompt template
        if document_type.lower() in self.extraction_prompts:
            prompt = self.extraction_prompts[document_type.lower()]
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.run(document_text=document_text[:4000])  # Limit to first 4000 chars
        else:
            prompt = self.extraction_prompts["default"]
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.run(document_text=document_text[:4000], document_type=document_type)
        
        # Attempt to parse the result as JSON
        try:
            # Find JSON in the response (in case there's extra text)
            json_match = re.search(r'({.*})', result, re.DOTALL)
            if json_match:
                result = json_match.group(1)
            
            extracted_data = json.loads(result)
            return extracted_data
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw text
            return {"error": "Failed to parse structured data", "raw_extraction": result}
    
    def get_tool(self):
        return Tool(
            name="MedicalDataExtractor",
            func=self.extract_medical_data,
            description="Extracts structured medical data from documents"
        )