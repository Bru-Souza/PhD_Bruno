import streamlit as st

from lib.nodes import *
from tasks.detection.detection import *
from lib.utils import update_project_file

from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # YOLO


def colorstr(*input):
    r"""
    Colors a string based on the provided color and style arguments. Utilizes ANSI escape codes.
    See https://en.wikipedia.org/wiki/ANSI_escape_code for more details.

    This function can be called in two ways:
        - colorstr('color', 'style', 'your string')
        - colorstr('your string')

    In the second form, 'blue' and 'bold' will be applied by default.

    Args:
        *input (str | Path): A sequence of strings where the first n-1 strings are color and style arguments,
                      and the last string is the one to be colored.

    Supported Colors and Styles:
        Basic Colors: 'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'
        Bright Colors: 'bright_black', 'bright_red', 'bright_green', 'bright_yellow',
                       'bright_blue', 'bright_magenta', 'bright_cyan', 'bright_white'
        Misc: 'end', 'bold', 'underline'

    Returns:
        (str): The input string wrapped with ANSI escape codes for the specified color and style.

    Examples:
        >>> colorstr("blue", "bold", "hello world")
        >>> "\033[34m\033[1mhello world\033[0m"
    """
    *args, string = input if len(input) > 1 else ("blue", "bold", input[0])  # color arguments, string
    colors = {
        "black": "\033[30m",  # basic colors
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "bright_black": "\033[90m",  # bright colors
        "bright_red": "\033[91m",
        "bright_green": "\033[92m",
        "bright_yellow": "\033[93m",
        "bright_blue": "\033[94m",
        "bright_magenta": "\033[95m",
        "bright_cyan": "\033[96m",
        "bright_white": "\033[97m",
        "end": "\033[0m",  # misc
        "bold": "\033[1m",
        "underline": "\033[4m",
    }
    return "".join(colors[x] for x in args) + f"{string}" + colors["end"]

st.set_page_config(
    page_title="Model configuration",
    page_icon="📌",
)
st.title("Model configuration")

st.write("""In this area you can configure different computer vision models to be executed on your video source. """)

st.write("## Choose model type.")

model_options = ["Object detection"]

model_type = st.selectbox("Select one of the model types", model_options, index=None, key=None, help=None, on_change=None, args=None, kwargs=None, placeholder="Choose an option")

model_name = st.text_input("Model name", placeholder="Insert model name")

if model_type == "Object detection":

    # Add dropdown menu for model selection
    available_models = ["lego_v1", "lego_v2", "yolo11n"]

    st.session_state['selected_model'] = st.sidebar.selectbox("Model", available_models)
    
    with st.form("task"):

        # Set iou_thres
        iou = float(st.slider("Select IoU threshold",0.0, 1.00, 0.60))

        # set conf_thres
        conf = float(st.slider("Confidence Threshold", 0.0, 1.0, 0.60, 0.01))

        submit = st.form_submit_button(label="Create task")

        if st.session_state['selected_model'] == "lego_v1":
            class_names = ["block_1x2", "block_1x4_h", "block_2_8", "block_2x2_h", "wheel"]
        elif st.session_state['selected_model'] == "lego_v2":
            class_names = ['3003_dark_azure', '3004_black', '3004_sky_blue', '3010_sky_blue', '3020_black', '3022_black', '3034_turquoise', '3039_transparent', '3040a_black', '3137_wheel']
        elif st.session_state['selected_model'] == "yolo11n":
            class_names = ["person", "bus", "car"]

        # Multiselect box with class names and get indices of selected classes
        st.session_state['selected_classes'] = st.sidebar.multiselect("Classes", class_names, default=class_names)
        st.session_state['selected_ind'] = [class_names.index(option) for option in st.session_state['selected_classes']]

        if submit: 

            detection_task = ObjectDetection(id=st.session_state['selected_model'], pos=(250,200), data={'content': st.session_state['selected_model']}, conf=conf, iou=iou)

            st.session_state['nodes'].append(detection_task.node)
            st.session_state['node_object'].append(detection_task)
            
            st.success("Detection model was configured successfully.")

            # Save model info to project file
            update_project_file({"model":{"selected_model": st.session_state['selected_model'], "iou": iou, "conf": conf, "selected_ind": st.session_state['selected_ind'], "selected_classes": st.session_state['selected_classes']}})


    
