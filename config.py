"""
Configuration file for Document Assignment & Labelling application.
Contains all endpoints, constants, and configuration variables.
"""

# --- AZURE CONFIGURATION ---
# These should be set in Streamlit secrets
AZURE_CONNECTION_STRING_KEY = 'AZURE_CONNECTION_STRING'
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT_KEY = 'AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT'
AZURE_DOCUMENT_INTELLIGENCE_KEY_KEY = 'AZURE_DOCUMENT_INTELLIGENCE_KEY'
AZURE_LLM_ENDPOINT_KEY = 'AZURE_LLM_ENDPOINT'
AZURE_LLM_API_KEY_KEY = 'AZURE_LLM_API_KEY'

# Azure Storage Configuration
CONTAINER_NAME = "assignmentlabelling"

# --- MODEL CONFIGURATION ---
# Available models
AVAILABLE_MODELS = {
    "phi4": "Phi-4-multimodal-instruct",
    "gpt4o_mini": "gpt-4o-mini", 
    "mistral": "mistralai-mistral-7b-instruc-11"
}

# Default model
DEFAULT_MODEL = "Phi-4-multimodal-instruct"

# Model parameters
MAX_CHARS = 28000
MAX_TOKENS = 250
TEMPERATURE = 0.0

# --- DOCUMENT CLASSIFICATION CONFIGURATION ---
# Document types
DOCUMENT_TYPES = ["Court", "SOLICITOR-TP", "Insured", "Other"]

# Document subtypes
DOCUMENT_SUBTYPES = ["Judgement", "Summons", "Notice to Issue", "Query Chaser", "Other"]

# Document type mapping for feedback
DOC_TYPE_MAP = {
    "Court": "C", 
    "SOLICITOR-TP": "STP", 
    "Insured": "I", 
    "Other": "O"
}

# Subtype mapping for feedback
SUBTYPE_MAP = {
    "Judgement": "J", 
    "Summons": "S", 
    "Notice to Issue": "N2I", 
    "Query Chaser": "QC", 
    "Other": "O"
}

# --- CLASSIFICATION CATEGORIES ---
CLASSIFICATION_CATEGORIES = {
    "SUMMONS": {
        "description": "A court-issued document notifying a party they are being sued.",
        "keywords": ["Claim Form", "Claim form", "sealed Claim Form", "Writ"],
        "additional_terms": ["Particulars of Claim", "Defendant Response Pack", "Statement of Truth"],
        "extract_defendant": True,
        "extract_date": True
    },
    "JUDGMENT": {
        "description": "An official court decision, often titled 'Judgment for Claimant' or 'General Form of Judgment or Order'.",
        "keywords": ["Judgment for Claimant", "General Form of Judgment or Order"],
        "extract_defendant": False,
        "extract_date": False
    },
    "SOLICITOR_TP_S152": {
        "description": "Document related to Section 152 or Road Traffic Act",
        "keywords": ["Section 152", "S.152", "s152", "Section 152 (1) (a)", "Section 152(1)a", "Road Traffic Act", "RTA", "Road Traffic Act 1988"],
        "extract_defendant": False,
        "extract_date": False
    },
    "CHASER": {
        "description": "Follow-up communication that does not contain legal or procedural terms",
        "exclude_keywords": ["Claim Form", "Summons", "Judgment", "Writ", "Section 151", "Section 152", "Road Traffic Act", "RTA 1988"],
        "extract_defendant": False,
        "extract_date": False
    },
    "OTHER": {
        "description": "Text that does not clearly fit any of the categories above",
        "extract_defendant": False,
        "extract_date": False
    }
}

# --- SPECIAL DEFENDANT NAMES ---
SPECIAL_DEFENDANT_NAMES = {
    "PH": "Policy Holder",
    "PAN": "Defendant's Legal Representative (solicitors)",
    "EUI": ["Admiral", "EUI Ltd", "EUI Limited", "EUI Limited (Company Number:...)"]
}

# --- UI CONFIGURATION ---
# File upload settings
SUPPORTED_FILE_TYPES = ["pdf", "image"]
MAX_DESCRIPTION_CHARS = 200

# Feedback status codes
FEEDBACK_STATUS = {
    "SUCCESS": "S",
    "FAILURE": "F"
}

# --- API ENDPOINTS ---
# Document Intelligence model
DOCUMENT_INTELLIGENCE_MODEL = "prebuilt-read"

# --- ERROR MESSAGES ---
ERROR_MESSAGES = {
    "MISSING_SECRET": "Missing secret: {}. Please add {} and {}.",
    "TEXT_EXTRACTION_FAILED": "Text Extraction Error for LLMs: The call to Azure DI 'read' model failed: {}",
    "NO_TEXT_CONTENT": "Could not classify document as no text content was provided.",
    "LLM_CLIENT_FAILED": "LLM client initialization failed",
    "NO_JSON_RESPONSE": "No JSON object found in response. Raw: {}",
    "NO_RESPONSE_CONTENT": "No response content was generated.",
    "HTTP_ERROR": "LLM Request Failed ({}) with status code: {}",
    "CLASSIFICATION_ERROR": "LLM Classification Error ({}): {}",
    "UPLOAD_ERROR": "Error uploading file to blob: {}",
    "FEEDBACK_UPLOAD_ERROR": "Failed to upload feedback signal to Blob Storage: {}"
}

# --- SUCCESS MESSAGES ---
SUCCESS_MESSAGES = {
    "FILE_UPLOADED": "File '{}' uploaded successfully to blob storage.",
    "FEEDBACK_CORRECT": "Feedback recorded: {} was correct.",
    "FEEDBACK_INCORRECT": "Feedback recorded: {} was incorrect.",
    "FEEDBACK_FAILED": "Feedback for failed analysis recorded."
}

# --- SYSTEM PROMPTS ---
SYSTEM_PROMPT = (
    "You are an expert document classifier. Your sole task is to classify the given text into one of the predefined categories below "
    "and return the result strictly in the required JSON format. Do not provide explanations or any additional text.\n\n"
)

# --- JSON OUTPUT FORMAT ---
JSON_OUTPUT_FORMAT = {
    "class": "<Summons|Judgment|Solicitor_TP_S152|Chaser|Other>",
    "confidence": "<float between 0.0 and 1.0>",
    "details": {
        "defendant_name": "<The full name of the defendant (ignore Limited, Ltd, or use 'EUI' if EUI Ltd / EUI Limited / Admiral, or 'PH' if a company)>",
        "date_of_service": "<The date in DD/MM format>"
    }
}
