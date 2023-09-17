from Project import Project
import streamlit as st
from create_projects import CreateProject
from comple_ddq_forms import CompleteDdqForms
from show_projects import ShowProjects

st.title("DDQ form automation using LLMs")


def main():
    tabs = ["Create Project", "Projects", "AI-Powered DDQ"]
    create_project_tab, projects_tab, ddq_forms_tab = st.tabs(tabs)
    project = Project()

    with create_project_tab:
        CreateProject.generate_form_ui(project)

    with projects_tab:
        ShowProjects.project_details()

    with ddq_forms_tab:
        CompleteDdqForms.complete_ddq_form()


if __name__ == "__main__":
    main()
