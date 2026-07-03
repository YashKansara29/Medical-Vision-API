import os
import io
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def generate_clinical_summary(image_bytes: bytes, clinical_context: str) -> str:
    try:
        # Convert raw bytes to a PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Systematic, chain-of-thought prompt for high accuracy
        clinical_prompt = f"""
You are a Board-Certified Radiologist. Perform a systematic, hierarchical 
analysis of this chest radiograph.

PATIENT SYMPTOMS: {clinical_context}

Follow these reasoning steps sequentially before forming an impression:

1. ANATOMICAL ANALYSIS: 
   - Right and Left lung zones: Identify any opacities.
   - Characterize margins: Are they "well-marginated/sharp" (suggestive of a nodule/mass) 
     or "ill-defined/patchy" (suggestive of consolidation/pneumonia)?
   - Anatomical Landmarks: Check the right heart border (silhouette sign) and 
     costophrenic angles. Do not report obscuration or blunting unless it is 
     clearly present.

2. FEATURE DIFFERENTIATION: 
   - If a density is present, is it homogeneous or heterogeneous? 
   - Are there air bronchograms? 

3. CLINICAL CORRELATION: 
   - Correlate the visual findings with the patient's symptoms (e.g., fever/cough).

4. FINAL IMPRESSION: 
   - Provide the most likely diagnosis.
   - If findings are ambiguous, state the limitation clearly.

STRICT RULES: 
- Do not invent findings. 
- Prioritize visual evidence over generic template phrases.
- If you cannot confirm a feature (e.g., obscuration), explicitly state it is not present.
""" 
        
        # Use Pro model for higher accuracy
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image, clinical_prompt],
        )
        return response.text
        
    except Exception as e:
        return f"AI Generation Failed: {str(e)}"