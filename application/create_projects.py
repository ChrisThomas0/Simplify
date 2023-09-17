import streamlit as st


class CreateProject:

    @staticmethod
    def generate_form_ui(project):
        st.write("Create project for AI Powered Due Diligence")

        with st.form("my-form", clear_on_submit=True):
            project_name = st.text_input("Enter Project Name", key="project_name")
            project_description = st.text_input("Enter Project Name", key="project_description")
            uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True)

            # set the class variables
            project.set_project_name(project_name)
            project.set_project_description(project_description)
            project.set_uploaded_files(uploaded_files)

            # create button on submit
            if st.form_submit_button("Create"):
                is_files_uploaded = project.create_project()

                if is_files_uploaded:
                    with st.container():
                        with st.spinner('Processing uploaded files'):
                            is_meta_data_created = project.create_meta_data()
                            if is_meta_data_created:
                                st.success(
                                    f"Project Name: {project.get_project_name()}  \n"
                                    f"Project Description: {project.project_description}")
                else:
                    st.warning(f'Error! {project.get_project_name()} project already exists in DB')
