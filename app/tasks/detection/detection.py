import os
from lib.nodes import *
from ultralytics import YOLO

class ObjectDetection(TaskNode):

    def __init__(self, id, pos, data, conf, iou):
        super().__init__(id, pos, data)

        self.conf: float = conf
        self.iou: float = iou
        self.class_names: list = []
        self.selected_ind: list = [0]
        self.model = None


    def process_task(self, frame):
        # Perform inference
        results = self.model(frame, conf=self.conf, iou=self.iou, classes=self.selected_ind)
        annotated_frame = results[0].plot()  # Add annotations on frame
        return annotated_frame


    def load_model(self, selected_model):
        self.model = YOLO(f"{os.getcwd()}/models/{selected_model.lower()}.pt")  # Load the YOLO model
        return

    
    def set_selected_ind(self, selected_ind: list):
        self.selected_ind = selected_ind
        return
