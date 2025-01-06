import optparse

import cv2
from inference import InferencePipeline
from inference.core.interfaces.camera.entities import VideoFrame
import supervision as sv

parser = optparse.OptionParser()

parser.add_option(
    "-o", "--order", action="store", dest="order", help="Order of parts to be assembled"
)
parser.add_option("-m", "--model_id", action="store", dest="model_id", help="Model ID")
parser.add_option(
    "-v",
    "--video",
    action="store",
    dest="video",
    help="Specify a camera ID or video file on which to run inference",
)
parser.add_option(
    "-c", "--classes", action="store", dest="classes", help="Classes of the model"
)

args = parser.parse_args()[0]

if not any([args.order, args.model_id, args.video, args.classes]):
    parser.error("Missing required arguments")

order = [i.strip() for i in args.order.split(",")]

tracked_ids = set({})
current_step = 0
active_parts_not_in_place = set({})
last_detection_was_wrong = False
classes = [i.strip() for i in args.classes.split(",")]
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

    text_anchor = sv.Point(x=200, y=100)

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

from inference.core.interfaces.stream.sinks import render_boxes

pipeline = InferencePipeline.init(
    model_id=args.model_id,
    video_reference=6,
    on_prediction=on_prediction
)

pipeline.start()

pipeline.join()

# This is example, reference implementation - you need to adjust the code to your purposes
#import os
#import json
#from inference.core.interfaces.camera.entities import VideoFrame
#from inference import InferencePipeline
#from typing import Any, List
#from ultralytics import YOLO
#from ultralytics.engine.results import Results 

#TARGET_DIR = "/home/bruno/projects/PhD_Bruno/assembly/my_predictions/"

#class MyModel:
#
#  def __init__(self, weights_path: str):
#    self._model = YOLO(weights_path)
#
#  # before v0.9.18  
#  def infer(self, video_frame: VideoFrame) -> Any:
#    return self._model(video_frame.image)
#
#  # after v0.9.18  
#  def infer(self, video_frames: List[VideoFrame]) -> List[Any]: 
#    # result must be returned as list of elements representing model prediction for single frame
#    # with order unchanged.
#    return self._model([v.image for v in video_frames])

#def save_prediction(prediction: Results, video_frame) -> None:
#    # Cria o diretório de destino, se não existir
#    os.makedirs(TARGET_DIR, exist_ok=True)
#    
#    # Define o caminho do arquivo de saída
#    file_path = os.path.join(TARGET_DIR, f"{video_frame.frame_id}.json")
#    
#    # Serializa o objeto Results para JSON
#    if isinstance(prediction, Results):
#        prediction_json = prediction.to_json()  # Gera uma string JSON
#    else:
#        raise TypeError(f"Object of type {type(prediction).__name__} is not serializable using tojson()")
#
#    # Salva a string JSON em um arquivo
#    with open(file_path, "w") as f:
#        f.write(prediction_json)

#my_model = MyModel("/home/bruno/projects/ultralytics/runs/detect/train/weights/best.pt")

#pipeline = InferencePipeline.init_with_custom_logic(
#  video_reference=0,
#  on_video_frame=my_model.infer,
#  on_prediction=on_prediction,
#)

## start the pipeline
#pipeline.start()
## wait for the pipeline to finish
#pipeline.join()


