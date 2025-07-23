
import os
import json
import re  
from groq import Groq
import pandas as pd

# IMPORTANT: Ensure all your plotting functions are imported
from utils.plotting import (
    create_line_chart, 
    create_bar_chart, 
    create_asset_liability_chart,
    create_growth_chart
)

# ... (REQUIRED_KEYS and groq_client initialization remain the same) ...
REQUIRED_KEYS = [
    "Revenue from Operations", "Other Income", "Total Income", "Profit Before Tax",
    "Net Profit", "Total Equity", "Total Assets", "Total Liabilities",
    "Non-current assets", "Current assets", "Non-current liabilities",
    "Current liabilities", "Cash and cash equivalents", "Earnings Per Share (Basic)"
]
groq_client = Groq()

# --- FUNCTION 1: DATA EXTRACTION (Replaces structure_data_with_gemini) ---
def structure_data_with_groq(text, year):
    """
    Extracts structured financial data from text using a Groq model.
    """
    # Llama 3 8B is extremely fast and great for structured data extraction.
    model_name = "llama3-8b-8192"

    prompt = f"""
    Analyze the following text from a single page of a financial report for the year {year}.
    Your task is to extract the specified financial metrics.

    Follow these rules strictly:
    1.  Return ONLY a single, valid JSON object. Do not include any other text, explanations, or markdown.
    2.  The JSON object must contain these exact keys: {', '.join(REQUIRED_KEYS)}.
    3.  Be flexible with labels: "Revenue from Operations" might appear as "Income from sales" or similar variations. Map them correctly.
    4.  If a value for a specific key cannot be found ON THIS PAGE, the value in the JSON must be `null`. Do not guess or make up values.
    5.  All numerical values must be in a raw number format (e.g., 123456.78). Remove all commas, currency symbols, and text like "Cr.".
    6.  Pay close attention to negative numbers, often in parentheses, e.g., (123.45). Convert them to negative numbers, e.g., -123.45.
    7.  The report might be for a consolidated or standalone entity. Extract the data that is most prominently displayed.

    Financial Report Page Text:
    ---
    {text}
    ---
    """

    try:
        response = groq_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a highly accurate data extraction bot. Your only output should be a single, valid JSON object based on the user's request."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0, # Lower temperature for factual tasks
            response_format={"type": "json_object"} # This forces the model to output valid JSON
        )
        # The response is now in a standard format
        json_str = response.choices[0].message.content
        data = json.loads(json_str)

        # Ensure all required keys are present, even if null
        for key in REQUIRED_KEYS:
            if key not in data:
                data[key] = None

        return data
    except Exception as e:
        print(f"Error during Groq extraction or JSON parsing: {e}")
        # Add the response content to the error if it exists for debugging
        response_text = "No response from API."
        if 'response' in locals() and hasattr(response, 'choices') and len(response.choices) > 0:
            response_text = response.choices[0].message.content
        return {"error": f"JSON parsing failed: {str(e)}", "details": response_text}


# --- FUNCTION 2: PDF PROCESSING (Minor change) ---
def process_pdf_pages(pages, year):
    """
    Processes a PDF page by page, intelligently merging the results.
    """
    final_data = {key: None for key in REQUIRED_KEYS}

    for i, page_text in enumerate(pages):
        print(f"Processing page {i + 1}/{len(pages)}...")
        combined_text = page_text
        if i + 1 < len(pages):
            combined_text += "\n\n--- NEXT PAGE CONTEXT ---\n\n" + pages[i+1]
        
        # We limit context, but Llama3 8B has an 8K token window, so we can be generous.
        # CHANGED: Call the new Groq function
        extracted_data = structure_data_with_groq(combined_text[:30000], year)

        if "error" not in extracted_data:
            for key, value in extracted_data.items():
                if final_data.get(key) is None and value is not None:
                    final_data[key] = value

    if all(value is None for value in final_data.values()):
        return {"error": "Could not extract any required financial data. The document might not be a financial report, or the data is in a format the AI could not read."}

    return final_data

# --- FUNCTION 3: CONVERSATIONAL AGENT SETUP (UPDATED PROMPT) ---
def get_initial_chat_messages(company_name, data_summary):
    """
    Creates a more forceful and clearer system prompt.
    """
    # --- SOLUTION: A stronger, more direct prompt ---
    system_prompt = f"""
    You are FinAnalyst, an AI financial analyst. Your goal is to help a top executive from {company_name} understand their company's performance.

    Your Core Directives:
    1.  **Analyze and Interpret**: Provide concise, insightful analysis. Identify trends, risks, and opportunities.
    2.  **TOOL USAGE IS MANDATORY**: When the user's query can be answered with a visualization (like showing a trend, growth, or comparison), you MUST use your plotting tool.
    
    **TOOL SCHEMA**: To use the plotting tool, your ENTIRE response MUST be a single, valid JSON object that looks exactly like this:
    ```json
    {{
      "message": "Your textual analysis and explanation of the plot goes here.",
      "plot_request": {{
        "type": "line | bar | asset_liability_comparison | growth",
        "metric": "Metric Name from the data table",
        "title": "A descriptive title for the chart"
      }}
    }}
    ```
    - Use the "growth" type for any "year-over-year growth" or "growth rate" questions.
    - If no plot is needed, respond with plain text only.

    Available Financial Data:
    ---
    {data_summary}
    ---
    """
    chat_history = [{"role": "system", "content": system_prompt}]
    return chat_history


# --- FUNCTION 4: GETTING A RESPONSE (ROBUST PARSING) ---
def get_groq_response(chat_history, prompt, df):
    """
    Gets a response from Groq with robust JSON parsing for plots.
    """
    model_name = "llama3-8b-8192" 
    chat_history.append({"role": "user", "content": prompt})

    try:
        response = groq_client.chat.completions.create(
            model=model_name,
            messages=chat_history,
            temperature=0.1, # Keep temperature low for reliable tool use
        )
        response_text = response.choices[0].message.content
        
        # --- IMPORTANT: Add this for debugging! ---
        print("\n--- RAW AI RESPONSE ---\n")
        print(response_text)
        print("\n--- END RAW AI RESPONSE ---\n")
        
        chat_history.append({"role": "assistant", "content": response_text})

    except Exception as e:
        print(f"Error getting response from Groq: {e}")
        return {"message": "Sorry, I encountered an error connecting to the AI model.", "plot": None}, chat_history

    final_response = {"message": None, "plot": None}
    
    # --- SOLUTION: Robust JSON extraction logic ---
    try:
        # Check if the AI intended to send a plot request
        if "plot_request" in response_text:
            # Use regex to find the JSON object, even if it's surrounded by text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                request_data = json.loads(json_str)
                
                final_response["message"] = request_data.get("message")
                plot_info = request_data.get("plot_request")

                if plot_info:
                    plot_type = plot_info.get("type")
                    metric = plot_info.get("metric")
                    title = plot_info.get("title")

                    # The rest of your plotting logic is perfect.
                    if plot_type in ["line", "bar"] and metric and metric in df['metric'].unique():
                        plot_df = df[df['metric'] == metric].sort_values('year')
                        if plot_type == "line":
                            final_response["plot"] = create_line_chart(plot_df, 'year', 'value', title)
                        else:
                            final_response["plot"] = create_bar_chart(plot_df, 'year', 'value', title)
                    
                    elif plot_type == "asset_liability_comparison":
                        final_response["plot"] = create_asset_liability_chart(df)
                    
                    elif plot_type == "growth" and metric and metric in df['metric'].unique():
                        final_response["plot"] = create_growth_chart(df, metric, title)
            else:
                # Could not find a JSON block, so treat it as plain text.
                 final_response["message"] = response_text
        else:
            # No plot request was intended, treat as plain text.
            final_response["message"] = response_text
    
    except Exception as e:
        # If anything goes wrong, default to showing the raw text.
        print(f"Error during plot processing. Displaying raw text. Error: {e}")
        final_response["message"] = response_text

    return final_response, chat_history