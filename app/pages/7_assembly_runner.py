import os
import cv2
import logging
import multiprocessing
import streamlit as st

os.environ['YOLO_VERBOSE'] = 'False'

from lib.utils import get_next_experiment_filename
from lib.template_matching.assembly_verification import AssemblyVerification
from lib.pipeline import capture_frames_process, inference_process, display_process, projector_process, update_monitoring
    
if __name__ == "__main__":
    
    # Global signal to close all processes
    stop_event = multiprocessing.Event()

    # Set page configuration and title
    st.set_page_config(page_title="Assembly", page_icon="📺")
    st.title("Aseembly Runner")

    # Initialize the session_state variable to save the video
    if "save_video" not in st.session_state:
        st.session_state.save_video = False
    if "video" not in st.session_state:
        st.session_state.video = None

    # Create toggle btn to save video
    st.session_state.save_video = st.toggle("Save video")

    # Assembly control button
    if st.button("Play Assembly"):

        # Check which is the current base folder for the experiment
        base_folder = os.path.join(st.session_state.project_folder, "runs")

        # Get json experiment path
        st.session_state.json_path = get_next_experiment_filename(base_folder, "json")

        if st.session_state.save_video:
            video_path = get_next_experiment_filename(base_folder, "mp4")

            # Create video file for save run
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            st.session_state.video = cv2.VideoWriter(video_path, fourcc, 15.0, (1280, 720))
            logging.info("Video file to save run exp was created.")

        # Show steps in monitoring screen
        st.subheader("Step list")
        st.session_state.image_placeholders = {}
        st.session_state.columns = {}
        st.session_state.status_dict = {}

        st.session_state.steps_order = []
        
        # Iterate over the branches and get the steps
        for node in st.session_state['all_possible_branches'][0]:
            if node.startswith("step"):
                st.session_state.steps_order.append(node)
                st.session_state.status_dict[node] = False
                st.session_state.columns[f"col1_{node}"], st.session_state.columns[f"col2_{node}"] = st.columns([3, 1])
                
                # Create text for each step
                with st.session_state.columns[f"col1_{node}"]:
                    st.write(node)
                
                # Create a placeholder for the image
                with st.session_state.columns[f"col2_{node}"]:
                    st.session_state.image_placeholders[node] = st.empty()

                logging.info(f"Creating step monitoring for: {node}.")

        # Initializing the template verifier
        logging.info("Initializing the template verifier.")
        st.session_state.assembly_verifier = AssemblyVerification()

        # Queue for data shared between processes
        frame_queue = multiprocessing.Queue(maxsize=10)
        prediction_queue = multiprocessing.Queue(maxsize=10)
        projector_queue = multiprocessing.Queue(maxsize=10)
        complete = multiprocessing.Value('b', False)
        step_status = multiprocessing.Queue()
        logging.info("Initializing Queues for data shared between processes.")

        step_status.put(st.session_state.status_dict)

        # Set process
        capture_frames_process = multiprocessing.Process(target=capture_frames_process, args=(frame_queue, stop_event))
        inference_process = multiprocessing.Process(target=inference_process, args=(frame_queue, prediction_queue, step_status, projector_queue, stop_event))
        display_process = multiprocessing.Process(target=display_process, args=(prediction_queue, stop_event))
        projector_process = multiprocessing.Process(target=projector_process, args=(projector_queue, stop_event))
        logging.info("Creating processes for capturing, inference, display and projection.")

        # Start the processes
        logging.info("Starting all processes.")
        capture_frames_process.start()
        inference_process.start()
        display_process.start()
        projector_process.start()
        

        update_monitoring(step_status)

        # Join all processes
        logging.info("Join all processes.")
        capture_frames_process.join()
        inference_process.join()
        display_process.join()
        projector_process.join()

