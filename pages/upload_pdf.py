# pages/2_📤_Upload_Report.py
import streamlit as st
import os
from utils.auth import check_login, logout_button
from utils.database import get_all_companies, save_financial_data
from utils.llm_helper import process_pdf_pages,process_pdf_pages
from utils.pdf_processor import extract_pages_from_pdf

# --- PAGE SETUP & AUTHENTICATION ---
st.set_page_config(page_title="Upload Report", page_icon="📤", layout="wide")
check_login()
logout_button()

# --- ROLE-BASED ACCESS CONTROL (THE NEW METHOD) ---
if st.session_state['role'] != 'analyst':
    st.error("🔒 Access Denied")
    st.warning("You do not have permission to view this page. Please log in as an Analyst.")
    st.stop()  # Stop executing the rest of the page

# --- PAGE CONTENT (Only runs if the user is an analyst) ---
st.title("📤 Upload Financial Report")
st.write("Analysts can upload annual financial reports in PDF format here.")

# --- FORM FOR UPLOAD ---
with st.form("upload_form", clear_on_submit=True):
    companies = get_all_companies()
    company_options = {c['name']: c['id'] for c in companies}
    
    selected_company_name = st.selectbox("Select Company", options=company_options.keys())
    year = st.number_input("Enter the Financial Year (e.g., 2023)", min_value=1990, max_value=2050, step=1, value=2023)
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    submitted = st.form_submit_button("Process and Save Data")


if submitted and uploaded_file is not None and year and selected_company_name:
    company_id = company_options[selected_company_name]
    
    with st.spinner(f"Processing '{uploaded_file.name}' for {year}... This may take several minutes."):
        save_path = os.path.join("data", uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # 1. Extract text page by page
        st.info("Step 1: Extracting text from PDF (page by page)...")
        pages = extract_pages_from_pdf(save_path)

        if not pages:
            st.error("Failed to extract any text from the PDF. The document might be scanned, encrypted or corrupted.")
            os.remove(save_path)
            st.stop()
        
        st.success(f"Text extraction complete. Found {len(pages)} pages with text.")

        # 2. Analyze pages with AI
        st.info("Step 2: Analyzing pages with AI to extract financial data...")
        # --- USE THE NEW FUNCTION ---
        financial_data = process_pdf_pages(pages, year) 

        os.remove(save_path)
        
        if "error" in financial_data:
            st.error(f"AI Analysis Failed: {financial_data['error']}")
        else:
            st.info("Step 3: Saving extracted data to the database...")
            save_financial_data(company_id, year, financial_data, uploaded_file.name)
            st.success(f"Successfully processed and saved data for {selected_company_name} for {year}.")
            st.balloons()
            st.subheader("Extracted Data:")
            st.json(financial_data)