import logging
import streamlit as st

from lib.nodes import *
from lib.utils import update_project_file
from tasks.detection.detection import *

from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # YOLO

# Set page configuration
st.set_page_config(
    page_title="Model configuration",
    page_icon="📌",
)

# Define page title
st.title("Model configuration")

st.write("""In this area you can configure different computer vision models to be executed on your video source. """)

st.write("## Choose model type.")

# Model option list
model_options = ["Object detection"]

# Get model option from selectbox
model_type = st.selectbox("Select one of the model types", model_options, index=None, key=None, help=None, on_change=None, args=None, kwargs=None, placeholder="Choose an option")

# Get model name from text input
model_name = st.text_input("Model name", placeholder="Insert model name")

if model_type == "Object detection":

    # Add dropdown menu for model selection
    available_models = ["lego_v1", "lego_v2", "yolo11n"]

    st.session_state['selected_model'] = st.sidebar.selectbox("Model", available_models)
    
    with st.form("task"):

        # Set iou_thres
        st.session_state.model_iou = float(st.slider("Select IoU threshold",0.0, 1.00, 0.70))

        # set conf_thres
        st.session_state.model_conf = float(st.slider("Confidence Threshold", 0.0, 1.0, 0.65, 0.01))

        submit = st.form_submit_button(label="Create task")

        # Define class names based on selected model
        if st.session_state['selected_model'] == "lego_v1":
            class_names = ["block_1x2", "block_1x4_h", "block_2_8", "block_2x2_h", "wheel"]
        elif st.session_state['selected_model'] == "lego_v2":
            class_names = ['3003_dark_azure', '3004_black', '3004_sky_blue', '3010_sky_blue', '3020_black', '3022_black', '3034_turquoise', '3039_transparent', '3040a_black', '3137_wheel']
        elif st.session_state['selected_model'] == "yolo11n":
            class_names = ["person", "bus", "car"]

        # Multiselect box with class names and get indices of selected classes
        st.session_state['selected_classes'] = st.sidebar.multiselect("Classes", class_names, default=class_names)
        st.session_state['selected_ind'] = [class_names.index(option) for option in st.session_state['selected_classes']]

        if submit:
            logging.info(f"Model: {st.session_state['selected_model']}, was selected.")
            logging.info(f"Model classes: {st.session_state['selected_classes']}.")
            # Create object detection model
            detection_task = ObjectDetection(id=st.session_state['selected_model'], pos=(250,200), data={'content': st.session_state['selected_model']}, conf=st.session_state.model_conf, iou=st.session_state.model_iou)

            # Add object and node object to session state lists
            st.session_state['nodes'].append(detection_task.node)
            st.session_state['node_object'].append(detection_task)
            
            st.success("Detection model was configured successfully.")

            # Save model info to project file
            update_project_file({"model":{"selected_model": st.session_state['selected_model'], "iou": st.session_state.model_iou, "conf": st.session_state.model_conf, "selected_ind": st.session_state['selected_ind'], "selected_classes": st.session_state['selected_classes']}})


