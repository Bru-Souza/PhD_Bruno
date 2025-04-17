import tempfile
import logging
import streamlit as st

from lib.nodes import InputNode
from lib.utils import update_project_file

# Set page config
st.set_page_config(page_title="Set video source", page_icon="📹")

# Define page title
st.title("Set video source")

st.write("""In this section, you can add your desired video source. 
            This can be a video file, a camera device or an IP address streaming images.
        """)

st.write("## Choose video source.")

# Define list option for video source
selectBox_options = ["Video file", "Camera device", "IP Address"]

# Get video option from selectbox
videoSrc_type = st.selectbox("Select one of the video source options", selectBox_options, index=None, key=None, help=None, on_change=None, args=None, kwargs=None, placeholder="Choose an option")

# Check selected video source
if videoSrc_type == "Video file":
    
    # Create a new form in streamlit
    with st.form("video_src"):
        logging.info("videoSrc_type set to Video file.")

        # Get video filepath
        uploaded_file = st.file_uploader("Choose a file")

        # Button for sending info
        submit = st.form_submit_button(label="Submit")

        if submit and uploaded_file:
            # Save file in tmp location
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name

            # Save path to local file
            st.session_state.uploaded_file_path = temp_file_path
            st.success("Video file uploaded successfully.")

            if 'uploaded_file_path' not in st.session_state:
                st.error("No video file uploaded. Please upload a video in the Upload Video page.")

            # Save info to project file
            update_project_file({"videoSrc_type": videoSrc_type, "source": uploaded_file.name})

            # Initialize input node
            if 'input_node' not in st.session_state:
                st.session_state['node_object'] = []

                # Create Input Node
                input_node = InputNode(
                    id="input_1",
                    pos=(100, 200),
                    data={'source_type': 'file', 'source': st.session_state.uploaded_file_path, 'content': 'Video Source'}
                )

                # Create node list and add input node
                st.session_state['nodes'] = [input_node.node]

                # Add node object to node list
                st.session_state['node_object'].append(input_node)
                
                # Create crontrol video state variable - Default is false
                if 'video_running' not in st.session_state:
                    st.session_state.video_running = False
                logging.info("Input node was created.")
        
        # Create cols to form organization
        col1, col2, col3 = st.columns(3)

        with col1:
            # Create a button to change page for ROI setup
            if st.form_submit_button(label="ROI setup"):
                st.switch_page("pages/3_ROI.py")
            

elif videoSrc_type == "Camera device":
    
    with st.form("camera_src"):
        logging.info("videoSrc_type set to Camera device.")

        # Define camera options
        cameras = ["webcam", "Intel RealSense D435i"]
        
        # Get camera from selectbox
        camera_name = st.selectbox("Select one of the camera options", cameras, index=None, key=None, help=None, on_change=None, args=None, kwargs=None, placeholder="Select the camera")
        
        submit = st.form_submit_button(label="Submit", type="primary")
        
        # Create camera device
        cameara_device = None

        if submit and camera_name != None:
            if camera_name == "webcam":
                cameara_device = 0
                logging.info("camera_name set to webcam.")
            elif camera_name == "Intel RealSense D435i":
                cameara_device = 6
                logging.info("camera_name set to Intel RealSense D435i.")
            

            # Save selected device
            st.session_state.uploaded_file_path = cameara_device
            
            # Save info to project file
            update_project_file({"videoSrc_type": videoSrc_type, "source": cameara_device})

            # Initialize input node
            if 'input_node' not in st.session_state:

                st.session_state['node_object'] = []

                # Create Input Node
                input_node = InputNode(
                    id="input_1",
                    pos=(100, 200),
                    data={'source_type': 'file', 'source': st.session_state.uploaded_file_path, 'content': 'Video Source'}
                )

                # Create node list and add input node
                st.session_state['nodes'] = [input_node.node]

                # Add node object to node list
                st.session_state['node_object'].append(input_node)
                
                # Create crontrol video state variable - Default is false
                if 'video_running' not in st.session_state:
                    st.session_state.video_running = False
                logging.info("Input node was created.")

        # Create cols to form organization
        col1, col2, col3 = st.columns(3)

        with col1:
            # Create a button to change page for ROI setup
            if st.form_submit_button(label="ROI setup"):
                st.switch_page("pages/3_ROI.py")


elif videoSrc_type == "IP Address":
    
    with st.form("ip_src"):
        logging.info("videoSrc_type set to IP Address.")

        # Get IP address from text input
        ip_src = st.text_input("Insert IP Address")
        submit = st.form_submit_button(label="Submit")

        if submit and ip_src:
            # Save IP address
            st.session_state.uploaded_file_path = ip_src
            logging.info(f"IP Address set for: {ip_src}.")
            st.success("IP source selected.")

            # Initialize input node
            if 'input_node' not in st.session_state:
                st.session_state['node_object'] = []

                # Create Input Node
                input_node = InputNode(
                    id="input_1",
                    pos=(100, 200),
                    data={'source_type': 'file', 'source': st.session_state.uploaded_file_path, 'content': 'Video Source'}
                )

                # Create node list and add input node
                st.session_state['nodes'] = [input_node.node]

                # Add node object to node list
                st.session_state['node_object'].append(input_node)
                
                # Create crontrol video state variable - Default is false
                if 'video_running' not in st.session_state:
                    st.session_state.video_running = False
                logging.info("Input node was created.")
        
        # Create cols to form organization
        col1, col2, col3 = st.columns(3)

        with col1:
            # Create a button to change page for ROI setup
            if st.form_submit_button(label="ROI setup"):
                st.switch_page("pages/3_ROI.py")

