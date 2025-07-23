import streamlit as st
import pandas as pd
from utils.auth import check_login, logout_button
from utils.database import get_user_accessible_companies, get_company_financials
from utils.llm_helper import get_initial_chat_messages, get_groq_response

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="AI Financial Analyst", page_icon="🤖", layout="wide")

# --- 2. AUTHENTICATION ---
check_login()
logout_button()

# --- 3. PAGE HEADER ---
st.title("🤖 AI Financial Analyst")
st.markdown("Select a company to review its financial snapshot and receive expert analysis from your AI partner.")
st.divider()

# --- 4. DATA LOADING AND SELECTION ---
user_id = st.session_state["user_id"]
role = st.session_state["role"]
accessible_companies = get_user_accessible_companies(user_id, role)

if not accessible_companies:
    st.warning("You do not have access to any companies. Please contact an administrator.")
    st.stop()

# Create a dictionary for easy lookup of company names to IDs
company_options = {c['name']: c['id'] for c in accessible_companies}

selected_company_name = st.selectbox(
    "Select a Company to Analyze",
    options=company_options.keys(),
    index=0 # Default to the first company in the list
)

# --- 5. MAIN APPLICATION LOGIC ---
if selected_company_name:
    selected_company_id = company_options[selected_company_name]
    
    # Fetch financial data for the selected company
    financial_records = get_company_financials(selected_company_id)
    
    if not financial_records:
        st.error(f"No financial data found for {selected_company_name}. Please upload a financial report for this company first.")
    else:
        # Convert data to a DataFrame for analysis and plotting
        df = pd.DataFrame(financial_records, columns=['year', 'metric', 'value'])
        
        # Display the main financial snapshot
        st.header(f"Financial Snapshot: {selected_company_name}")
        
        # Use a pivot table for a clean, year-by-year comparison
        snapshot_df = df.pivot_table(index='metric', columns='year', values='value').sort_index()
        st.dataframe(snapshot_df.style.format("{:,.2f}", na_rep="-"), use_container_width=True)

        st.divider()

        # --- 6. CHAT INTERFACE ---
        st.header("💬 Chat with your AI Analyst")

        # Initialize chat history. This is CRITICAL for the stateless Groq API.
        # It resets the chat if the user selects a new company.
        if "chat_history" not in st.session_state or st.session_state.get("company_id") != selected_company_id:
            st.info(f"Analyst is now focused on {selected_company_name}. Ask a question to begin.")
            data_summary = snapshot_df.to_string()
            # Get the initial system prompt and message list from our helper
            st.session_state.chat_history = get_initial_chat_messages(selected_company_name, data_summary)
            # This separate list stores messages for display purposes (without the long system prompt)
            st.session_state.messages_for_display = []
            st.session_state.company_id = selected_company_id

        # Display past chat messages
        for message in st.session_state.messages_for_display:
            with st.chat_message(message["role"]):
                # Handle messages that contain text, plots, or both
                if "content" in message and message["content"]:
                    st.markdown(message["content"])
                if "plot" in message and message["plot"]:
                    st.plotly_chart(message["plot"], use_container_width=True)

        # React to user input
        if prompt := st.chat_input(f"Ask about {selected_company_name}'s performance..."):
            # Add user's message to the display list and render it
            st.session_state.messages_for_display.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get the AI's response
            with st.chat_message("assistant"):
                with st.spinner("The AI Analyst is preparing your briefing..."):
                    # Call the Groq helper function
                    # It takes the full history and returns the response AND the updated history
                    response_data, updated_history = get_groq_response(
                        st.session_state.chat_history, 
                        prompt, 
                        df
                    )
                    
                    # IMPORTANT: Update the full chat history in session state
                    st.session_state.chat_history = updated_history
                    
                    # Prepare the bot's complete message (text + plot) for display
                    bot_message_for_display = {"role": "assistant"}
                    
                    if "message" in response_data and response_data["message"]:
                        st.markdown(response_data["message"])
                        bot_message_for_display["content"] = response_data["message"]
                    
                    if "plot" in response_data and response_data["plot"]:
                        st.plotly_chart(response_data["plot"], use_container_width=True)
                        bot_message_for_display["plot"] = response_data["plot"]
                    
                    # Add the complete bot message to the display history
                    st.session_state.messages_for_display.append(bot_message_for_display)