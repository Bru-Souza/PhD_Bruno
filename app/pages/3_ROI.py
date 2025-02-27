import cv2
import time
import logging
import numpy as np
import streamlit as st

from PIL import Image
from lib.utils import update_project_file
from streamlit_drawable_canvas import st_canvas


st.title("Select Region of Interest")

# Controle de execução do vídeo
if 'video_running' not in st.session_state:
    st.session_state.video_running = False
if 'frame_set' not in st.session_state:
    st.session_state.frame_set = False

current_frame = None

if not st.session_state.frame_set or st.button("Get frame"):
    st.session_state.video_running = True
    time.sleep(1)
    st.session_state['node_object'][0].initialize_video()
    time.sleep(1)
    current_frame = st.session_state['node_object'][0].get_frame()

    if current_frame is not None:
        st.session_state.frame_set = True
    else:
        st.warning("No frames available.")

# Exibir canvas apenas quando o frame for setado
if st.session_state.frame_set:

    if isinstance(current_frame, np.ndarray):
        current_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)
        current_frame = Image.fromarray(current_frame)

    if st.session_state.video_running == True:
        # Close video props
        st.session_state.video_running = False
        st.session_state['node_object'][0].release()
        
    # Opções de desenho
    drawing_mode = st.sidebar.selectbox("Drawing tool:", ("rect", "circle"))
    stroke_width = 3

    # Criação do canvas
    canvas_result = st_canvas(
        fill_color="rgba(77, 145, 207, 0.3)",  # Fixed fill color with some opacity
        stroke_width=stroke_width,
        stroke_color="000000",
        background_image=current_frame,
        update_streamlit=False,
        height=360,
        width=640,
        drawing_mode=drawing_mode,
        point_display_radius=0,
        key="canvas",
    )

    if st.button("Set ROI"):
        st.session_state["canvas_result"] = canvas_result.json_data
        print(canvas_result.json_data)

        # Update ROI information in project file
        update_project_file({"canvas_result": canvas_result.json_data})
        
        # Go to next page
        st.switch_page("pages/4_model_configuration.py")