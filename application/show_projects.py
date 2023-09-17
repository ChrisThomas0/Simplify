from Project import Project
import streamlit as st
from utils import *
from init_environment_variables import *
from datetime import datetime


class ShowProjects:

    @staticmethod
    def project_details():
        st.write("Project Details")

        db_path = PROJECT_PATH + "db"
        project_names = Project.get_all_projects_from_db(db_path)

        for project_name in project_names:
            if project_name != ".DS_Store":
                project_path = os.path.join(db_path, project_name)
                project_ctime = os.path.getctime(project_path)
                project_date_time = datetime.fromtimestamp(project_ctime).strftime('%Y-%m-%d %H:%M:%S')
                project_meta_data = pd.read_excel(project_path + '/Project_Meta_Data.xlsx')
                display_meta_data = project_meta_data.loc[:, project_meta_data.columns != 'full_contents']
                display_meta_data.columns = [column.strip().replace("_", " ").capitalize()
                                             for column in display_meta_data.columns]
                expander_string = "**Name:** " + project_name + "  \n" + \
                                  "**Created on:** " + project_date_time + "  \n"
                with st.expander(expander_string):
                    st.table(display_meta_data)
