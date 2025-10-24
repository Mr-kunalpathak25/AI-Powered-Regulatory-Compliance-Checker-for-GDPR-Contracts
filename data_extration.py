from google import genai
from pydantic import BaseModel
import json
import PyPDF2
import os
from groq import Groq
from dotenv import load_dotenv
from google.genai import types
import notification  # ✅ added import for notifications

load_dotenv()


# ********   Phase 1    ******** #
def Clause_extraction(file):
    print("inside clause extraction")

    class ClauseExtraction(BaseModel):
        clause_id: str
        heading: str
        text: str

    text = ""
    with open(file, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
    You are an expert in legal contract analysis.
    Your task is to extract all **clauses** from the following contract text.

    ### Guidelines:
    - A clause may begin with:
      - A number/letter (e.g. "1.", "A.")
      - The word "Clause" followed by a number (e.g. "Clause 1", "Clause 5")
      - An ALL CAPS heading (e.g. "DEFINITIONS", "TRANSFER OF DATA")

    - Each extracted clause must include:
      - **clause_id** (the exact numbering/label)
      - **heading/title** (explicit heading or first few words if missing)
      - **full text** (complete text including sub-clauses)

    - Maintain clause boundaries precisely; do not merge clauses.
    - Include exhibits, appendices, and annexes if present.
    - Omit only non-contractual elements (headers, footers, blank signature lines).
    - Respond in **valid JSON** only.

    Input: {text}

    Response in this JSON Structure:
    [
        {{
            "clause_id": "<clause_id>",
            "heading/title": "<heading_or_title>",
            "full text": "<full_text_of_clause>"
        }},
        ...
    ]
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            response_mime_type="application/json",
            response_schema=list[ClauseExtraction],
        ),
    )

    response = response.text
    print(response)
    return response


def Clause_extraction_with_summarization(file):
    print("inside clause extraction (summarized)")

    class ClauseExtraction(BaseModel):
        clause_id: str
        heading: str
        summarised_text: str

    text = ""
    with open(file, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = f"""
    You are an expert in legal contract analysis.
    Your task is to extract all **clauses** from the following contract text and summarize each clause.

    ### Guidelines:
    - A clause may begin with:
      - A number/letter (e.g. "1.", "A.")
      - The word "Clause" followed by a number (e.g. "Clause 1", "Clause 5")
      - An ALL CAPS heading (e.g. "DEFINITIONS", "TRANSFER OF DATA")

    - Each extracted clause must include:
      - **clause_id**
      - **heading/title**
      - **summarised text** (a concise, meaningful summary preserving core information)

    - Maintain clause boundaries precisely.
    - Include exhibits, appendices, and annexes if present.
    - Omit only non-contractual elements.
    - Respond in **valid JSON** only.

    Input: {text}

    Response in this JSON Structure:
    [
        {{
            "clause_id": "<clause_id>",
            "heading/title": "<heading_or_title>",
            "summarised_text": "<summarised_text_of_clause>"
        }},
        ...
    ]
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            response_mime_type="application/json",
            response_schema=list[ClauseExtraction],
        ),
    )

    response = response.text
    print(response)
    return response


if __name__ == "__main__":
    try:
        TEMPLATE_MAP = {
            "dpa.json": "templates/GDPR-Sample-Agreement.pdf",
            "jca.json": "templates/(JCA) model-joint-controllership-agreement.pdf",
            "c2c.json": "templates/(C2C) 2-Controller-to-controller-data-privacy-addendum.pdf",
            "scc.json": "templates/Standard-Contractual-Clauses-SCCs.pdf",
            "subprocessing.json": "templates/(Subprocessing Contract) Personal-Data-Sub-Processor-Agreement-2024-01-24.pdf"
        }

        for key, value in TEMPLATE_MAP.items():
            response = Clause_extraction(value)
            # For summarised version, use below instead:
            # response = Clause_extraction_with_summarization(value)

            with open("json_files/" + key, "w", encoding="utf-8") as f:
                json.dump(response, f, indent=2, ensure_ascii=False)

    except Exception as e:
        print("Error Occurred:", e)
        notification.send_notification(
            "Error Occurred in Template Data Extraction",
            f"Error details: {e}"
        )
