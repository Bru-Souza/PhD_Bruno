import os
import json
import streamlit as st

from lib.utils import save_project_to_json

st.set_page_config(
    page_title="Assembly Configuration",
    page_icon="📌",
)
st.title("Create Assembly Project")

st.sidebar.header("Projects")

st.write("""In this area you can create and load assembly projets. """)

project_mode = st.radio(
    "Select one of the possible modes",
    ["New project", "Load project"],
    captions=[
        "If you want to create a new assembly project.",
        "If you already have a project file."
    ],
)

    
if project_mode == "New project":
    st.info('Creating new project', icon=None)

    # Define project name
    project_name = st.text_input("Project name", "")

    create_project_btn = st.button("Create")
    
    if create_project_btn and project_name != "":
        # Create project file
        project_file = save_project_to_json(project_name)
        
        # save path to json file
        st.session_state.project_file = project_file

        st.switch_page("pages/2_input_video.py")

else:
    st.info('Load your project', icon=None)

