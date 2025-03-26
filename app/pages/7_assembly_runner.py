import os
import cv2
import multiprocessing
import streamlit as st

os.environ['YOLO_VERBOSE'] = 'False'

from lib.utils import get_next_experiment_filename
from lib.template_matching.assembly_verification import AssemblyVerification
from lib.pipeline import capture_frames_process, inference_process, display_process, projector_process, update_monitoring
    
if __name__ == "__main__":
    
    # Sinal global para encerrar os processos
    stop_event = multiprocessing.Event()

    st.set_page_config(page_title="Assembly", page_icon="📺")
    st.title("Aseembly Runner")

    # Inicializa a variável session_state para salvar o vídeo
    if "save_video" not in st.session_state:
        st.session_state.save_video = False
    if "video" not in st.session_state:
        st.session_state.video = None

    st.session_state.save_video = st.toggle("Save video")

    # Botões de controle do assembly
    if st.button("Play Assembly"):

        base_folder = os.path.join(st.session_state.project_folder, "runs")
        st.session_state.json_path = get_next_experiment_filename(base_folder, "json")

        if st.session_state.save_video:
            video_path = get_next_experiment_filename(base_folder, "mp4")

            # Criando o arquivo de vídeo
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            st.session_state.video = cv2.VideoWriter(video_path, fourcc, 30.0, (640, 480))

        # Show steps
        st.subheader("Step list")
        st.session_state.image_placeholders = {}
        st.session_state.columns = {}
        st.session_state.status_dict = {}

        st.session_state.steps_order = []
        # Iterar sobre os ramos e obter os steps
        for node in st.session_state['all_possible_branches'][0]:
            if node.startswith("step"):
                st.session_state.steps_order.append(node)
                st.session_state.status_dict[node] = False
                st.session_state.columns[f"col1_{node}"], st.session_state.columns[f"col2_{node}"] = st.columns([3, 1])
                with st.session_state.columns[f"col1_{node}"]:
                    st.write(node)
                
                with st.session_state.columns[f"col2_{node}"]:
                    # Criar um placeholder para a imagem
                    st.session_state.image_placeholders[node] = st.empty()
        
        # Inicialização do verificador de template
        st.session_state.assembly_verifier = AssemblyVerification()

        # Queue para dados compartilhados entre processos
        frame_queue = multiprocessing.Queue(maxsize=10)
        prediction_queue = multiprocessing.Queue(maxsize=10)
        projector_queue = multiprocessing.Queue(maxsize=10)
        complete = multiprocessing.Value('b', False)
        step_status = multiprocessing.Queue()

        step_status.put(st.session_state.status_dict)

        # Set dos processos
        capture_frames_process = multiprocessing.Process(target=capture_frames_process, args=(frame_queue, stop_event))
        inference_process = multiprocessing.Process(target=inference_process, args=(frame_queue, prediction_queue, step_status, projector_queue, stop_event))
        display_process = multiprocessing.Process(target=display_process, args=(prediction_queue, stop_event))
        projector_process = multiprocessing.Process(target=projector_process, args=(projector_queue, stop_event))

        # Iniciar os processos
        capture_frames_process.start()
        inference_process.start()
        display_process.start()
        projector_process.start()

        update_monitoring(step_status)

        # Join todos os processos
        capture_frames_process.join()
        inference_process.join()
        display_process.join()
        projector_process.join()

