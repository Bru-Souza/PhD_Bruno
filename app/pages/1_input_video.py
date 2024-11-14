import tempfile
import streamlit as st

from lib.nodes import InputNode

st.set_page_config(page_title="Upload Video", page_icon="📹")

st.title("Upload Video")

st.sidebar.header("Video Source")

st.write("""In this section, you can add your desired video source. 
            This can be a video file or an IP address streaming images from a real camera.
        """)

st.write("## Choose video source.")

selectBox_options = ["Video file", "IP Address"]
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
                    data={'source_type': 'file', 'source': st.session_state.uploaded_file_path, 'content': 'Input'}
                )
                
                input_node.initialize_video()  # Inicializa o vídeo
                st.session_state['input_node'] = input_node  # Salva o nó no estado da sessão
                st.session_state['nodes'] = [input_node.node]  # Inicializa a lista de nós

                # Adiciona o objeto node completo a sessão
                st.session_state['node_object'].append(input_node)
                # Controle do vídeo
                if 'video_running' not in st.session_state:
                    st.session_state.video_running = False
                
                print('[INFO] Input node was created.')
            

elif videoSrc_type == "IP Address":
    with st.form("video_src"):
        video_src = st.text_input("Insert IP Address", "0.0.0.0:0000")
        submit = st.form_submit_button(label="Submit")

        if submit and video_src:
            # Save IP address in a session state to be accessed by the play video page
            st.session_state.video_ip = video_src
            st.success("IP Address saved successfully. Please go to the 'Input Check' page to view the video.")


