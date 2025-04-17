import roboflow

rf = roboflow.Roboflow(api_key="i5nlY5Tsgam9Mdnezrfj")
project = rf.workspace().project("lego-tlftx")

#can specify weights_filename, default is "weights/best.pt"
version = project.version("2")
version.deploy("yolov11", "/home/bruno/projects/ultralytics/runs/detect/train/weights/", "best.pt")

