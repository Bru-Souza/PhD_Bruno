import os
import cv2
import time
import streamlit as st

from lib.utils import append_to_json
from tasks.detection.tracking import CustomTrackZone


def inference_process(frame_queue, prediction_queue, step_status, projector_queue, stop_event):
    
    # Start experiment timer
    startExp_time = time.time()

    # Rastrear o estado da montagem
    step_number = 0
    region_points = []

    # Define region points
    if 'canvas_result' in st.session_state:
        try:
            x1 = st.session_state['canvas_result']["objects"][0]["left"]
            w = st.session_state['canvas_result']["objects"][0]["width"]
            y1 = st.session_state['canvas_result']["objects"][0]["top"]
            h = st.session_state['canvas_result']["objects"][0]["height"]
            x2 = x1 + w
            y2 = y1 + h
            
            region_points = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        except:
            print("[ERROR] Error getting region points")

    else:
        print("[WARNING] No canvas result available")
        h, w, _ = frame_queue.get().shape
        region_points = [(0, 0), (w, 0), (w, h), (0, h)]

    
    # Init TrackZone (Object Tracking in Zones, not complete frame)
    model_path = os.getcwd() + "/models/" + st.session_state.selected_model.lower() + ".pt"
    trackzone = CustomTrackZone(
        show=False,  # Display the output
        region=region_points,  # Pass region points
        model=model_path,  # You can use any model that Ultralytics support, i.e. YOLOv9, YOLOv10
        line_width=2,  # Adjust the line width for bounding boxes and text display
        classes=st.session_state['selected_ind'],
        verbose=False
    )

    # Recognized ids storage
    st.session_state.recognized_ids = set()
    
    # Armazene os node_objects
    node_objects = st.session_state['node_object']

    for step in st.session_state.steps_order:
        current_step = step

        for obj in node_objects:
            if obj.id == current_step:
                print(f"[INFO] Current step: {current_step}")
                startStep_time = time.time()
                assembly_info = f"Current step: {current_step} - Expected object: {obj.obj_cls}"
                
                # Get current cls
                expected_class_idx = obj.obj_idx

                # Get current template img
                expected_template = cv2.imread(obj.template_img_path)

                # Get current instruction img
                assembly_visual_instruction = cv2.imread(obj.instruction_img_path)

                # Get current instruction text
                assembly_text_instruction = obj.instruction_text
                
                while obj.match == False and not stop_event.is_set():
                    if not frame_queue.empty():
                        # Get image frame
                        frame = frame_queue.get()

                        # Inferência
                        annotated_frame, boxes, track_ids, clss = trackzone.trackzone(frame)

                        if len(boxes) == 0:
                            assembly_info = f"Current step: {current_step} - Expected object: {obj.obj_cls}"
                        
                        # Iterate over boxes, track ids, classes indexes
                        for box, track_id, cls in zip(boxes, track_ids, clss):
                            if int(cls) == expected_class_idx and track_id not in st.session_state.recognized_ids and obj.recognized is False:
                                st.session_state.recognized_ids.add(track_id)
                                obj.recognized = True
                                print(f"[INFO] Object {obj.obj_cls} was recognized.")
                                # Set template
                                st.session_state.assembly_verifier.set_template(expected_template)
                                break

                            elif int(cls) != expected_class_idx and track_id not in st.session_state.recognized_ids and obj.recognized is False:
                                assembly_info = f"Wrong object detected. Expect a {obj.obj_cls}, but got a {st.session_state['selected_classes'][int(cls)]}."

                        if obj.recognized is True and expected_template is not None:
                            assembly_info = "Performing template matching..."
                            is_match, confidence, result_tamplate_img = st.session_state.assembly_verifier.verify(frame)
                            is_match = True
                            if is_match:
                                # Save template matching result
                                tm_img_path = st.session_state.project_folder + f"/template_matching_{current_step}.png"
                                cv2.imwrite(tm_img_path, result_tamplate_img)

                                obj.match = True
                                st.session_state.status_dict[obj.id] = True
                                step_status.put(st.session_state.status_dict)
                                print(f"[INFO] Step {obj.id} is done!")
                                endStep_time = time.time()
                                totalStep_time = endStep_time - startStep_time

                                append_to_json(st.session_state.json_path, {f"{current_step}": totalStep_time})

                                step_number += 1
                                if step_number == len(st.session_state.steps_order):
                                    print("[INFO] Assembly process is completed!")
                                    assembly_info = "Assembly process is completed!"
                                    
                                    # Stop experiment timer
                                    endExp_time = time.time()
                                    totalExp_time = endExp_time - startExp_time
                                    append_to_json(st.session_state.json_path, {"Total experiment time": totalExp_time})


                                    time.sleep(0.5)
                                    
                                    print("[DEBUG] Setting stop_event...")
                                    stop_event.set() 
                                    break
                        
                        # Enviar o frame e as previsões para exibição
                        if not prediction_queue.full():
                            prediction_queue.put((annotated_frame, boxes))
                        
                        # Enviar projecoes
                        if not projector_queue.full():
                            projector_queue.put((assembly_visual_instruction, assembly_info, assembly_text_instruction))

                    time.sleep(0.01)


# Captura de frames em um processo separado
def capture_frames_process(frame_queue, stop_event):
    cap = cv2.VideoCapture(st.session_state.uploaded_file_path)

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break

        if not frame_queue.full():
            frame_queue.put(frame)
        time.sleep(0.03)  # Limitar a taxa de captura de frames

    cap.release()
    print("[INFO] Camera released")


# Função de exibição de frames
def display_process(prediction_queue, stop_event):

    while not stop_event.is_set():
        if not prediction_queue.empty():
            frame, _ = prediction_queue.get()

            # Salva o frame no vídeo, se necessário
            if st.session_state.video:
                st.session_state.video.write(frame)

            cv2.imshow("Inference", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                stop_event.set() 
                break
    if st.session_state.video:
        st.session_state.video.release()
        st.session_state.video = None
    
    cv2.destroyAllWindows()
    print("[INFO] Display process exited")



def projector_process(projector_queue, stop_event):
    # Nome da janela
    window_name = "Frame Projetado"

    # Criar a janela como NORMAL para evitar problemas de exibição
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # Mover a janela para o projetor (HDMI-2)
    # cv2.moveWindow(window_name, 1920, 0)

    # Ajustar o tamanho manualmente
    # cv2.resizeWindow(window_name, 1920, 1079)

    # Garantir que a janela está em tela cheia no projetor
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while not stop_event.is_set():
        if not projector_queue.empty():
            frame, text_info, text_instruction = projector_queue.get()

            # Obter dimensões do frame
            height, width, _ = frame.shape
            bar_height = 50  # Altura da faixa preta

            # Definir propriedades do texto
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 3
            text_color = (255, 255, 255)  # Branco
            thickness = 2
            padding = 10  # Espaço extra ao redor do texto
            line_spacing = 20  # Espaço entre os textos

            # ---- Adicionar text_instruction (PRIMEIRO TEXTO) ----
            text_size_instr = cv2.getTextSize(text_instruction, font, font_scale, thickness)[0]
            text_x_instr = (width - text_size_instr[0]) // 2  # Centralizar no eixo X
            text_y_instr = bar_height + 50  # Ajustar no eixo Y

            # Retângulo de fundo do primeiro texto
            rect_x1 = text_x_instr - padding
            rect_y1 = text_y_instr - text_size_instr[1] - padding
            rect_x2 = text_x_instr + text_size_instr[0] + padding
            rect_y2 = text_y_instr + padding

            cv2.rectangle(frame, (rect_x1, rect_y1), (rect_x2, rect_y2), (0, 0, 0), -1)
            cv2.putText(frame, text_instruction, (text_x_instr, text_y_instr), font, font_scale, text_color, thickness, cv2.LINE_AA)

            # ---- Adicionar text_info (SEGUNDO TEXTO, LOGO ABAIXO) ----
            text_size_info = cv2.getTextSize(text_info, font, font_scale, thickness)[0]
            text_x_info = (width - text_size_info[0]) // 2  # Centralizar no eixo X
            text_y_info = text_y_instr + text_size_instr[1] + line_spacing  # Ajustar abaixo do primeiro texto

            # Retângulo de fundo do segundo texto
            rect_x1_info = text_x_info - padding
            rect_y1_info = text_y_info - text_size_info[1] - padding
            rect_x2_info = text_x_info + text_size_info[0] + padding
            rect_y2_info = text_y_info + padding

            cv2.rectangle(frame, (rect_x1_info, rect_y1_info), (rect_x2_info, rect_y2_info), (0, 0, 0), -1)
            cv2.putText(frame, text_info, (text_x_info, text_y_info), font, font_scale, text_color, thickness, cv2.LINE_AA)

            # Exibir o frame no projetor
            cv2.imshow(window_name, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                stop_event.set()
                break

    cv2.destroyAllWindows()
    print("[INFO] Projector process exited")


def update_monitoring(step_status):
    # status image path
    todo_img = os.getcwd() + "/static/TODO.png"
    done_img = os.getcwd() + "/static/DONE.png"

    progress_placeholder = st.empty()  # Placeholder for progress bar
    steps_completed_placeholder = st.empty()  # Placeholder for completed steps count
    
    while True:
        status = step_status.get()
        for key, value in status.items():
            with st.session_state.columns[f"col2_{key}"]:
                # Update img placeholder
                status_img = done_img if value == True else todo_img
                st.session_state.image_placeholders[key].image(status_img, width=30)

            # Show assembly progress
            total_steps = len(status)
            steps_completed = sum(1 for value in status.values() if value)  # Count how many steps are completed (value == True)
            progress = steps_completed / total_steps

            # Update progress bar
            progress_placeholder.progress(progress)

            # Update the number of completed steps
            steps_completed_placeholder.write(f"{steps_completed}/{total_steps} steps completed")

        time.sleep(5)
