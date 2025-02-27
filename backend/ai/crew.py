# backend/ai/crew.py
from crewai import Agent, Task, Crew, Process
from langchain.chat_models import ChatOpenAI
from .agents.document_processor import DocumentClassifier
from .agents.medical_extractor import MedicalDataExtractor
from .agents.compliance_agent import ComplianceAgent
from .agents.doctor_assistant import DoctorAssistant

class MedicalDocumentCrew:
    def __init__(self, openai_api_key):
        # Initialize the LLM
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            api_key=openai_api_key
        )
        
        # Create the agents
        self.classifier_agent = Agent(
            role="Medical Document Classifier",
            goal="Accurately classify medical documents by type",
            backstory="You are an expert in medical document classification with years of experience in healthcare records management.",
            verbose=True,
            allow_delegation=True,
            llm=self.llm,
            tools=[DocumentClassifier().classify_document]
        )
        
        self.extractor_agent = Agent(
            role="Medical Data Extractor",
            goal="Extract key medical data from documents with high precision",
            backstory="You are a specialized medical data extraction system trained to identify and extract critical health information from various medical reports.",
            verbose=True,
            allow_delegation=True,
            llm=self.llm,
            tools=[MedicalDataExtractor().extract_medical_data]
        )
        
        self.compliance_agent = Agent(
            role="Healthcare Compliance Officer",
            goal="Ensure all documents and extractions meet HIPAA compliance standards",
            backstory="You are a compliance expert responsible for ensuring all medical data handling follows strict privacy regulations.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[ComplianceAgent().check_compliance]
        )
    
    def process_document(self, document_text, filename):
        """
        Process a medical document through the agent crew
        """
        # Define tasks
        classification_task = Task(
            description=f"Classify the following medical document: {filename}. Determine whether it's a blood report, radiology report, prescription, or other medical document type.",
            agent=self.classifier_agent,
            expected_output="Document type classification with confidence score"
        )
        
        extraction_task = Task(
            description="Extract all relevant medical data including patient information, test results, diagnoses, and key health indicators.",
            agent=self.extractor_agent,
            expected_output="Structured JSON containing all extracted medical data",
            context=[classification_task]
        )
        
        compliance_task = Task(
            description="Verify the extracted data complies with HIPAA standards. Flag any potential compliance issues.",
            agent=self.compliance_agent,
            expected_output="Compliance verification report",
            context=[extraction_task]
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[self.classifier_agent, self.extractor_agent, self.compliance_agent],
            tasks=[classification_task, extraction_task, compliance_task],
            verbose=True,
            process=Process.sequential
        )
        
        result = crew.kickoff(inputs={"document_text": document_text})
        return result


class DoctorAssistantCrew:
    def __init__(self, openai_api_key):
        # Initialize the LLM
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.2,
            api_key=openai_api_key
        )
        
        # Create the agent
        self.doctor_assistant = Agent(
            role="Medical Assistant",
            goal="Provide accurate medical insights based on patient records",
            backstory="You are an AI medical assistant designed to help doctors quickly access and interpret patient medical records. You provide clear, concise information while maintaining patient confidentiality.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[DoctorAssistant().retrieve_patient_records, DoctorAssistant().analyze_medical_trends]
        )
    
    def answer_query(self, query, patient_id, doctor_id):
        """
        Answer a doctor's query about patient data
        """
        task = Task(
            description=f"Answer the following medical query from a doctor about patient {patient_id}: {query}",
            agent=self.doctor_assistant,
            expected_output="Comprehensive yet concise answer to the doctor's query based on patient records",
            context={"patient_id": patient_id, "doctor_id": doctor_id}
        )
        
        crew = Crew(
            agents=[self.doctor_assistant],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        return result