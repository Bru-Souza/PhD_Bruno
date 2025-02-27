import os
import cv2
import time
import multiprocessing
import streamlit as st

os.environ['YOLO_VERBOSE'] = 'False'

from lib.template_matching.assembly_verification import AssemblyVerification
from tasks.detection.tracking import CustomTrackZone

# Sinal global para encerrar os processos
stop_event = multiprocessing.Event()

st.set_page_config(page_title="Assembly", page_icon="📺")
st.title("Aseembly Runner")

steps_order: list = []

# Armazene os node_objects
node_objects = st.session_state['node_object']

# Botões de controle do assembly
if st.button("Play Assembly"):
    
    if "assembly_runner" not in st.session_state:
        st.session_state.assembly_runner = True
        # st.session_state.model.load_model(st.session_state.selected_model)

    # Iterar sobre os ramos e obter os steps
    for node in st.session_state['all_possible_branches'][0]:
        if node.startswith("step"):
            steps_order.append(node)

    # Inicialização do verificador de template
    assembly_verifier = AssemblyVerification()

    def inference_process(frame_queue, prediction_queue, stop_event):
        global step_number, complete

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
                print("Error getting region points")

        else:
            print("No canvas result available")
            h, w, _ = frame_queue.get().shape
            region_points = [(0, 0), (w, 0), (w, h), (0, h)]

        
        # Init TrackZone (Object Tracking in Zones, not complete frame)
        trackzone = CustomTrackZone(
            show=False,  # Display the output
            region=region_points,  # Pass region points
            model=st.session_state.selected_model,  # You can use any model that Ultralytics support, i.e. YOLOv9, YOLOv10
            line_width=2,  # Adjust the line width for bounding boxes and text display
            verbose=False
        )

        for step in steps_order:
            current_step = step

            for obj in node_objects:
                if obj.id == current_step:
                    print(f"Current step: {current_step}")

                    # Get current cls
                    expected_class = obj.obj_idx

                    # Get current template img
                    expected_template = cv2.imread(obj.template_img_path)
                    
                    while obj.match == False and not stop_event.is_set():
                        if not frame_queue.empty():

                            frame = frame_queue.get()

                            # Inferência
                            annotated_frame, boxes, track_ids, clss = trackzone.trackzone(frame)

                            # Iterate over boxes, track ids, classes indexes
                            for box, track_id, cls in zip(boxes, track_ids, clss):
                                if int(cls) == expected_class and obj.recognized is False:
                                    assembly_track.add(cls)
                                    obj.recognized = True
                                    print(f"[INFO] Object {cls} was recognized.")

                                    # Set template
                                    assembly_verifier.set_template(expected_template)
                                    break

                            if obj.recognized is True and expected_template is not None:

                                is_match, confidence, result_tamplate_img = assembly_verifier.verify(frame)
                                is_match = True
                                if is_match:
                                    obj.match = True
                                    print(f"[INFO] Step {obj.id} is done!")
                                    step_number += 1
                                    print(step_number, steps_order)
                                    if step_number == len(steps_order):
                                        print("[INFO] Assembly process is completed!")
                                        complete.value = True
                                        time.sleep(0.5)
                                        print("[DEBUG] Setting stop_event...")
                                        stop_event.set() 
                                        break
                            # Enviar o frame e as previsões para exibição
                            if not prediction_queue.full():
                                prediction_queue.put((annotated_frame, boxes))

                        time.sleep(0.01)


    # Queue para dados compartilhados entre processos
    frame_queue = multiprocessing.Queue(maxsize=10)  # Limitar o tamanho da fila
    prediction_queue = multiprocessing.Queue(maxsize=10)  # Limitar o tamanho da fila
    complete = multiprocessing.Value('b', False)  # Garante o acesso compartilhado

    # Rastrear o estado da montagem
    assembly_track = set()
    step_number = 0
    active_parts_not_in_place = set({})

    # Captura de frames em um processo separado
    def capture_frames_process(frame_queue, stop_event):
        cap = cv2.VideoCapture(0)

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

                cv2.imshow("Inference", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    stop_event.set() 
                    break

        cv2.destroyAllWindows()
        print("[INFO] Display process exited")


    # Set dos processos
    capture_process = multiprocessing.Process(target=capture_frames_process, args=(frame_queue, stop_event))
    inference_process = multiprocessing.Process(target=inference_process, args=(frame_queue, prediction_queue, stop_event))
    display_process = multiprocessing.Process(target=display_process, args=(prediction_queue, stop_event))

    # Iniciar os processos
    capture_process.start()
    inference_process.start()
    display_process.start()

    # Join todos os processos
    capture_process.join()
    inference_process.join()
    display_process.join()



