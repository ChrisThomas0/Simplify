import warnings
import streamlit as st
from functions import *

warnings.filterwarnings("ignore")

# Open AI related information
API_KEY = "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"
ORG_KEY = "org-VUUQolpC4g6Xn0hYFeH534xT"
document_content = ''
document_batches = []
file = None

# Initialization of variables and model names
st.header('Simplify Application for LLM testing')
openai.api_key = API_KEY
openai.organization = ORG_KEY

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

input_format = st.radio(
    "Please select a option for dataset format",
    ('PDF/TXT', 'PDF Images'))

# Based on the radio button we call different functions
if input_format == 'PDF/TXT':
    file = st.file_uploader("Choose a PDF file", type=["pdf", "txt"])
    if file is not None:
        if file.type == 'application/pdf':
            document_content = extract_from_pdf(file)
        elif file.type == 'text/plain':
            document_content = extract_from_text(file)
elif input_format == 'PDF Images':
    file = st.text_input("Enter the file path")
    if len(file) > 0:
        document_content = extract_pdf_from_image(file)

batch_size = 3500
if len(document_content) > 0:
    document_content = preprocess(document_content)
    st.write('Dividing the dataset into batches')
    document_batches = divide_into_sentence_chunks(document_content, batch_size)
    st.write('Document is divided into chunks. Ready to chat!')
    st.write('Document batches', document_batches)

    if prompt := st.chat_input("Send a message"):
        if len(document_batches) == 1:
            input_query = prompt + " " + document_batches[0]
        else:
            input_query = " "
            pass
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": input_query})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            response = invoke_gpt_api(st.session_state["openai_model"],
                                      st.session_state.messages)
            message_placeholder.markdown(response + "▌")
            message_placeholder.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

