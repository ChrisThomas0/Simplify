import re
import os

import fitz
import nltk
import openai
import pdfplumber
import pytesseract
import pandas as pd
from PyPDF2 import PdfReader
from nltk.corpus import stopwords
from pdf2image import convert_from_path
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')


def extract_pdf_from_image(path):
    pages = convert_from_path(path)
    whole_doc = ""
    for page in pages:
        whole_doc += pytesseract.image_to_string(page)
    return whole_doc


def extract_from_pdf(file):
    whole_doc = ''
    reader = PdfReader(file)
    total_pages = len(reader.pages)

    for i in range(0, total_pages):
        current_page = reader.pages[i]
        whole_doc += current_page.extract_text()
    return whole_doc


def extract_from_text(file_path):
    file = open(file_path, 'rb')
    file_contents = file.readlines()
    whole_doc = ""
    for contents in file_contents:
        if isinstance(contents, bytes):
            whole_doc += contents.decode("latin-1")
        else:
            whole_doc += contents
        whole_doc += " "
    return whole_doc


def preprocess(content):
    content = content.replace("\n", " ")
    return content


def divide_into_sentence_chunks(text, chunk_size):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


def invoke_gpt_api(model, messages):
    model_response = ""
    for response in openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": message["role"], "content": message["content"]}
                for message in messages
            ],
            temperature=0.1,
            max_tokens=300,
            stream=True,
    ):
        model_response += response.choices[0].delta.get("content", "")
    return model_response


def tokenize_and_remove_stop_words(input_query):
    words = word_tokenize(input_query)
    stop_words = set(stopwords.words('english'))

    filtered_words = [word for word in words if word.lower() not in stop_words]
    filtered_words = " ".join(words for words in filtered_words)
    return filtered_words


def compute_total_words(content):
    splitted_content = content.split()
    return len(splitted_content)


def create_db_directory(path, project_name):
    db_directory = os.path.join(path, project_name)
    if not os.path.isdir(db_directory):
        os.mkdir(db_directory)
        return True
    else:
        return False


def save_uploaded_files(files, directory):
    for file in files:
        file_path = os.path.join(directory, file.name)
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
    return "Files saved successfully."


def map_file_type(file_type):
    mime_mapper = {
        'application/pdf': 'PDF',
        'text/plain': 'TXT',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'XLSX'
    }
    return mime_mapper[file_type]


def create_meta_data(files, directory):
    document_contents = ""
    meta_data = {}

    for file in files:
        mapped_file_type = map_file_type(file.type)
        if file.type.lower() == 'application/pdf':
            document_contents = extract_pdf_from_image(directory + "/" + file.name)
        if file.type.lower() == 'text/plain':
            document_contents = extract_from_text(directory + "/" + file.name)
        document_word_length = compute_total_words(document_contents)

        """
        1. Get the document contents check if its pdf/txt
        2. Get the classification terms
        3. Create a prompt to classify the documents
        4. Update the variable for display purposes
        """

        meta_data[file.name] = {
            'file_name': file.name,
            'file_type': mapped_file_type,
            'full_contents': document_contents,
            'display_contents': document_contents[:100] + '...',
            'total_words': document_word_length,
            'character_length': len(document_contents),
            'classification': "Classification from GPT"
        }

    meta_data = pd.DataFrame.from_dict(meta_data, orient='index')
    meta_data.to_excel(directory + '/Project_Meta_Data.xlsx', index=False)
    return True


def pymu_pdf(file_path):
    doc = fitz.open(file_path)
    print(f'Document is {doc}')
    for page in doc:
        text = page.get_text()
    return text


def pdf_plumber(file_path):
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
    return text
