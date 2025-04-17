import os
import cv2
import time
import logging
import numpy as np
import streamlit as st

from lib.utils import append_to_json
from tasks.detection.tracking import CustomTrackZone


def inference_process(frame_queue, prediction_queue, step_status, projector_queue, stop_event):
    logging.info("Inference process started.")
    # Start experiment timer
    startExp_time = time.time()

    # Track assembly step
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

    # Define ROI for template matching
    st.session_state.assembly_verifier.set_region_points(region_points)

    # Init TrackZone (Object Tracking in Zones, not complete frame)
    model_path = os.getcwd() + "/models/" + st.session_state.selected_model.lower() + ".pt"
    trackzone = CustomTrackZone(
        show=False,  # Display the output
        region=region_points,  # Pass region points
        model=model_path,
        line_width=2,  # Adjust the line width for bounding boxes and text display
        classes=st.session_state['selected_ind'],
        iou=st.session_state.model_iou,
        conf=st.session_state.model_conf,
        verbose=False
    )

    # Recognized ids storage
    st.session_state.recognized_ids = set()
    
    # Store node_objects
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
                        frame_cp = frame.copy()
                        # Infer
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
                            is_match, confidence, result_tamplate_img = st.session_state.assembly_verifier.verify(frame_cp)
                            if is_match and confidence >= obj.obj_match_conf:
                                print(f"[INFO] Template matching confidence: {confidence}.")
                                # Save template matching result
                                tm_img_path = st.session_state.project_folder + f"/template_matching_{current_step}.png"
                                cv2.imwrite(tm_img_path, result_tamplate_img)

                                obj.match = True
                                st.session_state.status_dict[obj.id] = True
                                step_status.put(st.session_state.status_dict)
                                projector_queue.put(("flash_green",))
                                print(f"[INFO] Step {obj.id} is done!")
                                endStep_time = time.time()
                                totalStep_time = endStep_time - startStep_time

                                append_to_json(st.session_state.json_path, {f"{current_step}": totalStep_time})

                                step_number += 1
                                if step_number == len(st.session_state.steps_order):
                                    print("[INFO] Assembly process is completed!")
                                    assembly_info = "Assembly process is completed!"
                                    logging.info("Assembly process completed.")

                                    # Stop experiment timer
                                    endExp_time = time.time()
                                    totalExp_time = endExp_time - startExp_time
                                    append_to_json(st.session_state.json_path, {"Total experiment time": totalExp_time})
                                    time.sleep(0.5)
                                    stop_event.set() 
                                    logging.info("Setting stop_event.")
                        
                        # Send frame and detections for visualization
                        if not prediction_queue.full():
                            prediction_queue.put((annotated_frame, boxes))
                        
                        # Send projections
                        if not projector_queue.full():
                            projector_queue.put((assembly_visual_instruction, assembly_info, assembly_text_instruction))

                    time.sleep(0.01)


def capture_frames_process(frame_queue, stop_event):
    """
    Capturing frames in a separate process
    """
    logging.info("Capture frame process started.")
    cap = cv2.VideoCapture(st.session_state.uploaded_file_path)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break

        if not frame_queue.full():
            frame_queue.put(frame)
        time.sleep(0.03)

    cap.release()
    logging.info("Camera released.")
    print("[INFO] Camera released")


def display_process(prediction_queue, stop_event):
    """
    Função de exibição de frames    
    """
    logging.info("Display frame process started.")

    while not stop_event.is_set():
        if not prediction_queue.empty():
            frame, _ = prediction_queue.get()

            # Save video frame
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
    logging.info("Display frame process exited.")


def projector_process(projector_queue, stop_event):
    logging.info("Projector process started.")

    # Set window name
    window_name = "Frame Projetado"

    # Create the window as NORMAL to avoid display issues
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # Move window to projector (HDMI-2)
    # cv2.moveWindow(window_name, 1920, 0)

    # Adjust the size manually
    # cv2.resizeWindow(window_name, 1920, 1079)

    # Ensure the window is full screen on the projector
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while not stop_event.is_set():
        if not projector_queue.empty():

            item = projector_queue.get()

            # Check special command
            if isinstance(item, tuple) and isinstance(item[0], str) and item[0] == "flash_green":
                logging.info("Received green flash command.")
                
                # Create green signal 3s
                green_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
                green_frame[:] = (0, 200, 0)  # Verde

                # Define duration
                duration = 3  # seconds
                interval = 0.25  # seconds
                start_time = time.time()

                toggle = True
                
                while time.time() - start_time < duration and not stop_event.is_set():
                    frame_to_show = green_frame if toggle else rotated_frame
                    rotated = cv2.rotate(frame_to_show, cv2.ROTATE_180)
                    cv2.imshow(window_name, frame_to_show)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        stop_event.set()
                        break

                    time.sleep(interval)
                    toggle = not toggle
                continue
            
            frame, text_info, text_instruction = item

            # Get frame dimensions
            height, width, _ = frame.shape
            bar_height = 50  #Black band height

            # Set text properties
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 3
            text_color = (255, 255, 255)  # white
            thickness = 2
            padding = 10  # Extra space around text
            line_spacing = 20  # Space between texts

            # ---- Add text_instruction (FIRST TEXT) ----
            text_size_instr = cv2.getTextSize(text_instruction, font, font_scale, thickness)[0]
            text_x_instr = (width - text_size_instr[0]) // 2  # Center on X axis
            text_y_instr = bar_height + 50  # Snap to Y axis

            # First text background rectangle
            rect_x1 = text_x_instr - padding
            rect_y1 = text_y_instr - text_size_instr[1] - padding
            rect_x2 = text_x_instr + text_size_instr[0] + padding
            rect_y2 = text_y_instr + padding

            cv2.rectangle(frame, (rect_x1, rect_y1), (rect_x2, rect_y2), (0, 0, 0), -1)
            cv2.putText(frame, text_instruction, (text_x_instr, text_y_instr), font, font_scale, text_color, thickness, cv2.LINE_AA)

            #---- Add text_info (SECOND TEXT) ----
            text_size_info = cv2.getTextSize(text_info, font, font_scale, thickness)[0]
            text_x_info = (width - text_size_info[0]) // 2  # Center on X axis
            text_y_info = text_y_instr + text_size_instr[1] + line_spacing  # Fit below first text

            # Second text background rectangle
            rect_x1_info = text_x_info - padding
            rect_y1_info = text_y_info - text_size_info[1] - padding
            rect_x2_info = text_x_info + text_size_info[0] + padding
            rect_y2_info = text_y_info + padding

            cv2.rectangle(frame, (rect_x1_info, rect_y1_info), (rect_x2_info, rect_y2_info), (0, 0, 0), -1)
            cv2.putText(frame, text_info, (text_x_info, text_y_info), font, font_scale, text_color, thickness, cv2.LINE_AA)

            rotated_frame = cv2.rotate(frame, cv2.ROTATE_180)
            # Display the frame on the projector
            cv2.imshow(window_name, rotated_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                stop_event.set()
                break

    cv2.destroyAllWindows()
    print("[INFO] Projector process exited")
    logging.info("Projector process exited.")


def update_monitoring(step_status):
    logging.info("Monitoring view update.")
    
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
