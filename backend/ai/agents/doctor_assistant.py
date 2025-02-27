# backend/ai/agents/doctor_assistant.py
from langchain.tools import Tool
from langchain.chains import LLMChain, RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from ..embeddings import get_vectorstore
import json

class DoctorAssistant:
    """Tool for assisting doctors with patient information and medical queries"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.2)
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        
        self.qa_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""
            You are a medical AI assistant helping a doctor review patient information.
            Use the following patient information to answer the doctor's question.
            If you don't know the answer based on the given information, say so clearly.
            Do not make up information.
            
            Patient Information:
            {context}
            
            Doctor's Question:
            {question}
            
            Answer:
            """
        )
    
    def retrieve_patient_records(self, patient_id, query=None):
        """
        Retrieve and search through a patient's medical records
        
        Args:
            patient_id (str): The patient ID to search for
            query (str, optional): Specific query to search within patient records
            
        Returns:
            dict: Relevant patient information based on the query
        """
        try:
            # In a real implementation, this would retrieve the actual patient documents
            # from the database and create a vector store from them
            
            # For example:
            # vectorstore = get_vectorstore(patient_id)
            # retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
            
            # Placeholder for demonstration
            return {
                "result": f"Retrieved patient records for patient {patient_id}",
                "records": [
                    {"type": "Blood Test", "date": "2023-09-15", "key_findings": "Normal CBC, elevated glucose (142 mg/dL)"},
                    {"type": "Doctor Visit", "date": "2023-08-01", "key_findings": "Patient complained of fatigue and increased thirst"},
                    {"type": "Medication", "date": "2023-09-20", "details": "Metformin 500mg prescribed, once daily"}
                ]
            }
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_medical_trends(self, patient_id, metric_name):
        """
        Analyze trends in patient's medical data over time
        
        Args:
            patient_id (str): The patient ID to analyze
            metric_name (str): The medical metric to track (e.g., "glucose", "blood pressure")
            
        Returns:
            dict: Analysis of trends for the specified metric
        """
        try:
            # In a real implementation, this would retrieve historical measurements
            # and compute trends and statistical analysis
            
            # Placeholder for demonstration
            if metric_name.lower() == "glucose":
                return {
                    "metric": "Blood Glucose",
                    "unit": "mg/dL",
                    "values": [
                        {"date": "2023-07-10", "value": 130},
                        {"date": "2023-08-15", "value": 135},
                        {"date": "2023-09-15", "value": 142},
                    ],
                    "trend": "Increasing",
                    "average": 135.7,
                    "reference_range": "70-99 mg/dL (normal fasting)",
                    "status": "Above normal range"
                }
            else:
                return {"message": f"No trend data available for {metric_name}"}
        except Exception as e:
            return {"error": str(e)}
    
    def answer_medical_query(self, query, patient_context):
        """
        Answer a doctor's medical query based on patient context
        
        Args:
            query (str): The doctor's question
            patient_context (str): Patient information and medical records
            
        Returns:
            str: Response to the doctor's query
        """
        chain = LLMChain(
            llm=self.llm,
            prompt=self.qa_prompt
        )
        
        response = chain.run(context=patient_context, question=query)
        return response
    
    def get_tools(self):
        return [
            Tool(
                name="PatientRecordRetriever",
                func=self.retrieve_patient_records,
                description="Retrieves and searches through a patient's medical records"
            ),
            Tool(
                name="MedicalTrendAnalyzer",
                func=self.analyze_medical_trends,
                description="Analyzes trends in a patient's medical data over time"
            ),
            Tool(
                name="MedicalQueryAnswerer",
                func=self.answer_medical_query,
                description="Answers medical queries based on patient context"
            )
        ]