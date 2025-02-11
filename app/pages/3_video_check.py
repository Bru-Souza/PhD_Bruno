import time
import streamlit as st

def main():
    st.set_page_config(page_title="Input Viewer", page_icon="🎥")
    st.title("Input Viewer")

    # Controle do vídeo
    st.session_state.video_running = False

    # create cols
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Botões de controle do vídeo
        if st.button("Play Video"):
            st.session_state.video_running = True
            st.session_state['node_object'][0].initialize_video()
            st.info("Initializing video", icon=None)
    with col2:
        if st.button("Stop Video"):
            st.session_state.video_running = False
            st.session_state['node_object'][0].release()
            st.info("Destroying video", icon=None)
    with col3:
        if st.button("ROI setup"):
            if st.session_state.video_running == True:
                st.session_state.video_running = False
                st.session_state['node_object'][0].release()
            st.info("Destroying video", icon=None)
            st.switch_page("pages/4_ROI.py")

    # Visualização do vídeo
    frame_placeholder = st.empty()  # Cria um espaço que pode ser atualizado
    current_frame = None  # Variável para manter o último frame

    while st.session_state.video_running:
        current_frame = st.session_state['node_object'][0].get_frame()
        
        if current_frame is not None:
            frame_placeholder.image(current_frame, channels="BGR", use_container_width=True)
        else:
            st.warning("No frames available.")
            st.session_state['node_object'][0].release()
            st.info("Destroying video", icon=None)
            st.session_state.video_running = False  # Para o vídeo se não houver mais frames

        time.sleep(0.05)  # Delay para não sobrecarregar a CPU

if __name__ == "__main__":
    main()
