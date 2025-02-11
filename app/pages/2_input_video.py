import tempfile
import streamlit as st

from lib.nodes import InputNode

st.set_page_config(page_title="Set video source", page_icon="📹")

st.title("Set video source")

st.write("""In this section, you can add your desired video source. 
            This can be a video file, a camera device or an IP address streaming images.
        """)

st.write("## Choose video source.")

selectBox_options = ["Video file", "Camera device", "IP Address"]
videoSrc_type = st.selectbox("Select one of the video source options", selectBox_options, index=None, key=None, help=None, on_change=None, args=None, kwargs=None, placeholder="Choose an option")

# Define a fonte de vídeo
if videoSrc_type == "Video file":
    with st.form("video_src"):
        uploaded_file = st.file_uploader("Choose a file")
        submit = st.form_submit_button(label="Submit")

        if submit and uploaded_file:
            # Salvar o arquivo em um local temporário
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name

            # Salvar o caminho do arquivo temporário no session_state
            st.session_state.uploaded_file_path = temp_file_path
            st.success("Video file uploaded successfully. Please go to the 'Input Check' page to view the video.")

            if 'uploaded_file_path' not in st.session_state:
                st.error("No video file uploaded. Please upload a video in the Upload Video page.")

            # Inicializa o InputNode apenas uma vez
            if 'input_node' not in st.session_state:

                st.session_state['node_object'] = []

                # Cria o InputNode
                input_node = InputNode(
                    id="input_1",
                    pos=(100, 200),
                    data={'source_type': 'file', 'source': st.session_state.uploaded_file_path, 'content': 'Video Source'}
                )

                st.session_state['nodes'] = [input_node.node]  # Inicializa a lista de nós

                # Adiciona o objeto node completo a sessão
                st.session_state['node_object'].append(input_node)
                # Controle do vídeo
                if 'video_running' not in st.session_state:
                    st.session_state.video_running = False
                
                print('[INFO] Input node was created.')
            

elif videoSrc_type == "Camera device":
    
    with st.form("camera_src"):
        # Set camera options
        cameras = ["webcam", "Intel RealSense D435i"]
        # Seleciona o dispositivo
        camera_name = st.selectbox("Select one of the camera options", cameras, index=None, key=None, help=None, on_change=None, args=None, kwargs=None, placeholder="Select the camera")
        
        submit = st.form_submit_button(label="Submit", type="primary")
        cameara_device = None

        if submit and camera_name != None:
            if camera_name == "webcam":
                cameara_device = 0
            elif camera_name == "Intel RealSense D435i":
                cameara_device = 6
            

            # Salvar o caminho do arquivo temporário no session_state
            st.session_state.uploaded_file_path = cameara_device
            st.success("Camera source selected.")

            # Inicializa o InputNode apenas uma vez
            if 'input_node' not in st.session_state:

                st.session_state['node_object'] = []

                # Cria o InputNode
                input_node = InputNode(
                    id="input_1",
                    pos=(100, 200),
                    data={'source_type': 'file', 'source': st.session_state.uploaded_file_path, 'content': 'Video Source'}
                )

                st.session_state['nodes'] = [input_node.node]  # Inicializa a lista de nós

                # Adiciona o objeto node completo a sessão
                st.session_state['node_object'].append(input_node)
                
                # Controle do vídeo
                if 'video_running' not in st.session_state:
                    st.session_state.video_running = False
                
                print('[INFO] Input node was created.')

        # create cols
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.form_submit_button(label="Check video src"):
                st.switch_page("pages/3_video_check.py") 
        with col2:
            if st.form_submit_button(label="ROI setup"):
                st.switch_page("pages/4_ROI.py")

elif videoSrc_type == "IP Address":
    with st.form("ip_src"):
        ip_src = st.text_input("Insert IP Address")
        submit = st.form_submit_button(label="Submit")

        if submit and ip_src:
            # Salvar o caminho do arquivo temporário no session_state
            st.session_state.uploaded_file_path = ip_src
            st.success("IP source selected.")

            # Inicializa o InputNode apenas uma vez
            if 'input_node' not in st.session_state:

                st.session_state['node_object'] = []

                # Cria o InputNode
                input_node = InputNode(
                    id="input_1",
                    pos=(100, 200),
                    data={'source_type': 'file', 'source': st.session_state.uploaded_file_path, 'content': 'Input'}
                )

                st.session_state['nodes'] = [input_node.node]  # Inicializa a lista de nós

                # Adiciona o objeto node completo a sessão
                st.session_state['node_object'].append(input_node)
                
                # Controle do vídeo
                if 'video_running' not in st.session_state:
                    st.session_state.video_running = False
                
                print('[INFO] Input node was created.')


