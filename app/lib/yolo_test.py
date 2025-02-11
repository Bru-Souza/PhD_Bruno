# # Ultralytics YOLO 🚀, AGPL-3.0 license

# import io
# import re
# import time

# import cv2
# import torch
# from importlib import metadata
# from pathlib import Path

# FILE = Path(__file__).resolve()
# ROOT = FILE.parents[1]  # YOLO

# #from ultralytics.utils.checks import check_requirements
# #from ultralytics.utils.downloads import GITHUB_ASSETS_STEMS

# def colorstr(*input):
#     r"""
#     Colors a string based on the provided color and style arguments. Utilizes ANSI escape codes.
#     See https://en.wikipedia.org/wiki/ANSI_escape_code for more details.

#     This function can be called in two ways:
#         - colorstr('color', 'style', 'your string')
#         - colorstr('your string')

#     In the second form, 'blue' and 'bold' will be applied by default.

#     Args:
#         *input (str | Path): A sequence of strings where the first n-1 strings are color and style arguments,
#                       and the last string is the one to be colored.

#     Supported Colors and Styles:
#         Basic Colors: 'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'
#         Bright Colors: 'bright_black', 'bright_red', 'bright_green', 'bright_yellow',
#                        'bright_blue', 'bright_magenta', 'bright_cyan', 'bright_white'
#         Misc: 'end', 'bold', 'underline'

#     Returns:
#         (str): The input string wrapped with ANSI escape codes for the specified color and style.

#     Examples:
#         >>> colorstr("blue", "bold", "hello world")
#         >>> "\033[34m\033[1mhello world\033[0m"
#     """
#     *args, string = input if len(input) > 1 else ("blue", "bold", input[0])  # color arguments, string
#     colors = {
#         "black": "\033[30m",  # basic colors
#         "red": "\033[31m",
#         "green": "\033[32m",
#         "yellow": "\033[33m",
#         "blue": "\033[34m",
#         "magenta": "\033[35m",
#         "cyan": "\033[36m",
#         "white": "\033[37m",
#         "bright_black": "\033[90m",  # bright colors
#         "bright_red": "\033[91m",
#         "bright_green": "\033[92m",
#         "bright_yellow": "\033[93m",
#         "bright_blue": "\033[94m",
#         "bright_magenta": "\033[95m",
#         "bright_cyan": "\033[96m",
#         "bright_white": "\033[97m",
#         "end": "\033[0m",  # misc
#         "bold": "\033[1m",
#         "underline": "\033[4m",
#     }
#     return "".join(colors[x] for x in args) + f"{string}" + colors["end"]

# def parse_version(version="0.0.0") -> tuple:
#     """
#     Convert a version string to a tuple of integers, ignoring any extra non-numeric string attached to the version. This
#     function replaces deprecated 'pkg_resources.parse_version(v)'.

#     Args:
#         version (str): Version string, i.e. '2.0.1+cpu'

#     Returns:
#         (tuple): Tuple of integers representing the numeric part of the version and the extra string, i.e. (2, 0, 1)
#     """
#     try:
#         return tuple(map(int, re.findall(r"\d+", version)[:3]))  # '2.0.1+cpu' -> (2, 0, 1)
#     except Exception as e:
#         LOGGER.warning(f"WARNING ⚠️ failure for parse_version({version}), returning (0, 0, 0): {e}")
#         return 0, 0, 0


# def check_version(
#     current: str = "0.0.0",
#     required: str = "0.0.0",
#     name: str = "version",
#     hard: bool = False,
#     verbose: bool = False,
#     msg: str = "",
# ) -> bool:
#     """
#     Check current version against the required version or range.

#     Args:
#         current (str): Current version or package name to get version from.
#         required (str): Required version or range (in pip-style format).
#         name (str, optional): Name to be used in warning message.
#         hard (bool, optional): If True, raise an AssertionError if the requirement is not met.
#         verbose (bool, optional): If True, print warning message if requirement is not met.
#         msg (str, optional): Extra message to display if verbose.

#     Returns:
#         (bool): True if requirement is met, False otherwise.

#     Example:
#         ```python
#         # Check if current version is exactly 22.04
#         check_version(current="22.04", required="==22.04")

#         # Check if current version is greater than or equal to 22.04
#         check_version(current="22.10", required="22.04")  # assumes '>=' inequality if none passed

#         # Check if current version is less than or equal to 22.04
#         check_version(current="22.04", required="<=22.04")

#         # Check if current version is between 20.04 (inclusive) and 22.04 (exclusive)
#         check_version(current="21.10", required=">20.04,<22.04")
#         ```
#     """
#     if not current:  # if current is '' or None
#         LOGGER.warning(f"WARNING ⚠️ invalid check_version({current}, {required}) requested, please check values.")
#         return True
#     elif not current[0].isdigit():  # current is package name rather than version string, i.e. current='ultralytics'
#         try:
#             name = current  # assigned package name to 'name' arg
#             current = metadata.version(current)  # get version string from package name
#         except metadata.PackageNotFoundError as e:
#             if hard:
#                 raise ModuleNotFoundError(emojis(f"WARNING ⚠️ {current} package is required but not installed")) from e
#             else:
#                 return False

#     if not required:  # if required is '' or None
#         return True

#     if "sys_platform" in required and (  # i.e. required='<2.4.0,>=1.8.0; sys_platform == "win32"'
#         (WINDOWS and "win32" not in required)
#         or (LINUX and "linux" not in required)
#         or (MACOS and "macos" not in required and "darwin" not in required)
#     ):
#         return True

#     op = ""
#     version = ""
#     result = True
#     c = parse_version(current)  # '1.2.3' -> (1, 2, 3)
#     for r in required.strip(",").split(","):
#         op, version = re.match(r"([^0-9]*)([\d.]+)", r).groups()  # split '>=22.04' -> ('>=', '22.04')
#         if not op:
#             op = ">="  # assume >= if no op passed
#         v = parse_version(version)  # '1.2.3' -> (1, 2, 3)
#         if op == "==" and c != v:
#             result = False
#         elif op == "!=" and c == v:
#             result = False
#         elif op == ">=" and not (c >= v):
#             result = False
#         elif op == "<=" and not (c <= v):
#             result = False
#         elif op == ">" and not (c > v):
#             result = False
#         elif op == "<" and not (c < v):
#             result = False
#     if not result:
#         warning = f"WARNING ⚠️ {name}{op}{version} is required, but {name}=={current} is currently installed {msg}"
#         if hard:
#             raise ModuleNotFoundError(emojis(warning))  # assert version requirements met
#         if verbose:
#             LOGGER.warning(warning)
#     return result

# def check_requirements(requirements=ROOT.parent / "requirements.txt", exclude=(), install=True, cmds=""):
#     """
#     Check if installed dependencies meet YOLOv8 requirements and attempt to auto-update if needed.

#     Args:
#         requirements (Union[Path, str, List[str]]): Path to a requirements.txt file, a single package requirement as a
#             string, or a list of package requirements as strings.
#         exclude (Tuple[str]): Tuple of package names to exclude from checking.
#         install (bool): If True, attempt to auto-update packages that don't meet requirements.
#         cmds (str): Additional commands to pass to the pip install command when auto-updating.

#     Example:
#         ```python
#         from ultralytics.utils.checks import check_requirements

#         # Check a requirements.txt file
#         check_requirements("path/to/requirements.txt")

#         # Check a single package
#         check_requirements("ultralytics>=8.0.0")

#         # Check multiple packages
#         check_requirements(["numpy", "ultralytics>=8.0.0"])
#         ```
#     """
#     prefix = colorstr("red", "bold", "requirements:")
#     if isinstance(requirements, Path):  # requirements.txt file
#         file = requirements.resolve()
#         assert file.exists(), f"{prefix} {file} not found, check failed."
#         requirements = [f"{x.name}{x.specifier}" for x in parse_requirements(file) if x.name not in exclude]
#     elif isinstance(requirements, str):
#         requirements = [requirements]

#     pkgs = []
#     for r in requirements:
#         r_stripped = r.split("/")[-1].replace(".git", "")  # replace git+https://org/repo.git -> 'repo'
#         match = re.match(r"([a-zA-Z0-9-_]+)([<>!=~]+.*)?", r_stripped)
#         name, required = match[1], match[2].strip() if match[2] else ""
#         try:
#             assert check_version(metadata.version(name), required)  # exception if requirements not met
#         except (AssertionError, metadata.PackageNotFoundError):
#             pkgs.append(r)
            
# GITHUB_ASSETS_NAMES = (
#     [f"yolov8{k}{suffix}.pt" for k in "nsmlx" for suffix in ("", "-cls", "-seg", "-pose", "-obb", "-oiv7")]
#     + [f"yolo11{k}{suffix}.pt" for k in "nsmlx" for suffix in ("", "-cls", "-seg", "-pose", "-obb")]
#     + [f"yolov5{k}{resolution}u.pt" for k in "nsmlx" for resolution in ("", "6")]
#     + [f"yolov3{k}u.pt" for k in ("", "-spp", "-tiny")]
#     + [f"yolov8{k}-world.pt" for k in "smlx"]
#     + [f"yolov8{k}-worldv2.pt" for k in "smlx"]
#     + [f"yolov9{k}.pt" for k in "tsmce"]
#     + [f"yolov10{k}.pt" for k in "nsmblx"]
#     + [f"yolo_nas_{k}.pt" for k in "sml"]
#     + [f"sam_{k}.pt" for k in "bl"]
#     + [f"FastSAM-{k}.pt" for k in "sx"]
#     + [f"rtdetr-{k}.pt" for k in "lx"]
#     + ["mobile_sam.pt"]
#     + ["calibration_image_sample_data_20x128x128x3_float32.npy.zip"]
# )
# GITHUB_ASSETS_STEMS = [Path(k).stem for k in GITHUB_ASSETS_NAMES]

# def inference(model=None):
#     """Performs real-time object detection on video input using YOLO in a Streamlit web application."""
#     check_requirements("streamlit>=1.29.0")  # scope imports for faster ultralytics package load speeds
#     import streamlit as st

#     from ultralytics import YOLO

#     # Hide main menu style
#     menu_style_cfg = """<style>MainMenu {visibility: hidden;}</style>"""

#     # Main title of streamlit application
#     main_title_cfg = """<div><h1 style="color:#FF64DA; text-align:center; font-size:40px; 
#                              font-family: 'Archivo', sans-serif; margin-top:-50px;margin-bottom:20px;">
#                     Ultralytics YOLO Streamlit Application
#                     </h1></div>"""

#     # Subtitle of streamlit application
#     sub_title_cfg = """<div><h4 style="color:#042AFF; text-align:center; 
#                     font-family: 'Archivo', sans-serif; margin-top:-15px; margin-bottom:50px;">
#                     Experience real-time object detection on your webcam with the power of Ultralytics YOLO! 🚀</h4>
#                     </div>"""

#     # Set html page configuration
#     st.set_page_config(page_title="Ultralytics Streamlit App", layout="wide", initial_sidebar_state="auto")

#     # Append the custom HTML
#     st.markdown(menu_style_cfg, unsafe_allow_html=True)
#     st.markdown(main_title_cfg, unsafe_allow_html=True)
#     st.markdown(sub_title_cfg, unsafe_allow_html=True)

#     # Add ultralytics logo in sidebar
#     with st.sidebar:
#         logo = "https://raw.githubusercontent.com/ultralytics/assets/main/logo/Ultralytics_Logotype_Original.svg"
#         st.image(logo, width=250)

#     # Add elements to vertical setting menu
#     st.sidebar.title("User Configuration")

#     # Add video source selection dropdown
#     source = st.sidebar.selectbox(
#         "Video",
#         ("webcam", "video"),
#     )

#     vid_file_name = ""
#     if source == "video":
#         vid_file = st.sidebar.file_uploader("Upload Video File", type=["mp4", "mov", "avi", "mkv"])
#         if vid_file is not None:
#             g = io.BytesIO(vid_file.read())  # BytesIO Object
#             vid_location = "ultralytics.mp4"
#             with open(vid_location, "wb") as out:  # Open temporary file as bytes
#                 out.write(g.read())  # Read bytes into file
#             vid_file_name = "ultralytics.mp4"
#     elif source == "webcam":
#         vid_file_name = 0

#     # Add dropdown menu for model selection
#     available_models = [x.replace("yolo", "YOLO") for x in GITHUB_ASSETS_STEMS if x.startswith("yolo11")]
#     if model:
#         available_models.insert(0, model.split(".pt")[0])  # insert model without suffix as *.pt is added later

#     selected_model = st.sidebar.selectbox("Model", available_models)
#     with st.spinner("Model is downloading..."):
#         model = YOLO(f"{selected_model.lower()}.pt")  # Load the YOLO model
#         class_names = list(model.names.values())  # Convert dictionary to list of class names
#     st.success("Model loaded successfully!")

#     # Multiselect box with class names and get indices of selected classes
#     selected_classes = st.sidebar.multiselect("Classes", class_names, default=class_names[:3])
#     selected_ind = [class_names.index(option) for option in selected_classes]

#     if not isinstance(selected_ind, list):  # Ensure selected_options is a list
#         selected_ind = list(selected_ind)

#     enable_trk = st.sidebar.radio("Enable Tracking", ("Yes", "No"))
#     conf = float(st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.25, 0.01))
#     iou = float(st.sidebar.slider("IoU Threshold", 0.0, 1.0, 0.45, 0.01))

#     col1, col2 = st.columns(2)
#     org_frame = col1.empty()
#     ann_frame = col2.empty()

#     fps_display = st.sidebar.empty()  # Placeholder for FPS display

#     if st.sidebar.button("Start"):
#         videocapture = cv2.VideoCapture(vid_file_name)  # Capture the video

#         if not videocapture.isOpened():
#             st.error("Could not open webcam.")

#         stop_button = st.button("Stop")  # Button to stop the inference

#         while videocapture.isOpened():
#             success, frame = videocapture.read()
#             if not success:
#                 st.warning("Failed to read frame from webcam. Please make sure the webcam is connected properly.")
#                 break

#             prev_time = time.time()  # Store initial time for FPS calculation

#             # Store model predictions
#             if enable_trk == "Yes":
#                 results = model.track(frame, conf=conf, iou=iou, classes=selected_ind, persist=True)
#             else:
#                 results = model(frame, conf=conf, iou=iou, classes=selected_ind)
#             annotated_frame = results[0].plot()  # Add annotations on frame

#             # Calculate model FPS
#             curr_time = time.time()
#             fps = 1 / (curr_time - prev_time)

#             # display frame
#             org_frame.image(frame, channels="BGR")
#             ann_frame.image(annotated_frame, channels="BGR")

#             if stop_button:
#                 videocapture.release()  # Release the capture
#                 torch.cuda.empty_cache()  # Clear CUDA memory
#                 st.stop()  # Stop streamlit app

#             # Display FPS in sidebar
#             fps_display.metric("FPS", f"{fps:.2f}")

#         # Release the capture
#         videocapture.release()

#     # Clear CUDA memory
#     torch.cuda.empty_cache()

#     # Destroy window
#     cv2.destroyAllWindows()


# # Main function call
# if __name__ == "__main__":
#     inference()