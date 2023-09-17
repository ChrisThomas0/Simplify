import re
import os
import nltk
import openai
import pytesseract
import pandas as pd
import numpy as np
import openpyxl
from PyPDF2 import PdfReader
from nltk.corpus import stopwords
from pdf2image import convert_from_path
from nltk.tokenize import word_tokenize

nltk.download('punkt')
nltk.download('stopwords')

class Utils:


    @staticmethod
    def extract_pdf_from_image(path):
        pages = convert_from_path(path)
        whole_doc = ""
        for page in pages:
            whole_doc += pytesseract.image_to_string(page)
        return whole_doc


    @staticmethod
    def extract_with_easy_ocr(reader, file_path):
        content_string = ''
        images = convert_from_path(file_path, dpi=200)

        for i, image in enumerate(images):
            image_array = np.array(image)
            results = reader.readtext(image_array, detail=0,
                                      slope_ths=0.1, ycenter_ths=0.5,
                                      height_ths=0.5, width_ths=0.5,
                                      add_margin=0.1, x_ths=1.0,
                                      y_ths=0.5, paragraph=True)
            content_string += ' '.join(result for result in results)
        return content_string

    @staticmethod
    def extract_from_pdf(file):
        whole_doc = ''
        reader = PdfReader(file)
        total_pages = len(reader.pages)

        for i in range(0, total_pages):
            current_page = reader.pages[i]
            whole_doc += current_page.extract_text()
        return whole_doc

    @staticmethod
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

    @staticmethod
    def extract_from_excel(file_path):
        workbook = openpyxl.load_workbook(file_path)
        whole_doc = ""
        worksheet = workbook['Sheet1']

        for row in worksheet.iter_rows(values_only=True):
            row_data = "\t".join(str(cell) for cell in row)
            whole_doc += row_data + "\n"
        workbook.close()
        return whole_doc

    @staticmethod
    def preprocess(content):
        content = content.replace("\n", " ")
        return content

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def tokenize_and_remove_stop_words(input_query):
        words = word_tokenize(input_query)
        stop_words = set(stopwords.words('english'))

        filtered_words = [word for word in words if word.lower() not in stop_words]
        filtered_words = " ".join(words for words in filtered_words)
        return filtered_words

    @staticmethod
    def compute_total_words(content):
        splitted_content = content.split()
        return len(splitted_content)

    @staticmethod
    def map_file_type(file_type):
        mime_mapper = {
            'application/pdf': 'PDF',
            'text/plain': 'TXT',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'XLSX',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'DOCX'
        }
        return mime_mapper[file_type]

    @staticmethod
    def convert_to_csv(dataset):
        return dataset.to_csv(index=False).encode('utf-8')

