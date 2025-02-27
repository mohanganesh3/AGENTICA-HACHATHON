# backend/ai/agents/compliance_agent.py
from langchain.tools import Tool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

class ComplianceAgent:
    """Tool for checking HIPAA compliance of medical data handling"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        
        self.compliance_prompt = PromptTemplate(
            input_variables=["data"],
            template="""
            You are a HIPAA compliance expert. Review the following medical data and check for:
            
            1. Protected Health Information (PHI) that should be handled with care
            2. Proper patient identifiers
            3. Compliance risks
            4. Recommendations for secure handling
            
            Data to review:
            {data}
            
            Provide a compliance assessment with specific recommendations:
            """
        )
        
        self.compliance_chain = LLMChain(
            llm=self.llm,
            prompt=self.compliance_prompt
        )
    
    def check_compliance(self, data):
        """
        Check if the data handling is HIPAA compliant
        
        Args:
            data (str or dict): The data to check for compliance
            
        Returns:
            dict: Compliance assessment and recommendations
        """
        # Convert dict to string if needed
        if isinstance(data, dict):
            data_str = str(data)
        else:
            data_str = data
            
        assessment = self.compliance_chain.run(data=data_str[:4000])  # Limit to first 4000 chars
        
        return {
            "compliant": "non-compliant" not in assessment.lower(),
            "assessment": assessment,
            "contains_phi": "phi" in assessment.lower() or "protected health information" in assessment.lower()
        }
    
    def get_tool(self):
        return Tool(
            name="ComplianceChecker",
            func=self.check_compliance,
            description="Checks if medical data handling is HIPAA compliant"
        )