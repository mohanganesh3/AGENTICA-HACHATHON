# backend/ai/prompts.py
"""
Contains all prompt templates for the healthcare document management system agents
Organized by agent type and function
"""

# ========================
# DOCUMENT PROCESSOR PROMPTS
# ========================

DOCUMENT_CLASSIFICATION_PROMPT = """You are a medical document classification expert. 
Analyze the document text and classify it into one of these categories:

Allowed Types:
- Blood Test Report
- Radiology Report (X-ray/MRI/CT)
- Doctor Progress Note
- Prescription
- Medical History
- Discharge Summary
- Pathology Report
- Surgical Report
- Immunization Record
- Insurance Claim
- Referral Letter
- Other (specify reason)

Document Content:
{document_text}

Provide your classification in this format:
{{
  "document_type": "classified_type",
  "confidence": 0.0-1.0,
  "reason": "brief explanation",
  "identified_metadata": {{
    "patient_id": "extracted_if_present",
    "date": "extracted_date_if_available"
  }}
}}"""

# ========================
# MEDICAL DATA EXTRACTION PROMPTS
# ========================

BLOOD_TEST_EXTRACTION_PROMPT = """Extract structured data from this blood test report:

Required Fields:
- Patient ID (MRN)
- Patient Name
- Date of Collection
- Ordering Physician
- Tests: [list with name, value, unit, reference_range, flag]
- Summary of Abnormalities
- Any Notes/Interpretations

Document Content:
{document_text}

Return JSON format with exactly these fields. If information is missing, use null.
Example:
{{
  "patient_mrn": "123-45-678",
  "tests": [
    {{
      "name": "Hemoglobin",
      "value": 14.2,
      "unit": "g/dL",
      "reference_range": "13.5-17.5",
      "flag": "normal"
    }}
  ]
}}"""

RADIOLOGY_REPORT_PROMPT = """Extract key information from this radiology report:

Structure:
- Patient ID
- Imaging Modality (CT/X-ray/MRI)
- Body Part
- Clinical Indication
- Technique
- Findings
- Impression
- Recommendations
- Critical Findings (yes/no)

Content:
{document_text}

Return as JSON with the above structure. Use null for missing fields."""

# ========================
# COMPLIANCE AGENT PROMPTS 
# ========================

HIPAA_COMPLIANCE_CHECK_PROMPT = """Analyze this medical document extract for PHI and HIPAA compliance:

Document Excerpt:
{content}

Check for:
1. Direct identifiers (names, MRN, DOB)
2. Indirect identifiers (dates < year, rare conditions)
3. Proper de-identification
4. Unnecessary sensitive information

Return assessment in this format:
{{
  "phi_present": boolean,
  "compliance_status": "compliant/partially_compliant/non_compliant",
  "risk_level": "low/medium/high",
  "recommended_actions": ["redact_item1", "replace_item2"]
}}"""

# ========================
# DOCTOR ASSISTANT PROMPTS
# ========================

PATIENT_QUERY_PROMPT = """You are a medical AI assistant helping a doctor with patient care.
Use these patient records to answer the question:

Patient Context:
- Name: {patient_name}
- Age: {age}
- Conditions: {conditions}
- Recent Tests: {recent_tests}
- Current Meds: {medications}

Doctor's Question: {question}

Guidelines:
1. Be concise but thorough
2. Highlight critical values
3. Suggest next steps if appropriate
4. Never make diagnoses
5. Maintain HIPAA compliance

Format response as:
**Summary**
Brief overview

**Relevant Findings**
- Bullet points of key data

**Recommendations**
- Possible actions to consider"""

TREND_ANALYSIS_PROMPT = """Analyze medical trends for {patient_id}:

Data Points:
{data_points}

Task:
1. Identify significant trends
2. Compare to reference ranges
3. Flag dangerous trajectories
4. Suggest monitoring/follow-up

Format as:
**Trend Analysis Report**
- Parameter: {parameter}
- Time Period: {start_date} to {end_date}
- Key Observations
- Clinical Significance
- Recommended Actions"""

# ========================
# SEARCH AGENT PROMPTS
# ========================

SEMANTIC_SEARCH_PROMPT = """Generate search queries for medical document retrieval:

User Question: {question}

Constraints:
- Patient ID: {patient_id}
- Date Range: {date_range}
- Document Types: {doc_types}

Create 3 search queries that combine:
- Clinical concepts from the question
- Relevant medical terminology
- Possible synonyms/acronyms

Return as JSON:
{{
  "queries": [
    "query1",
    "query2", 
    "query3"
  ]
}}"""

# ========================
# ERROR HANDLING PROMPTS
# ========================

ERROR_RESPONSE_PROMPT = """Handle this medical document processing error:

Error Context:
- Document Type: {doc_type}
- Stage: {stage}
- Error Message: {error}

Create a user-friendly message that:
1. Explains the issue in non-technical terms
2. Suggests possible solutions
3. Maintains HIPAA compliance
4. Provides error code for support

Example Format:
"We encountered an issue processing your {doc_type}. This is usually caused by [...] 
Please try [...] or contact support with code: {error_code}" """

# ========================
# REDACTION PROMPTS
# ========================

PHI_REDACTION_PROMPT = """Redact Protected Health Information (PHI) from this text:

Input:
{text}

Rules:
1. Replace names with [PATIENT]
2. Replace MRNs with [MRN]
3. Replace dates > current year with [DATE]
4. Keep medical terms intact
5. Preserve clinical meaning

Output only the redacted text, no additional commentary."""

# ========================
# REPORT GENERATION PROMPTS
# ========================

DISCHARGE_SUMMARY_PROMPT = """Generate a hospital discharge summary using:

Patient Data:
{patient_data}

Hospital Course:
- Admission Date: {admit_date}
- Discharge Date: {discharge_date}
- Procedures: {procedures}
- Complications: {complications}

Medications at Discharge:
{medications}

Follow-up Plan:
{follow_up}

Format using standard medical sections:
1. Admission Diagnosis  
2. Hospital Course
3. Discharge Medications
4. Follow-up Instructions
5. Patient Education"""


def get_prompt(prompt_name: str) -> str:
    """Retrieve prompt template by name"""
    return globals().get(prompt_name.upper(), "")