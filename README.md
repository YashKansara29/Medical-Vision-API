# Medical Vision & Diagnostics API

A stateful, clinical-grade informatics backend designed to interpret medical radiographs by integrating visual reasoning with patient clinical history.

## 1. The Problem: AI Hallucinations in Radiology
During the development of this project, I identified three critical failure points common in diagnostic AI that lead to unreliable clinical reporting:

*   **Template Hallucination**: Without strict constraints, the model defaulted to generic "pneumonia" reports, inventing clinical findings like "blunted costophrenic angles" or "obscured heart borders" even when the visual evidence (e.g., in `carcinoid-tumour-of-the-lung (1).jpg`) showed perfectly sharp angles and normal anatomy.
*   **Anatomical Mislocalization**: The model struggled to differentiate between diffuse airspace opacification (pneumonia) and focal, well-marginated lesions (nodules/tumors) because it lacked a hierarchical review process, often mislabeling a focal mass as diffuse consolidation.
*   **Context Blindness**: By treating X-rays in isolation, the AI failed to perform **clinical correlation**. It initially ignored vital patient data (e.g., cough and fever for 3 days), leading to diagnostic reports that lacked the necessary nuance to differentiate between acute infectious processes and chronic neoplastic masses.

## 2. The Solution: Chain-of-Thought (CoT) Informatics
I transitioned from basic image summarization to a rigorous, systematic analysis pipeline to solve these issues:

*   **Pixel-Level Direct Injection**: I implemented a pipeline using `PIL` to convert upload streams into raw image bytes, bypassing metadata-only interpretation and forcing the model to analyze the actual pixels.
*   **Hierarchical Anatomical Constraints**: I enforced a mandatory multi-step prompt protocol. The AI is now required to assess specific landmarks (Heart Border, Hila, Diaphragms) **before** writing an impression. This structural constraint physically prevents the model from hallucinating findings contradicted by the scan.
*   **Clinical Data Injection**: By passing symptoms via `Form` data, I enabled "context-aware" vision. The AI now interprets the *same* visual opacity differently based on whether the patient presents with a fever (suggesting pneumonia) or is asymptomatic (suggesting a possible nodule/mass).
*   **Model Hardening**: I moved to `gemini-1.5-pro` for its superior visual reasoning capabilities, ensuring higher fidelity in distinguishing between subtle pathologies.

## 3. Technology Stack
*   **Backend**: FastAPI, SQLModel
*   **AI Engine**: Google Gemini 2.5 Flash 
*   **Image Processing**: Pillow (PIL)
*   **Database**: SQLite (SQLModel)
*   **Frontend**: Streamlit

## 4. Project Structure
```text
medical-vision-api/
├── app/                  # FastAPI Backend Logic
│   ├── ai_service.py     # Core logic for CoT prompting
│   ├── database.py       # SQLModel connection setup
│   ├── main.py           # API endpoints & Form handling
│   └── models.py         # ChatSession & ChatMessage schemas
├── frontend/             # Frontend Interface
│   ├── app.py            # Streamlit entry point
│   └── utils.py          # API request helper functions
├── .env                  # API key management
├── requirements.txt      # Project dependencies
└── README.md             # Project documentation
```

## 5. Future Roadmap

*   **Explainable AI (XAI)**: Implementing visual attention maps to overlay on the X-ray, highlighting exactly pixels triggered a specific diagnostic finding.
*   **Native DICOM Processing**: Upgrading from web formats (JPEG/PNG) to medical-grade DICOM files to preserve full 16-bit grayscale depth for superior nodule detection.
*   **Differential Diagnosis**: Automating a ranked list of alternative diagnoses to reduce cognitive bias in automated reporting.
*   **Temporal Comparison**: Integrating with hospital databases to pull past patient imaging, allowing the AI to identify if a lesion has grown or changed over time.