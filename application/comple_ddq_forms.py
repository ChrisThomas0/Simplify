from Project import Project
import streamlit as st
from utils import *
from init_environment_variables import *


class CompleteDdqForms:

    @staticmethod
    def complete_ddq_form():

        if "messages" not in st.session_state:
            st.session_state.messages = []

        db_path = PROJECT_PATH
        projects = Project.get_all_projects_from_db(db_path)
        projects.remove(".DS_Store")
        projects.insert(0, "Select a project")
        projects = tuple(projects)

        project_options = st.selectbox(
            'Projects', projects)

        project_index = projects.index(project_options)
        completed_ddq_form = []

        if project_index != 0:
            try:
                ddq_data = Project.get_project_ddq_file(db_path, project_options)
                project_meta_data = Project.get_project_meta_data(db_path, project_options)

                for index, row in ddq_data.iterrows():
                    temp = {}
                    response = ""
                    prompt = row['Sub Prompt']
                    ddq_question = row['Entity Name']
                    file_names = row['Reference in Data Room']
                    file_names = file_names.split("\n")

                    try:
                        file_names = list(filter("".__ne__, file_names))
                    except ValueError:
                        pass

                    with st.chat_message("user"):
                        st.markdown(ddq_question)

                    for file_name in file_names:

                        meta_data_contents = project_meta_data[
                            project_meta_data['file_name'].str.contains(file_name)].reset_index()

                        if len(meta_data_contents) > 0:
                            full_contents = meta_data_contents['full_contents'][0]

                            if len(full_contents) > 4096:
                                full_contents = Utils.divide_into_sentence_chunks(full_contents, 3500)[0]

                            input_query = prompt + full_contents

                            st.session_state.messages.append({"role": "user", "content": input_query})

                            response += Utils.invoke_gpt_api(openai_model, st.session_state.messages)
                            response += f"  \n**Refer to document {meta_data_contents['file_name'][0]} \
                                        in the data room**  \n\n"
                        else:
                            response += f"\n\n  **{file_name} missing in database.**"

                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        message_placeholder.markdown(response)

                    st.session_state.messages = []

                    temp['Entity Name'] = ddq_question
                    temp['Sub Prompt'] = prompt
                    temp['Response'] = response
                    completed_ddq_form.append(temp)

                st.markdown("DDQ Application process is completed!")

                completed_ddq_form = pd.DataFrame(completed_ddq_form)
                csv = Utils.convert_to_csv(completed_ddq_form)

                download_form = st.download_button(
                    label="Download Form",
                    data=csv,
                    file_name='Completed DDQ Form.csv',
                    mime='text/csv'
                )

            except FileNotFoundError:
                st.markdown('No DDQ found. Please upload the project DDQ file')
