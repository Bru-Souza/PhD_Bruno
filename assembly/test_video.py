from inference import get_model


from inference import InferencePipeline
from inference.core.interfaces.stream.sinks import render_boxes

pipeline = InferencePipeline.init(
    model_id="lego-tlftx/1",
    video_reference=0,
    on_prediction=render_boxes
)

pipeline.start()
pipeline.join()