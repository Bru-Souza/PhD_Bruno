import time
import streamlit as st

from lib.nodes import InputNode


def main():
    st.set_page_config(page_title="Input Viewer", page_icon="🎥")
    st.title("Flow Viewer")

    # Controle do vídeo
    st.session_state.video_running = False

    # Botões de controle do vídeo
    if st.button("Play Video"):
        st.session_state.video_running = True
        
    if st.button("Stop Video"):
        st.session_state.video_running = False

    # Visualização do vídeo
    frame_placeholder = st.empty()  # Cria um espaço que pode ser atualizado
    current_frame = None  # Variável para manter o último frame

    while st.session_state.video_running:
        current_frame = st.session_state['input_node'].get_frame()
        
        if current_frame is not None:
            frame_placeholder.image(current_frame, channels="BGR", use_column_width=True)
        else:
            st.warning("No frames available.")
            st.session_state.video_running = False  # Para o vídeo se não houver mais frames

        time.sleep(0.05)  # Delay para não sobrecarregar a CPU

if __name__ == "__main__":
    main()
