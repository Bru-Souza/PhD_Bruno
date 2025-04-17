from ultralytics import YOLO

# Load a model
model = YOLO("yolo11l.pt")  # load a pretrained model (recommended for training)


# Train the model
results = model.train(data="lego_v2.yaml", batch=8, epochs=150, imgsz=640)