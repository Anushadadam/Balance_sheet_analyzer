# Balance Sheet Analyzer AI

A Streamlit-based financial analysis tool that uses LLMs to extract, analyze, and visualize structured financial data from company annual reports in PDF format. With built-in role-based access control, it enables different types of users—Analysts, CEOs, and Top Management—to securely log in and explore financial trends using AI assistance.

---

## Features

- Secure Login with Role-Based Access
  - Analyst: Upload PDFs and view all companies.
  - CEO: View their company's financials.
  - Top Management: View all companies under their group.
- AI-Powered Financial Analysis using Groq + LLaMA 3
- Interactive Visualizations with Plotly (Line, Bar, Growth, Asset-Liability charts)
- PDF Parsing using `pdfplumber`, page-by-page
- Natural Language Chat Interface for AI-based Q&A
- Structured Storage of extracted metrics in SQLite

---

## Tech Stack

| Component     | Tool / Library          |
|---------------|-------------------------|
| Frontend      | Streamlit               |
| AI / LLM      | Groq API with LLaMA 3   |
| PDF Parsing   | pdfplumber              |
| Database      | SQLite                  |
| Charts        | Plotly                  |
| OCR (Future)  | Tesseract (planned)     |

---

## Setup & Installation

1. Clone the Repository

```bash
git clone <your-repo-url>
cd balance_sheet_analyzer
```

2. Create & Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
```

3. Install Dependencies

```bash
pip install -r requirements.txt
```

4. Configure API Key

Create a `.env` file:

```
touch .env
```

Add your Groq API key:

```
GROQ_API_KEY="your_groq_api_key"
```

---

## Run the App

```bash
streamlit run app.py
```

Then open: http://localhost:8501

---

## Sample Users

| Role           | Username   | Password     |
|----------------|------------|--------------|
| Analyst        | analyst    | password123  |
| CEO (Jio)      | jio_ceo    | password123  |
| Top Management | ambani     | password123  |

---

## How It Works – Methodology

### 1. Role-Based Login

- Enforced using `session_state` and database verification.
- Access restricted via decorators like `check_role_access()`.

### 2. Page-by-Page PDF Text Extraction

- Uses `pdfplumber` to extract text from each page of the uploaded report.

### 3. AI-Based Financial Metric Extraction

- Each page’s text is sent to Groq API (LLaMA 3-8B).
- The model extracts key metrics (like Revenue, Profit, Assets, etc.) in strict JSON format.
- Only exact numeric values are accepted (e.g., no "N/A", commas, Cr., etc.)
- Extracted metrics are validated and saved to the database.

Why Groq?

- OpenAI and Gemini were tested.
- OpenAI GPT-4 had high latency and strict free-tier limits.
- Gemini 1.5 Flash was fast but only allowed limited requests.
- Groq with LLaMA 3 provided structured, reliable responses ideal for this use-case, with moderate latency and fewer restrictions.

### 4. Interactive Visual Insights

- Users can generate:
  - Line charts (trends)
  - Bar charts (year comparison)
  - YoY Growth charts
  - Assets vs. Liabilities comparisons

### 5. Conversational AI Assistance

- Users can ask questions like:
  - “How did revenue change in the last 3 years?”
  - “What are the biggest risks in this company’s financials?”
- The assistant replies with textual analysis and plots.

---

## Findings

- Structured financial data can be reliably extracted using LLMs if prompted properly.
- Role-based control ensures data confidentiality and proper segmentation.
- AI + Plotly offers intuitive visual storytelling for financial metrics.
- LLM services (OpenAI, Gemini) have limits; Groq is more consistent for structured JSON tasks.

---

## Future Enhancements

- Add OCR fallback for scanned PDFs using Tesseract.
- Add memory-based chat for smarter multi-turn conversations.
- Improve session security and password hashing.
- Add unit tests for database, auth, and AI extraction functions.

---
