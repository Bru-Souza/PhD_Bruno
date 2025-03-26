import os
import json
import logging
import streamlit as st
import torch
torch.classes.__path__ = []

from lib.utils import save_project_to_json, get_project_data, create_log_file, setup_logger

def get_next_experiment_filename(base_folder):
    os.makedirs(base_folder, exist_ok=True)
    exp_num = 1
    while os.path.exists(os.path.join(base_folder, f"exp_{exp_num:02d}.mp4")):
        exp_num += 1
    return os.path.join(base_folder, f"exp_{exp_num:02d}.mp4")

# Set YOLO to quiet mode
os.environ['YOLO_VERBOSE'] = 'False'

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

        # Create and set log file
        log_file = create_log_file()

        setup_logger(log_file)

        st.switch_page("pages/2_input_video.py")

else:
    st.info('Load your project', icon=None)
    # Carregar o arquivo JSON
    loaded_project_file = st.file_uploader("Upload your project (JSON file)", type="json")

    if loaded_project_file is not None:
        try:
            st.session_state.project_folder = os.getcwd() + "/projects/project_" + os.path.splitext(loaded_project_file.name)[0] + "/"
            # Carregar o conteúdo do arquivo JSON
            project_data = json.load(loaded_project_file)
            st.success("Project loaded successfully!")
            st.json(project_data)

            # Create project nodes
            get_project_data(project_data)
            
            logging.info("Project loaded successfully.")
        
        except json.JSONDecodeError:
            st.error("Error: The file is not a valid JSON.")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

