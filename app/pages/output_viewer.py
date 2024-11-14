import time
import streamlit as st

def main():
    st.set_page_config(page_title="Output Viewer", page_icon="📺")
    st.title("Output Viewer")
    
    # Botões de controle do vídeo
    if st.button("Play Video"):
        
        st.session_state.video_running = True
        # Iterar sobre os ramos e obter os frames
        for path in st.session_state['all_possible_branches']:
            
            # Armazene os node_objects e o frame_placeholder uma vez, fora do loop
            node_objects = st.session_state['node_object']
            frame_placeholder = st.empty()  # placeholder para exibir frames

            while st.session_state.video_running:

                frame = None
                
                # Iterar sobre os IDs de nodes no caminho (path)
                for node_idx, node_id in enumerate(path):

                    # Obter o frame inicial apenas uma vez
                    if node_id == 'input_1':
                        frame = node_objects[0].get_frame()  # Obter o frame inicial

                    elif frame is not None and node_id != 'output_1':
                        # Aplicar o processamento do frame em cada nó
                        frame = node_objects[node_idx].process_task(frame)

                    elif frame is not None:
                        # Exibe o frame final no placeholder
                        frame_placeholder.image(frame, channels="BGR", use_column_width=True)
                        break  # Evitar continuar o loop desnecessariamente após exibir o frame

                if frame is None:
                    st.warning("No frames available.")
                    st.session_state.video_running = False  # Para o vídeo se não houver mais frames
                    break

                # Calcula o intervalo baseado na taxa de frames, ex: 30 FPS (33 ms)
                # time.sleep(1 / 30.0)  # Ajuste para a taxa de frames desejada
                time.sleep(0.05)

if __name__ == "__main__":
    main()
