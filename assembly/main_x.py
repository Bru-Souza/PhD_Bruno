
"""
python main_x.py -o "block_2_8, block_2x2_h, block_1x2" -m "lego-tlftx/1" -v 0 -c "block_1x2, block_1x4_h, block_2_8, block_2x2_h, wheel"

i5nlY5Tsgam9Mdnezrfj
export ROBOFLOW_API_KEY="i5nlY5Tsgam9Mdnezrfj"

"""
import optparse

import cv2
from inference import InferencePipeline

import supervision as sv

order = "block_2_8, block_2x2_h, block_1x4_h, block_2_8"
model_id = "lego-tlftx/2" 
classes = "block_1x2, block_1x4_h, block_2_8, block_2x2_h, wheel"

order = [i.strip() for i in order.split(",")]

tracked_ids = set({})
current_step = 0
active_parts_not_in_place = set({})
last_detection_was_wrong = False
classes = [i.strip() for i in classes.split(",")]
complete = False

tracker = sv.ByteTrack()
smoother = sv.DetectionsSmoother()


def on_prediction(inference_results, frame):
    global current_step
    global last_detection_was_wrong
    global complete

    predictions = sv.Detections.from_inference(inference_results).with_nms()
    predictions = tracker.update_with_detections(predictions)
    predictions = smoother.update_with_detections(predictions)

    predictions = predictions[predictions.confidence > 0.85]

    message = (
        f"Wrong part! Expected {order[current_step]}"
        if len(active_parts_not_in_place) > 0
        else None
    )

    for prediction in predictions:
        if prediction[4] in tracked_ids:
            continue

        class_name = classes[int(prediction[3])]

        if class_name == order[current_step]:
            tracked_ids.add(prediction[4])

            print(f"Part {class_name} in place")
            if current_step == len(order) - 1:
                print("Assembly complete!")
                complete = True
                break

            current_step = current_step + 1
            active_parts_not_in_place.clear()
            break
        elif class_name == order[current_step - 1]:
            tracked_ids.add(prediction[4])
            last_detection_was_wrong = False
            active_parts_not_in_place.clear()
        else:
            active_parts_not_in_place.add(prediction[4])
            last_detection_was_wrong = True

    bounding_box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()

    text_anchor = sv.Point(x=300, y=100)

    if complete:
        message = "Assembly complete!"

    next_step = f"Next part: {order[current_step]}" if message is None else message

    annotated_image = bounding_box_annotator.annotate(
        scene=frame.image, detections=predictions
    )
    annotated_image = label_annotator.annotate(
        scene=annotated_image,
        detections=predictions,
        labels=[classes[int(i[3])] for i in predictions],
    )
    annotated_image = sv.draw_text(
        scene=annotated_image,
        text=next_step,
        text_anchor=text_anchor,
        text_scale=1,
        background_color=sv.Color(r=255, g=255, b=255),
        text_color=sv.Color(r=0, g=0, b=0),
    )

    cv2.imshow("Inference", annotated_image)
    cv2.waitKey(1)


pipeline = InferencePipeline.init(
    model_id=model_id,
    video_reference=6,
    on_prediction=on_prediction
)

pipeline.start()

pipeline.join()