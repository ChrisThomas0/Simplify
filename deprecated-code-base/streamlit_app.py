import warnings
import streamlit as st
from functions import *
from init_environment_variables import *

warnings.filterwarnings("ignore")

st.title("DDQ form automation using LLMs")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []


def create_project():
    st.write("Create project for AI Powered Due Diligence")

    with st.form("my-form", clear_on_submit=True):
        project_name = st.text_input("Project Name", key="project_name")
        project_description = st.text_input("Project Description", key="project_description")
        uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True)

        if st.form_submit_button("Create"):

            if not os.path.isdir(PROJECT_PATH + "db"):
                os.makedirs(PROJECT_PATH + "db")

            db_path = PROJECT_PATH + "db"

            is_db_created = create_db_directory(db_path, project_name)
            if is_db_created:
                project_dir = os.path.join(db_path, project_name)
                save_uploaded_files(uploaded_files, project_dir)

                with st.container():
                    with st.spinner('Processing uploaded files'):
                        is_meta_data_created = create_meta_data(uploaded_files, project_dir)
                        if is_meta_data_created:
                            st.success(f"Project Name: {project_name}  \nProject Description: {project_description}")
            else:
                st.warning(f'{project_name} project already exists!')


def project_details():
    st.write("Project Details")
    db_path = PROJECT_PATH + "db"

    project_names = os.listdir(db_path)

    for project_name in project_names:
        if project_name != ".DS_Store":
            project_path = os.path.join(db_path, project_name)
            project_meta_data = pd.read_excel(project_path + '/Project_Meta_Data.xlsx')

            display_meta_data = project_meta_data.loc[:, project_meta_data.columns != 'full_contents']
            display_meta_data.columns = [column.strip().replace("_", " ").capitalize()
                                         for column in display_meta_data.columns]

            with st.expander(project_name):
                st.table(display_meta_data)


def complete_ddq_form():
    projects = (os.listdir(PROJECT_PATH + "db/")[1:])
    projects.insert(0, "Select a project")
    projects = tuple(projects)

    project_options = st.selectbox(
        'Projects', projects)

    project_index = projects.index(project_options)

    if project_index != 0:
        project_ddq_file = PROJECT_PATH + "db/" + project_options + "/DDQ.xlsx"
        project_meta_data_file = PROJECT_PATH + "db/" + project_options + "/Project_Meta_Data.xlsx"

        try:
            ddq_data = pd.read_excel(project_ddq_file)
            project_meta_data = pd.read_excel(project_meta_data_file)
            for index, row in ddq_data.iterrows():
                prompt = row['Sub Prompt']
                ddq_question = row['Entity Name']
                file_name = row['Reference in Data Room']
                meta_data_contents = project_meta_data[
                    project_meta_data['file_name'].str.contains(file_name)].reset_index()

                with st.chat_message("user"):
                    st.markdown(ddq_question)

                if len(meta_data_contents) > 0:
                    full_contents = meta_data_contents['full_contents'][0]
                    input_query = prompt + full_contents

                    st.session_state.messages.append({"role": "user", "content": input_query})

                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        response = invoke_gpt_api(st.session_state["openai_model"],
                                                  st.session_state.messages)
                        # Intentional to leave two space to print the contents in a new line - this works in markdown
                        response += "  \nRefer to document " + meta_data_contents['file_name'][0] + " in the data " \
                                                                                                    "room"
                        message_placeholder.markdown(response + "▌")
                        message_placeholder.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

                    # clear the messages once the response is obtained to process next message
                    st.session_state.messages = []
                else:
                    with st.chat_message("assistant"):
                        st.markdown("No relevant files found!")
            st.markdown("DDQ Application process is completed!")
        except FileNotFoundError:
            st.markdown('No DDQ found. Please upload the project DDQ file')


def main():
    tabs = ["Create Project", "Projects", "AI-Powered DDQ"]
    create_project_tab, projects_tab, ddq_forms_tab = st.tabs(tabs)

    with create_project_tab:
        create_project()
    with projects_tab:
        project_details()
    with ddq_forms_tab:
        complete_ddq_form()


if __name__ == "__main__":
    main()
