import easyocr

from utils import *
from init_environment_variables import *
import streamlit as st


class Project:

    def __init__(self):
        self.project_name = ""
        self.project_description = ""
        self.uploaded_files = None
        self.project_directory = ""

    def set_project_name(self, project_name):
        self.project_name = project_name

    def get_project_name(self):
        return self.project_name

    def set_project_description(self, project_description):
        self.project_description = project_description

    def get_project_description(self):
        return self.project_description

    def set_uploaded_files(self, files):
        self.uploaded_files = files

    def get_uploaded_files(self):
        return self.uploaded_files

    def set_project_directory(self, directory):
        self.project_directory = directory

    def get_project_directory(self):
        return self.project_directory

    def create_db_directory(self, db_path):
        db_directory = os.path.join(db_path, self.project_name)
        if not os.path.isdir(db_directory):
            os.mkdir(db_directory)
            return True
        else:
            return False

    def save_uploaded_files(self):
        try:
            for file in self.uploaded_files:
                file_path = os.path.join(self.get_project_directory(), file.name)
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())
            return True
        except [BufferError, FileNotFoundError, OSError]:
            return False

    def get_document_classification_categories(self):
        document_categories = [
            "Corporate Information", "Business and trading", "Properties", "Assets", "Licences and regulatory",
            "Intellectual property", "Finance", "Accounts", "Contractual arrangements", "Litigation", "Insurance",
            "Employees", "Data protection", "Environmental", "Connected persons", "General"]
        return document_categories

    def create_meta_data(self):
        meta_data = {}
        document_word_length = 0
        document_char_length = 0
        classification = "N/A"
        document_categories = self.get_document_classification_categories()

        for file in self.uploaded_files:
            mapped_file_type = Utils.map_file_type(file.type)
            if file.type.lower() == 'application/pdf':
                reader = easyocr.Reader(['en'], gpu=True, quantize=True)
                # document_contents = Utils.extract_pdf_from_image(self.get_project_directory() + "/" + file.name)
                document_contents = Utils.extract_with_easy_ocr(reader, self.get_project_directory() + "/" + file.name)
            elif file.type.lower() == 'text/plain':
                document_contents = Utils.extract_from_text(self.get_project_directory() + "/" + file.name)
            elif mapped_file_type == "XLSX":
                document_contents = Utils.extract_from_excel(self.get_project_directory() + "/" + file.name)
            else:
                document_contents = "No parser found"

            if document_contents != "No parser found":
                document_word_length = Utils.compute_total_words(document_contents)
                document_char_length = len(document_contents)
                category_classification_prompt = "[PROMPT] Predict the most suitable category and return only the " \
                                                 "category name for the given document from the following list " \
                                                 + str(document_categories) + " and return the categories in one " \
                                                                              "word [/PROMPT]: \n"
                input_query = [{"role": "user", "content": category_classification_prompt + document_contents[:1000]}]
                classification = Utils.invoke_gpt_api(openai_model, input_query)

                for index, value in enumerate(document_categories):
                    if value in classification:
                        classification = document_categories[index]

            meta_data[file.name] = {
                'file_name': file.name,
                'file_type': mapped_file_type,
                'full_contents': document_contents,
                'display_contents': document_contents[:100] + '...',
                'total_words': document_word_length,
                'character_length': document_char_length,
                'classification': classification
            }

        meta_data = pd.DataFrame.from_dict(meta_data, orient='index')
        meta_data.to_excel(self.get_project_directory() + '/Project_Meta_Data.xlsx', index=False)
        return True

    def create_project(self):
        if not os.path.isdir(PROJECT_PATH):
            os.makedirs(PROJECT_PATH)
        db_path = PROJECT_PATH + "db"
        is_db_created = self.create_db_directory(db_path)
        if is_db_created:
            project_dir = os.path.join(db_path, self.get_project_name())
            self.set_project_directory(project_dir)
            is_files_uploaded = self.save_uploaded_files()
            if is_files_uploaded:
                return True
            else:
                st.warning(f'Error while uploading {self.get_project_name()} files')
                return False
        else:
            return False

    @staticmethod
    def get_all_projects_from_db(path):
        files = os.listdir(path)
        files.sort(key=lambda file: os.path.getctime(os.path.join(path, file)), reverse=True)
        return files

    @staticmethod
    def get_project_ddq_file(path, project):
        return pd.read_excel(path + "/" + project + "/DDQ.xlsx")

    @staticmethod
    def get_project_meta_data(path, project):
        return pd.read_excel(path + "/" + project + "/Project_Meta_Data.xlsx")
