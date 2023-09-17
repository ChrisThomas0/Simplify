import streamlit as st
from PyPDF2 import PdfReader
from docquery import document, pipeline


def extract_pdf(file):
    whole_doc = ''
    reader = PdfReader(file)
    total_pages = len(reader.pages)

    for i in range(0, total_pages):
        print(f'Processing {i} page')
        current_page = reader.pages[i]
        whole_doc += current_page.extract_text()
    return whole_doc


def doc_query_qa(file, questions_array):
    p = pipeline('document-question-answering')
    doc = document.load_document(file)

    for question in questions_array:
        answer = p(question=question, **doc.context)
        st.write('Answer obtained from DocQuery is', answer)


st.header('Simplify Application for LLM testing')

entire_doc_content = ''
questions_lists = []

file_input_path = st.text_input("Enter the file path to PDF file")

input_question_container = st.empty()

if file_input_path != '':
    st.write('The file path is - ', file_input_path)
    # st.write('Word length of the document is - ', len(entire_doc_content))
    input_questions = input_question_container.text_input("Enter the question")
    if input_questions != '':
        questions_lists.append(input_questions)
        doc_query_qa(file=file_input_path, questions_array=questions_lists)

# st.write('Entire document content is - ', whole_doc)
