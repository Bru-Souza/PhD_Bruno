import cv2
import time
import logging
import numpy as np
import streamlit as st

from PIL import Image
from lib.utils import update_project_file
from streamlit_drawable_canvas import st_canvas

# Define page title
st.title("Select Region of Interest")

# Control video src
if 'video_running' not in st.session_state:
    st.session_state.video_running = False

# Control frame video
if 'frame_set' not in st.session_state:
    st.session_state.frame_set = False

# Variables to store frame information
current_frame = None
current_frame_h = None
current_frame_w = None

if not st.session_state.frame_set or st.button("Get frame"):
    # Start video source
    logging.info("Starting video source to get ROI frame.")
    st.session_state.video_running = True
    st.session_state['node_object'][0].initialize_video()
    
    time.sleep(3)
    
    if st.session_state['node_object'][0].video_manager.cap.isOpened():
        # Get frame from video src
        current_frame = st.session_state['node_object'][0].get_frame()
    
    if current_frame is not None:
        logging.info("Frame loaded successfully.")
        st.session_state.frame_set = True
        # Get frame information
        current_frame_h, current_frame_w, _ = current_frame.shape
        logging.info(f"Frame details: height = {current_frame_h}, width = {current_frame_w}.")
    else:
        st.warning("No frames available.")

# Show canvas when frame is set
if st.session_state.frame_set:

    if isinstance(current_frame, np.ndarray):
        current_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)
        current_frame = Image.fromarray(current_frame)
        output_path = st.session_state.project_folder + "/ROI.png"
        current_frame.save(output_path)
        logging.info(f"Saving ROI frame to {output_path}.")

    if st.session_state.video_running == True:
        # Close video source
        st.session_state.video_running = False
        st.session_state['node_object'][0].release()
        logging.info("Close video source.")

        
    # Draw options
    drawing_mode = st.sidebar.selectbox("Drawing tool:", ("rect", "circle"))
    stroke_width = 3

    # Create canvas
    logging.info("Creating canvas.")
    canvas_result = st_canvas(
        fill_color="rgba(77, 145, 207, 0.3)",  # Fixed fill color with some opacity
        stroke_width=stroke_width,
        stroke_color="000000",
        background_image=current_frame,
        update_streamlit=False,
        height=720,
        width=1280,
        drawing_mode=drawing_mode,
        point_display_radius=0,
        key="canvas",
    )

    if st.button("Set ROI"):
        logging.info("ROI is set.")
        st.session_state["canvas_result"] = canvas_result.json_data
        logging.info(f"Canvas Props: {canvas_result.json_data}.")

        # Update ROI information in project file
        update_project_file({"canvas_result": canvas_result.json_data})

        # Go to next page
        st.switch_page("pages/4_model_configuration.py")

