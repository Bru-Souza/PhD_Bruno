import streamlit as st

from lib.nodes import *

st.set_page_config(
    page_title="Create Task",
    page_icon="📌",
)
st.title("Create Task")

st.sidebar.header("Tasks")

st.write("""In this area you can register different computer vision tasks to be executed on your video source. """)

st.write("## Choose task type.")

selectBox_options = ["Object Detection", "Segmentation", "Action Recognition", "Draw Circle", "Draw Square"]

task_type = st.selectbox("Select one of the task types", selectBox_options, index=None, key=None, help=None, on_change=None, args=None, kwargs=None, placeholder="Choose an option")

task_name = st.text_input("Task name", placeholder="Insert task name")

if task_type == "Object Detection":
    
    with st.form("task"):

        # Upload model file
        model_file = st.file_uploader("Upload model file")

        # Upload model config file
        model_config = st.file_uploader("Upload model configuration file")
        
        # Define image size
        img_sz = st.radio("Image size:", ["224 x 224", "416 x 416", "640 x 640"], index=None)

        # Set conf_thres
        color = st.slider("Select confidence threshold",0.0, 1.00, 0.60)

        # Define Classes
        classes = st.multiselect(
            "Select classes",
            ["person", "hand", "tool", "nobreak"],
            [],
        )

        submit = st.form_submit_button(label="Create task")

        if submit and model_file:
            # Save uploaded file in a session state to be accessed by the play video page
            st.session_state.model_file = model_file
            st.success("Model uploaded successfully.")
        
        if submit and model_config:
            # Save uploaded file in a session state to be accessed by the play video page
            st.session_state.model_config = model_config
            st.success("Model configuration uploaded successfully.")

elif task_type == "Draw Circle":
    
    with st.form("task"):
        
        submit = st.form_submit_button(label="Create task")

        if submit:
            circle_task = CircleTaskNode(id='circle1', pos=(300,200), data={'content': 'Draw Circle'})
            print("[INFO] Task node was created.")

            st.session_state['nodes'].append(circle_task.node)
            st.session_state['node_object'].append(circle_task)
            st.success("Task created successfully.")


elif task_type == "Draw Square":
    with st.form("task"):
        
        submit = st.form_submit_button(label="Create task")

        if submit:
            square_task = SquareTaskNode(id='square1', pos=(300,400), data={'content': 'Draw Square'})
            print("[INFO] Task node was created.")

            st.session_state['nodes'].append(square_task.node)
            st.session_state['node_object'].append(square_task)
            st.success("Task created successfully.")
    
