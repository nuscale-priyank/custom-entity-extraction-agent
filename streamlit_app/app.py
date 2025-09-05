x#!/usr/bin/env python3
"""
Streamlit Application for Custom Entity Extraction Agent
Interacts with the FastAPI backend to test the agent end-to-end
"""

import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Configuration
FASTAPI_BASE_URL = "http://localhost:8001"
API_ENDPOINTS = {
    "health": f"{FASTAPI_BASE_URL}/health",
    "chat": f"{FASTAPI_BASE_URL}/chat",
    "context_providers": f"{FASTAPI_BASE_URL}/context-providers"
}

def load_mock_data():
    """Load mock BC3 and data asset data"""
    try:
        # Load BC3 segments
        with open("../mock_data/bc3_segments.json", "r") as f:
            bc3_segments = json.load(f)
        
        # Load data assets
        with open("../mock_data/data_assets.json", "r") as f:
            data_assets = json.load(f)
        
        return bc3_segments, data_assets
    except Exception as e:
        st.error(f"Error loading mock data: {e}")
        return [], []

def check_api_health():
    """Check if the FastAPI backend is running"""
    try:
        response = requests.get(API_ENDPOINTS["health"], timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"API returned status {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {e}"

def send_chat_message(message, session_id, selected_bc3_fields=None, selected_asset_columns=None):
    """Send a chat message to the agent with selected BC3 fields and asset columns"""
    try:
        payload = {
            "message": message,
            "session_id": session_id,
            "context_provider": "credit_domain"
        }
        
        # Add selected BC3 fields if any
        if selected_bc3_fields:
            payload["selected_bc3_fields"] = selected_bc3_fields
        
        # Add selected asset columns if any
        if selected_asset_columns:
            payload["selected_asset_columns"] = selected_asset_columns
        
        response = requests.post(
            API_ENDPOINTS["chat"],
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"API returned status {response.status_code}: {response.text}"
    
    except requests.exceptions.RequestException as e:
        return False, f"Request error: {e}"

def display_bc3_field_selection(segments):
    """Display BC3 segments with individual field selection"""
    if not segments:
        st.info("No BC3 segments available")
        return []
    
    st.subheader("📊 BC3 Field Selection")
    st.write("Select individual business dictionary fields from each segment:")
    
    selected_fields = []
    
    for segment in segments:
        with st.expander(f"**{segment['segment_name']}** ({len(segment.get('business_dictionary', []))} fields)", expanded=False):
            if 'business_dictionary' in segment:
                for field in segment['business_dictionary']:
                    # Create a unique key for each field
                    field_key = f"bc3_{segment['segment_name']}_{field['uuid']}"
                    
                    # Checkbox for field selection
                    if st.checkbox(
                        f"**{field['description']}** - {field['definition'][:50]}...",
                        key=field_key,
                        help=f"UUID: {field['uuid']}\nNotes: {field.get('notes', 'N/A')}"
                    ):
                        # Add segment context to the selected field
                        selected_field = {
                            "field": field,
                            "segment_context": {
                                "segment_name": segment['segment_name'],
                                "segment_type": "bc3"
                            }
                        }
                        selected_fields.append(selected_field)
                        
                        # Show field details
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Definition:** {field['definition']}")
                            st.write(f"**Known Implementations:** {', '.join(field.get('known_implementations', []))}")
                        with col2:
                            st.write(f"**Valid Values:** {', '.join(field.get('valid_values', []))}")
                            st.write(f"**Notes:** {field.get('notes', 'N/A')}")
                        
                        st.divider()
    
    return selected_fields

def display_asset_column_selection(assets):
    """Display data assets with individual column selection"""
    if not assets:
        st.info("No data assets available")
        return []
    
    st.subheader("🗄️ Asset Column Selection")
    st.write("Select individual columns from each data asset:")
    
    selected_columns = []
    
    for asset in assets:
        with st.expander(f"**{asset['asset_name']}** ({len(asset.get('columns', []))} columns)", expanded=False):
            # Asset-level information
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Workspace:** {asset['workspace_name']}")
                st.write(f"**BigQuery Table:** {asset['big_query_table_name']}")
            with col2:
                st.write(f"**Asset ID:** {asset['asset_id']}")
                st.write(f"**Asset Type:** Data Asset")
            
            st.divider()
            
            # Column selection
            if 'columns' in asset:
                for column in asset['columns']:
                    # Create a unique key for each column
                    column_key = f"asset_{asset['asset_name']}_{column['column']}"
                    
                    # Checkbox for column selection
                    if st.checkbox(
                        f"**{column['column_name']}** ({column['column']})",
                        key=column_key,
                        help=f"Column identifier: {column['column']}"
                    ):
                        # Add asset context to the selected column
                        selected_column = {
                            "column": column,
                            "asset_context": {
                                "asset_id": asset['asset_id'],
                                "asset_name": asset['asset_name'],
                                "workspace_name": asset['workspace_name'],
                                "big_query_table_name": asset['big_query_table_name'],
                                "asset_type": "data_asset"
                            }
                        }
                        selected_columns.append(selected_column)
                        
                        # Show column details
                        st.write(f"**Column Name:** {column['column_name']}")
                        st.write(f"**Column ID:** {column['column']}")
                        st.divider()
    
    return selected_columns

def display_selected_context(selected_bc3_fields, selected_asset_columns):
    """Display the selected context for the LLM"""
    st.subheader("🎯 Selected Context for Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if selected_bc3_fields:
            st.write(f"**BC3 Fields Selected:** {len(selected_bc3_fields)}")
            for field_data in selected_bc3_fields:
                field = field_data['field']
                segment = field_data['segment_context']
                st.write(f"• {field['description']} ({segment['segment_name']})")
        else:
            st.write("**BC3 Fields:** None selected")
    
    with col2:
        if selected_asset_columns:
            st.write(f"**Asset Columns Selected:** {len(selected_asset_columns)}")
            for column_data in selected_asset_columns:
                column = column_data['column']
                asset = column_data['asset_context']
                st.write(f"• {column['column_name']} ({asset['asset_name']})")
        else:
            st.write("**Asset Columns:** None selected")
    
    # Show combined context summary
    if selected_bc3_fields or selected_asset_columns:
        st.success(f"✅ Total context items selected: {len(selected_bc3_fields) + len(selected_asset_columns)}")
        st.info("💡 The LLM will analyze these combinations to extract relevant entities")
    else:
        st.warning("⚠️ No context selected. The agent will provide general guidance.")

def display_extracted_entities(entities):
    """Display extracted entities in a structured way"""
    if not entities:
        st.info("No entities extracted yet")
        return
    
    st.subheader("🔍 Extracted Entities")
    
    # Create a DataFrame for better visualization
    entity_data = []
    for entity in entities:
        entity_data.append({
            "Type": entity.get("entity_type", "Unknown"),
            "Name": entity.get("entity_name", "Unknown"),
            "Value": entity.get("entity_value", "Unknown"),
            "Confidence": f"{entity.get('confidence', 0):.2f}",
            "Source": entity.get("source_field", "Unknown"),
            "Context": entity.get("context_provider", "Unknown")
        })
    
    df = pd.DataFrame(entity_data)
    st.dataframe(df, use_container_width=True)
    
    # Create a pie chart of entity types
    if entity_data:
        entity_counts = df['Type'].value_counts()
        fig = px.pie(
            values=entity_counts.values,
            names=entity_counts.index,
            title="Entity Types Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

def display_chat_history(chat_state):
    """Display the chat conversation history"""
    if not chat_state or not chat_state.get("messages"):
        st.info("No chat history yet")
        return
    
    st.subheader("💬 Chat History")
    
    for message in chat_state["messages"]:
        if message.get("role") == "user":
            st.chat_message("user").write(message.get("content", ""))
        elif message.get("role") == "assistant":
            st.chat_message("assistant").write(message.get("content", ""))

def display_fastapi_logs():
    """Display FastAPI logs in real-time"""
    st.subheader("📋 FastAPI Logs")
    
    # Add log controls
    col1, col2 = st.columns([2, 1])
    with col1:
        log_lines = st.slider("Number of log lines", min_value=10, max_value=200, value=50, step=10)
    with col2:
        if st.button("🔄 Refresh Logs"):
            st.rerun()
    
    # Try to get logs from FastAPI
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/logs?lines={log_lines}", timeout=5)
        
        if response.status_code == 200:
            log_data = response.json()
            
            # Display log file info
            st.write(f"**Log File:** {log_data.get('log_file', 'N/A')}")
            st.write(f"**Total Lines:** {log_data.get('total_lines', 0)}")
            st.write(f"**Last Updated:** {log_data.get('timestamp', 'N/A')}")
            
            # Display recent logs
            recent_lines = log_data.get('recent_lines', [])
            if recent_lines:
                st.subheader(f"📝 Recent Logs (Last {len(recent_lines)} lines)")
                
                # Create a text area for logs with syntax highlighting
                log_text = "".join(recent_lines)
                st.text_area(
                    "FastAPI Logs",
                    value=log_text,
                    height=300,
                    help="Recent FastAPI application logs"
                )
                
                # Add download button
                if st.button("📥 Download Logs"):
                    st.download_button(
                        label="Download Log File",
                        data=log_text,
                        file_name=f"fastapi_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
            else:
                st.info("No logs available. The FastAPI server may not have generated any logs yet.")
                
        else:
            st.error(f"Failed to fetch logs: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to FastAPI: {e}")
        st.info("""
        **To view FastAPI logs manually:**
        
        1. **Terminal Output**: Check the terminal where you started `python main.py --port 8000`
        2. **Log Files**: Check for `fastapi.log` in the project directory
        3. **Real-time Monitoring**: Use `tail -f fastapi.log` for live monitoring
        """)

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="Custom Entity Extraction Agent",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🤖 Custom Entity Extraction Agent")
    st.markdown("Test the agent end-to-end with selective BC3 fields and asset columns")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Health Check
        st.subheader("🔌 API Status")
        if st.button("Check API Health"):
            is_healthy, health_info = check_api_health()
            if is_healthy:
                st.success("✅ API is running")
                st.json(health_info)
            else:
                st.error(f"❌ API is not accessible: {health_info}")
        
        # Session Management
        st.subheader("🆔 Session Management")
        session_id = st.text_input(
            "Session ID",
            value=f"streamlit_session_{int(time.time())}",
            help="Unique identifier for this chat session"
        )
        
        if st.button("New Session"):
            session_id = f"streamlit_session_{int(time.time())}"
            st.rerun()
        
        st.info(f"Current Session: `{session_id}`")
        
        # Data Selection Summary
        st.subheader("📊 Selection Summary")
        
        # Load mock data
        bc3_segments, data_assets = load_mock_data()
        
        st.write(f"**Available BC3 Segments:** {len(bc3_segments)}")
        st.write(f"**Available Data Assets:** {len(data_assets)}")
        
        # Show available data counts
        total_bc3_fields = sum(len(seg.get('business_dictionary', [])) for seg in bc3_segments)
        total_asset_columns = sum(len(asset.get('columns', [])) for asset in data_assets)
        
        st.write(f"**Total BC3 Fields:** {total_bc3_fields}")
        st.write(f"**Total Asset Columns:** {total_asset_columns}")
    
    # Main content area - Chat Interface on the left
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat with Agent")
        
        # Chat input
        user_message = st.chat_input("Type your message here...")
        
        if user_message:
            # Display user message
            st.chat_message("user").write(user_message)
            
            # Get selected context from session state
            selected_bc3_fields = st.session_state.get('selected_bc3_fields', [])
            selected_asset_columns = st.session_state.get('selected_asset_columns', [])
            
            # Send to agent with selected context
            with st.spinner("🤖 Agent is analyzing the selected context..."):
                # Add a progress bar for better UX
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulate progress
                for i in range(100):
                    time.sleep(0.01)
                    progress_bar.progress(i + 1)
                    if i < 30:
                        status_text.text("🔄 Initializing agent...")
                    elif i < 60:
                        status_text.text("🧠 Analyzing selected context...")
                    elif i < 90:
                        status_text.text("🔍 Extracting relevant entities...")
                    else:
                        status_text.text("✅ Finalizing response...")
                
                # Send actual request
                success, response = send_chat_message(
                    user_message, 
                    session_id, 
                    selected_bc3_fields, 
                    selected_asset_columns
                )
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
            
            if success:
                # Display agent response
                st.chat_message("assistant").write(response.get("response", "No response"))
                
                # Store response for display
                st.session_state.last_response = response
                
                # Show success message
                st.success("✅ Message processed successfully!")
                
            else:
                st.error(f"❌ Error: {response}")
        
        # Display chat history and response details
        if 'last_response' in st.session_state:
            response = st.session_state.last_response
            
            # Display metadata
            st.subheader("📊 Response Metadata")
            metadata = response.get("metadata", {})
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Session ID:** {metadata.get('session_id', 'N/A')}")
            with col2:
                st.write(f"**Processing Time:** {response.get('processing_time', 0):.2f}s")
            with col3:
                st.write(f"**Confidence:** {response.get('confidence_score', 0):.2f}")
            
            # Display extracted entities
            entities = response.get("extracted_entities", [])
            display_extracted_entities(entities)
            
            # Display chat state
            chat_state = response.get("chat_state", {})
            display_chat_history(chat_state)
    
    # Right column - Data Selection and Context
    with col2:
        st.header("📊 Data Selection & Context")
        
        # Load mock data
        bc3_segments, data_assets = load_mock_data()
        
        # BC3 Field Selection
        selected_bc3_fields = display_bc3_field_selection(bc3_segments)
        
        # Asset Column Selection
        selected_asset_columns = display_asset_column_selection(data_assets)
        
        # Store selections in session state
        st.session_state.selected_bc3_fields = selected_bc3_fields
        st.session_state.selected_asset_columns = selected_asset_columns
        
        # Display selected context
        display_selected_context(selected_bc3_fields, selected_asset_columns)
        
        # FastAPI Logs
        st.divider()
        display_fastapi_logs()
    
    # Instructions
    st.header("📖 How to Use")
    
    with st.expander("Click to see instructions", expanded=False):
        st.markdown("""
        ### 🚀 Getting Started
        
        1. **Check API Health**: Make sure the FastAPI backend is running on port 8000
        2. **Select Context**: Choose specific BC3 fields and asset columns from the right panel
        3. **Start Chatting**: Type messages in the chat input to interact with the agent
        
        ### 💡 Example Messages
        
        - "Hello! Can you help me extract entities from the selected context?"
        - "What entities can you find in the selected BC3 fields and asset columns?"
        - "Analyze the relationship between the selected BC3 fields and asset columns"
        - "Extract business entities based on the selected context combinations"
        
        ### 🔍 Context Selection
        
        - **BC3 Fields**: Select individual business dictionary fields from each segment
        - **Asset Columns**: Select specific columns from each data asset
        - **Combined Analysis**: The LLM will analyze the relationships between selected items
        
        ### 🔧 Troubleshooting
        
        - **API Connection Issues**: Make sure the FastAPI server is running (`python main.py --port 8000`)
        - **No Response**: Check the API health status in the sidebar
        - **Data Loading Issues**: Verify the mock data files exist in the `mock_data/` directory
        - **View Logs**: Check the terminal where you started the FastAPI server
        
        ### 📁 File Structure
        
        ```
        bc3_ai_agent/
        ├── main.py              # FastAPI server
        ├── streamlit_app/       # This Streamlit app
        ├── mock_data/           # Mock BC3 and asset data
        └── ...
        ```
        """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Custom Entity Extraction Agent** - Built with LangGraph, Vertex AI, and Streamlit"
    )

if __name__ == "__main__":
    main()
