import streamlit as st
from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest
from azure.core.exceptions import HttpResponseError
import pymupdf # PyMuPDF
from PIL import Image
import io
import re
import time
from azure.core.exceptions import AzureError, ClientAuthenticationError
from datetime import datetime
import json
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
import urllib.request
import urllib.error

# Import configuration
from config import (
    AZURE_CONNECTION_STRING_KEY, CONTAINER_NAME, AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT_KEY,
    AZURE_DOCUMENT_INTELLIGENCE_KEY_KEY, AZURE_LLM_ENDPOINT_KEY, AZURE_LLM_API_KEY_KEY,
    AVAILABLE_MODELS, DEFAULT_MODEL, MAX_CHARS, MAX_TOKENS, TEMPERATURE,
    DOCUMENT_TYPES, DOCUMENT_SUBTYPES, DOC_TYPE_MAP, SUBTYPE_MAP,
    CLASSIFICATION_CATEGORIES, SPECIAL_DEFENDANT_NAMES, SUPPORTED_FILE_TYPES,
    MAX_DESCRIPTION_CHARS, FEEDBACK_STATUS, DOCUMENT_INTELLIGENCE_MODEL,
    ERROR_MESSAGES, SUCCESS_MESSAGES, SYSTEM_PROMPT, JSON_OUTPUT_FORMAT
)

# --- AZURE AND APP CONFIGURATION ---
# Handle both Streamlit secrets and environment variables for Azure deployment
try:
    AZURE_CONNECTION_STRING = st.secrets[AZURE_CONNECTION_STRING_KEY]
except:
    AZURE_CONNECTION_STRING = os.getenv(AZURE_CONNECTION_STRING_KEY)

try:
    ENDPOINT = st.secrets[AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT_KEY]
except:
    ENDPOINT = os.getenv(AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT_KEY)

try:
    KEY = st.secrets[AZURE_DOCUMENT_INTELLIGENCE_KEY_KEY]
except:
    KEY = os.getenv(AZURE_DOCUMENT_INTELLIGENCE_KEY_KEY)

# Set Streamlit configuration for Azure
st.set_page_config(
    page_title="Document Assignment & Labelling",
    page_icon="📄",
    layout="wide"
)

# Azure-specific configuration as per Microsoft docs
if __name__ == '__main__':
    st.set_option('server.enableCORS', True)

# --- LLM AND COMPARISON FUNCTIONS (Updated to compare two LLMs) ---

def get_llm_client():
    """Initializes and returns the Azure ChatCompletionsClient for the LLMs."""
    try:
        # Try Streamlit secrets first, then environment variables
        try:
            endpoint = st.secrets[AZURE_LLM_ENDPOINT_KEY]
        except:
            endpoint = os.getenv(AZURE_LLM_ENDPOINT_KEY)
        
        try:
            api_key = st.secrets[AZURE_LLM_API_KEY_KEY]
        except:
            api_key = os.getenv(AZURE_LLM_API_KEY_KEY)
        
        if not endpoint or not api_key:
            raise KeyError(f"Missing {AZURE_LLM_ENDPOINT_KEY} or {AZURE_LLM_API_KEY_KEY}")
            
        return ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))
    except KeyError as e:
        st.error(ERROR_MESSAGES["MISSING_SECRET"].format(e, AZURE_LLM_ENDPOINT_KEY, AZURE_LLM_API_KEY_KEY))
        return None

def extract_text_for_llms(file_binary):
    """Extracts text from a document using the Azure DI 'prebuilt-read' model for robust OCR."""
    try:
        client = DocumentIntelligenceClient(endpoint=ENDPOINT, credential=AzureKeyCredential(KEY))
        poller = client.begin_analyze_document(DOCUMENT_INTELLIGENCE_MODEL, AnalyzeDocumentRequest(bytes_source=file_binary))
        result = poller.result()
        return result.content
    except HttpResponseError as e:
        st.error(ERROR_MESSAGES["TEXT_EXTRACTION_FAILED"].format(e.message))
        return None

# --- Start of updated code block ---
def classify_with_model(text_content, model_name):
    """Sends document text to a specified LLM for classification and conditional entity extraction."""
    if not text_content:
        st.warning(ERROR_MESSAGES["NO_TEXT_CONTENT"])
        return {"class": "Error", "reason": "No text content provided"}

    if len(text_content) > MAX_CHARS:
        text_content = text_content[:MAX_CHARS]

    user_prompt_template = (
        "Analyze the following text. First, classify it. "
        "### Categories:\n"
        "1. **Summons**\n"
        "   - A court-issued document notifying a party they are being sued.\n"
        "   - Must contain references to 'Claim Form', 'Claim form', 'sealed Claim Form', or 'Writ' (case-insensitive, even if inside a covering letter).\n"
        "   - May also include terms such as 'Particulars of Claim', 'Defendant Response Pack', or 'Statement of Truth'.\n\n"
        "   - Will usually include fields for claimant's and defendant's names and addresses.\n\n"
        "If the class is 'Summons':\n"
        "- You MUST extract the defendant's name.\n"
        "- Use the 'Issued' or 'Submitted' date (if available) as the date of service. Format as DD/MM.\n"
        "- If the summons is against the Policy Holder then return 'PH' for the defendant's name.\n"
        "- If there is a section called 'Defendant's Legal Representative' with the name of solicitors then return 'PAN' for the defendant's name.\n"
        "- If the summons is against Admiral, EUI Ltd, or EUI Limited (including variants such as 'EUI Limited (Company Number:...)'), you MUST return exactly 'EUI' for the defendant's name.\n\n"
        "If it is not a Summons, the 'Description' field should be null.\n"
        "2. **Judgment**\n"
        "   - An official court decision, often titled 'Judgment for Claimant' or 'General Form of Judgment or Order'.\n\n"
        "3. **Solicitor_TP_S152**\n"
        "   - Classify as Solicitor_TP_S152 if and ONLY if:\n"
        "       - The text contains a clear reference to 'Section 152' (e.g., 'Section 152', 'S.152', 's152', 'Section 152 (1) (a)', 'Section 152(1)a').\n"
        "       - OR the text contains a clear reference to 'Road Traffic Act' (e.g., 'Road Traffic Act', 'RTA', 'Road Traffic Act 1988').\n"
        "       - The keywords are case-insensitive and can have spaces/punctuation between numbers/letters.\n"
        "4. **Chaser**\n"
        "- Only classify as Chaser if the document is a follow-up communication AND does NOT contain any legal or procedural terms that indicate a Summons, Judgment, or Solicitor_TP_S152 document.\n"
        "- Do NOT classify as Chaser if text contains terms like 'Claim Form', 'Summons', 'Judgment', 'Writ', 'Section 151', 'Section 152', 'Road Traffic Act', or 'RTA 1988'.\n"
        "- Any follow-up communication or repeated attempt to get a response,\n"
        "  even if the reason or context is not explicitly stated.\n"
        "- May reference a previous call, message, or action, OR simply indicate\n"
        "  continued attempts to contact or follow up (e.g., 'I tried again today, no answer')\n"
        "- Can include cases where:\n"
        "   • The user receives claim-related communication but doesn't understand the context or origin.\n"
        "   • The user seeks clarification of a claim.\n"
        "   • The user expresses frustration over being contacted by phone and would prefer email communication.\n"
        "   • The user says they prefer to be contacted via telephone.\n"
        "   • The user has technical issues with access to documents sent by the claims handler.\n"
        "5. **Other**\n"
        "   - The text does not clearly fit any of the categories above.\n"
        "Return ONLY the JSON object.\n\n"
        "--- DOCUMENT TEXT BEGIN ---\n"
        f"{text_content}\n"
        "--- DOCUMENT TEXT END ---\n\n"
        "JSON output format:\n"
        "{\n"
        '  "class": "<Summons|Judgment|Solicitor_TP_S152|Chaser|Other>",\n'
        '  "confidence": <float between 0.0 and 1.0>,\n'
        '  "details": {\n'
        '    "defendant_name": "<The full name of the defendant (ignore Limited, Ltd, or use \'EUI\' if EUI Ltd / EUI Limited / Admiral, or \'PH\' if a company)>",\n'
        '    "date_of_service": "<The date in DD/MM format>"\n'
        "  } OR null\n"
        "}"
    )
   
    raw_response_content = None # This will hold the raw string from the model

    try:
        # --- IF THE MODEL IS MISTRAL, USE URLLIB REQUEST ---
        # This assumes your mistral model name in the main app block will contain "mistral"
        if "mistral" in model_name:
            # Try Streamlit secrets first, then environment variables
            try:
                url = st.secrets['AZURE_LLM_ENDPOINT']
            except:
                url = os.getenv('AZURE_LLM_ENDPOINT')
            
            try:
                api_key = st.secrets['AZURE_LLM_API_KEY']
            except:
                api_key = os.getenv('AZURE_LLM_API_KEY')
            
            if not api_key or not url:
                raise Exception("AZURE_LLM_ENDPOINT or AZURE_LLM_API_KEY secrets are not set.")

            # Construct the request data in the Mistral format
            data = {
                "input_data": {
                    "input_string": [
                        {
                            "role": "user",
                            "content": f"{SYSTEM_PROMPT}\n{user_prompt_template}"
                        }
                    ],
                    "parameters": {
                        "max_new_tokens": 250,
                        "temperature": 0.0,
                        "return_full_text": False
                    }
                }
            }

            body = str.encode(json.dumps(data))
            headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}
            req = urllib.request.Request(url, body, headers)
           
            response = urllib.request.urlopen(req)
            result = response.read()
            # The response from Azure ML endpoints is often a JSON string containing a list,
            # with the model's output as the first element.
            response_json = json.loads(result.decode('utf-8'))
            raw_response_content = response_json[0]


        # --- ELSE, USE THE AZURE AI SDK (FOR PHI-4 etc.) ---
        else:
            client = get_llm_client()
            if not client:
                return {"class": "Error", "reason": "LLM client initialization failed"}
           
            # This format is for Phi-4
            response = client.complete(
                messages=[SystemMessage(content=system_prompt), UserMessage(content=user_prompt_template)],
                model=model_name,
                max_tokens=250,
                temperature=0.0,
            )
            raw_response_content = response.choices[0].message.content

        # --- COMMON RESPONSE PARSING FOR BOTH MODELS ---
        if raw_response_content:
            # Find the JSON object within the response, in case the model adds extra text
            json_match = re.search(r'\{.*\}', raw_response_content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
           
            st.error(f"LLM Error ({model_name}): No JSON object found in response. Raw: {raw_response_content}")
            return {"class": "Error", "reason": "No JSON object in response"}
       
        # This case is reached if no response was generated by either method
        st.error(f"LLM Error ({model_name}): No response content was generated.")
        return {"class": "Error", "reason": "No response content generated"}

    except urllib.error.HTTPError as error:
        st.error(f"LLM Request Failed ({model_name}) with status code: {error.code}")
        st.error(f"Details: {error.read().decode('utf8', 'ignore')}")
        return {"class": "Error", "reason": f"HTTP Error {error.code}"}
    except (ClientAuthenticationError, HttpResponseError, Exception) as e:
        st.error(f"LLM Classification Error ({model_name}): {e}")
        return {"class": "Error", "reason": str(e)}
# --- End of updated code block ---


def normalize_and_describe_model_result(model_result):
    """Converts an LLM result into a standard (DocType, SubType, Description) tuple."""
    if not model_result or model_result.get('class') == 'Error':
        return ("Error", f"Classification failed: {model_result.get('reason', 'Unknown')}", "")

    #st.write(f"Helper: model_result {model_result}")
    llm_class = model_result.get('class')
    #st.write(f"Helper: llm_class {llm_class}")
    details = model_result.get('details')
    #st.write(f"Helper: details {details}")
    if llm_class == "Summons":
        if details:
            defendant = details.get('defendant_name', '(Defendant unknown)')
            date = details.get('date_of_service', '(Date unknown)')
            description = f"LIT; SUMMONS {defendant} {date}"
        else:
            description = "LIT; SUMMONS (Defendant unknown) (Date unknown)"
        return ("Court", "Summons", description)
    elif llm_class == "Judgment":
        return ("Court", "Judgement", "(1) LIT; JUDGMENT")
    elif llm_class == "Solicitor_TP_S152":
        return ("SOLICITOR-TP", "Notice to Issue", "")
    elif llm_class == "Chaser":
        return ("Insured", "Query Chaser", "")
    return ("Other", "Other", "")

def sanitize_for_blob_name(text: str) -> str:
    """Removes characters that are not permitted in Azure Blob Storage filenames."""
    # Removes characters: \ / : * ? " < > |
    return re.sub(r'[\\/:*?"<>|]', '', text)

# --- UI AND DISPLAY FUNCTIONS ---

def upload_to_blob(file_data, filename):
    """Uploads a file to Azure Blob Storage."""
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=filename)
        blob_client.upload_blob(file_data, overwrite=True)
        st.success(f"File '{filename}' uploaded successfully to blob storage.")
    except Exception as e:
        st.error(f"Error uploading file to blob: {str(e)}")

def render_pdf(file):
    doc = pymupdf.open(stream=file.read(), filetype="pdf")
    page = doc.load_page(0)
    st.image(page.get_pixmap().tobytes(), caption='First page of PDF')

def render_image(file):
    st.image(Image.open(file), caption='Uploaded Image')

def main():
    st.title("Document Assignment & Labelling")
    uploaded_file = st.file_uploader("Upload a file, view it, then classify it.")
   
    if uploaded_file is not None:
        st.session_state["filename"] = uploaded_file.name
        if st.button("Upload and view first page"):
            file_binary = uploaded_file.getvalue()
            st.session_state["uploaded_filename"] = file_binary
            upload_to_blob(file_binary, uploaded_file.name)
            # --- CHANGE START ---
            # Clear previous results and feedback choices on new upload
            for key in ["classification_complete", "model_a_result", "feedback_choice"]:
                if key in st.session_state:
                    del st.session_state[key]
            # --- CHANGE END ---
           
            if 'pdf' in uploaded_file.type:
                render_pdf(uploaded_file)
            elif 'image' in uploaded_file.type:
                render_image(uploaded_file)
            else:
                st.write("Unsupported file type. Please upload a PDF or image.")

def display_model_results(model_result):
    """Displays the formatted results from a given model."""
    if not model_result:
        st.error("No result to display.")
        return

    doc_type, sub_type, description = normalize_and_describe_model_result(model_result)
    st.write(f"**Document Type:** {doc_type}")
    st.write(f"**Document SubType:** {sub_type}")
    if description:
        st.write(f"**Description:** {description}")
   
    confidence = model_result.get('confidence', 'N/A')
    st.write(f"**Model Confidence:** {confidence:.2f}" if isinstance(confidence, float) else f"**Model Confidence:** {confidence}")

# --- FEEDBACK FUNCTIONS ---

def upload_feedback_blob(model_prediction, model_name, actual_classification):
    """
    Uploads a feedback signal file for a specific model to Azure Blob Storage.
    - model_prediction: The raw JSON result from the model being logged.
    - model_name: The string name of the model (e.g., 'gpt-4o-mini').
    - actual_classification: None if the prediction was correct, or a normalized
      (DocType, SubType, Description) tuple if it was incorrect.
    """
    pred_norm = normalize_and_describe_model_result(model_prediction)

    # UPDATED: Added "Other" to the maps to prevent "manual" default.
    doc_type_map = {"Court": "C", "SOLICITOR-TP": "STP", "Insured": "I", "Other": "O"}
    sub_type_map = {"Judgement": "J", "Summons": "S", "Notice to Issue": "N2I", "Query Chaser": "QC", "Other": "O"}

    # Extract predicted values from the model's normalized output
    predicted_doc_type = doc_type_map.get(pred_norm[0], "unknown")
    predicted_sub_type = sub_type_map.get(pred_norm[1], "unknown")
    predicted_desc = pred_norm[2] if pred_norm[2] else "NA"

    is_correct = actual_classification is None
    if is_correct:
        # If correct, actual values are the same as predicted
        actual_doc_type = predicted_doc_type
        actual_sub_type = predicted_sub_type
        actual_desc = predicted_desc
    else:
        # If the classification was incorrect, use the provided actual_classification tuple
        # (which contains the correct values from the dropdown menus) to set the ground truth.
        correct_doc_type_full = actual_classification[0]
        correct_sub_type_full = actual_classification[1]
        correct_desc = actual_classification[2]

        # Convert the full-text classification from the dropdowns into the required short codes for the filename.
        actual_doc_type = doc_type_map.get(correct_doc_type_full, "manual")
        actual_sub_type = sub_type_map.get(correct_sub_type_full, "manual")
        actual_desc = correct_desc if correct_desc else "NA"

    # Sanitize the description parts for the blob name
    predicted_desc = sanitize_for_blob_name(predicted_desc)
    actual_desc = sanitize_for_blob_name(actual_desc)

    try:
        timestamp = datetime.now().strftime("%y%m%d%H%M%S")
        status = "S" if is_correct else "F"
       
        # Updated blob name format to include all required fields
        blob_name = f"{status}___{timestamp}___{model_name}___{predicted_doc_type}___{predicted_sub_type}___{predicted_desc}___{actual_doc_type}___{actual_sub_type}___{actual_desc}___{st.session_state['filename']}.txt"
       
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
        blob_client.upload_blob(b"", overwrite=True)
        return True
    except (KeyError, AzureError, Exception) as ex:
        st.error(f"Failed to upload feedback signal to Blob Storage: {ex}")
        return False


# --- MAIN EXECUTION BLOCK ---

if __name__ == "__main__":
    main()
    # --- CHANGE START ---
    # Set the model to use
    model_a = "Phi-4-multimodal-instruct"
    # model_a = "gpt-4o-mini"
    # model_a = "mistralai-mistral-7b-instruc-11"

    # Initialize session state keys if they don't exist
    for key in ["classification_complete", "model_a_result"]:
        if key not in st.session_state:
            st.session_state[key] = {} if key.endswith('_result') else False
    # --- CHANGE END ---

    if st.button("Classify document"):
        if "uploaded_filename" not in st.session_state:
            st.warning("Please upload a file and click 'Upload and view first page' first.")
        else:
            # --- CHANGE START ---
            with st.spinner(f"Extracting text and analyzing with {model_a}... This may take a moment."):
                text_content = extract_text_for_llms(st.session_state.uploaded_filename)
               
                st.write(f"This is the text being sent to the LLM:\n\n{text_content}\n\n")

                # Run the classification model
                st.session_state.model_a_result = classify_with_model(text_content, model_name=model_a)
               
                st.session_state.classification_complete = True
                # Reset feedback choice on new classification
                if 'feedback_choice' in st.session_state:
                    del st.session_state['feedback_choice']
            # --- CHANGE END ---


    if st.session_state.classification_complete:
        st.markdown("---")
        st.header("Classification Result")
       
        # --- CHANGE START ---
        # Display the single model's result
        with st.container(border=True):
            st.subheader(f"{model_a} Result")
            display_model_results(st.session_state.model_a_result)
       
        st.markdown("---")

        model_a_result = st.session_state.get("model_a_result")
       
        PREDEFINED_DOC_TYPES = ["Court", "SOLICITOR-TP", "Insured", "Other"]
        PREDEFINED_SUB_TYPES = ["Judgement", "Summons", "Notice to Issue", "Query Chaser", "Other"]

        # If the model returned a valid classification (not an error)
        if model_a_result and model_a_result.get('class') != 'Error':
            with st.container(border=True):
                st.radio(
                    "Is this classification correct?",
                    ("Correct", "Incorrect"),
                    key="feedback_choice",
                    horizontal=True
                )
                with st.form("feedback_form_success"):
                    if st.session_state.feedback_choice == "Incorrect":
                        st.write("Please provide the correct classification:")
                        c1, c2 = st.columns(2)
                        doc_type = c1.selectbox("Correct Document Type", PREDEFINED_DOC_TYPES, key="doc_type_s")
                        sub_type = c2.selectbox("Correct SubType", PREDEFINED_SUB_TYPES, key="sub_type_s")
                        st.text_input("Description", key="description_s", max_chars=200)
                   
                    submitted = st.form_submit_button("Submit Feedback")
                    if submitted:
                        if st.session_state.feedback_choice == "Correct":
                            # Log the model as correct.
                            res = upload_feedback_blob(model_a_result, model_a, actual_classification=None)
                            if res:
                                st.toast(f"Feedback recorded: {model_a} was correct.", icon="✅")
                                time.sleep(4); st.rerun()
                        else: # Incorrect
                            # Log the model as incorrect against the manual entry.
                            actual_manual = (st.session_state.doc_type_s, st.session_state.sub_type_s, st.session_state.description_s)
                            res = upload_feedback_blob(model_a_result, model_a, actual_classification=actual_manual)
                            if res:
                                st.toast(f"Feedback recorded: {model_a} was incorrect.", icon="❌")
                                time.sleep(4); st.rerun()
        else:
            # This block handles the case where the model failed classification (returned an error)
            st.info("Model could not classify the document. Please provide the correct classification manually.")
            with st.form("feedback_form_error"):
                st.write("Please provide the correct classification:")
                c1, c2 = st.columns(2)
                doc_type = c1.selectbox("Correct Document Type", PREDEFINED_DOC_TYPES, key="doc_type_e")
                sub_type = c2.selectbox("Correct SubType", PREDEFINED_SUB_TYPES, key="sub_type_e")
                st.text_input("Description", key="description_e", max_chars=200)

                submitted = st.form_submit_button("Submit Feedback")
                if submitted:
                    actual_manual = (st.session_state.doc_type_e, st.session_state.sub_type_e, st.session_state.description_e)
                    # Log feedback for the model against the manual entry
                    res = upload_feedback_blob(model_a_result, model_a, actual_classification=actual_manual)
                    if res:
                        st.toast("Feedback for failed analysis recorded.", icon="✅")
                        time.sleep(4); st.rerun()
        # --- CHANGE END ---