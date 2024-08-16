import streamlit as st
import requests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from BEES_CHAT_UI.SourceCode.GetSessionDetails import get_ip_related_details
from BEES_CHAT_UI.SourceCode.GetSessionDetails import get_session_details
import warnings
from datetime import datetime, timedelta
from BEES_CHAT_UI.SourceCode.CSS import css_selector
from BEES_CHAT_UI.SourceCode.CSS import custom_js
from BEES_CHAT_UI.SourceCode.PDFChat import fileUpload
# Current date
from streamlit_javascript import st_javascript
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
current_date = datetime.now().strftime('%Y-%m-%d')

# Previous date (yesterday) in yyyy-mm-dd format
previous_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
warnings.filterwarnings("ignore", category=DeprecationWarning)


def call_api(user_message, ip, session_id):
    # Mockoon API endpoint (replace with your actual URL)
    api_url = f"http://{os.environ.get('local_link')}/api/chat"

    # Send POST request with user message as data
    data = {"query": user_message, "ip_address": ip,
            "session_id": session_id}
    headers = {"Authorization": f"{os.environ.get('chat_access_token')}"}
    response = requests.post(api_url, json=data, headers=headers)
    # Check for successful response
    if response.status_code == 200:
        return response.json()  # Extract response message
    else:
        return "API Error: " + str(response.status_code)


def get_ip():
    url = 'https://api.ipify.org?format=json'
    script = (f'await fetch("{url}"). then('
              f'function(response) {{'
              f'return response.json();'
              f'}})')
    try:
        result = st_javascript(script)
        if isinstance(result, dict) and 'ip' in result:
            return result['ip']
    except:
        pass
    return None


def main():
    st.set_page_config(page_title="BEES Chat", page_icon=":books:")
    ip = '74.225.252.130'
    # ip = get_ip()
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
        st.session_state.chat_history = []
        st.session_state.new_chat = True
    # if 'new_chat' not in st.session_state:
    #     st.session_state.new_chat = False
    if not st.session_state.new_chat:
        st.session_state.chat_history = []
    if "link_clicked" not in st.session_state:
        st.session_state.link_clicked = False
    if "success_upload" not in st.session_state:
        st.session_state.success_upload = False
    try:
        chat_history_json_response = get_ip_related_details(ip)
    except:
        chat_history_json_response = []
    st.markdown(css_selector, unsafe_allow_html=True)
    st_javascript(custom_js)
    base_url = st_javascript('window.location.origin')
    # base_url = base_url + '/File_Upload'
    # print("Base Url :", base_url)
    uploaded_files = st.file_uploader("Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
    if st.button("Upload"):
        st.query_params.clear()
        st.session_state.session_id = None
        st.session_state.chat_history = []
        if fileUpload(uploaded_files):
            st.session_state.success_upload = True
            st.success(f"Files Processed successfully.Now you can chat.")
            st.session_state.new_chat = True


if __name__ == "__main__":
    main()
