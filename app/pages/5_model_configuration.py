import streamlit as st

from lib.nodes import *
from tasks.detection.detection import *
import re

from importlib import metadata
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # YOLO

#from ultralytics.utils.checks import check_requirements
#from ultralytics.utils.downloads import GITHUB_ASSETS_STEMS

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

def parse_version(version="0.0.0") -> tuple:
    """
    Convert a version string to a tuple of integers, ignoring any extra non-numeric string attached to the version. This
    function replaces deprecated 'pkg_resources.parse_version(v)'.

    Args:
        version (str): Version string, i.e. '2.0.1+cpu'

    Returns:
        (tuple): Tuple of integers representing the numeric part of the version and the extra string, i.e. (2, 0, 1)
    """
    try:
        return tuple(map(int, re.findall(r"\d+", version)[:3]))  # '2.0.1+cpu' -> (2, 0, 1)
    except Exception as e:
        LOGGER.warning(f"WARNING ⚠️ failure for parse_version({version}), returning (0, 0, 0): {e}")
        return 0, 0, 0


def check_version(
    current: str = "0.0.0",
    required: str = "0.0.0",
    name: str = "version",
    hard: bool = False,
    verbose: bool = False,
    msg: str = "",
) -> bool:
    """
    Check current version against the required version or range.

    Args:
        current (str): Current version or package name to get version from.
        required (str): Required version or range (in pip-style format).
        name (str, optional): Name to be used in warning message.
        hard (bool, optional): If True, raise an AssertionError if the requirement is not met.
        verbose (bool, optional): If True, print warning message if requirement is not met.
        msg (str, optional): Extra message to display if verbose.

    Returns:
        (bool): True if requirement is met, False otherwise.

    Example:
        ```python
        # Check if current version is exactly 22.04
        check_version(current="22.04", required="==22.04")

        # Check if current version is greater than or equal to 22.04
        check_version(current="22.10", required="22.04")  # assumes '>=' inequality if none passed

        # Check if current version is less than or equal to 22.04
        check_version(current="22.04", required="<=22.04")

        # Check if current version is between 20.04 (inclusive) and 22.04 (exclusive)
        check_version(current="21.10", required=">20.04,<22.04")
        ```
    """
    if not current:  # if current is '' or None
        LOGGER.warning(f"WARNING ⚠️ invalid check_version({current}, {required}) requested, please check values.")
        return True
    elif not current[0].isdigit():  # current is package name rather than version string, i.e. current='ultralytics'
        try:
            name = current  # assigned package name to 'name' arg
            current = metadata.version(current)  # get version string from package name
        except metadata.PackageNotFoundError as e:
            if hard:
                raise ModuleNotFoundError(emojis(f"WARNING ⚠️ {current} package is required but not installed")) from e
            else:
                return False

    if not required:  # if required is '' or None
        return True

    if "sys_platform" in required and (  # i.e. required='<2.4.0,>=1.8.0; sys_platform == "win32"'
        (WINDOWS and "win32" not in required)
        or (LINUX and "linux" not in required)
        or (MACOS and "macos" not in required and "darwin" not in required)
    ):
        return True

    op = ""
    version = ""
    result = True
    c = parse_version(current)  # '1.2.3' -> (1, 2, 3)
    for r in required.strip(",").split(","):
        op, version = re.match(r"([^0-9]*)([\d.]+)", r).groups()  # split '>=22.04' -> ('>=', '22.04')
        if not op:
            op = ">="  # assume >= if no op passed
        v = parse_version(version)  # '1.2.3' -> (1, 2, 3)
        if op == "==" and c != v:
            result = False
        elif op == "!=" and c == v:
            result = False
        elif op == ">=" and not (c >= v):
            result = False
        elif op == "<=" and not (c <= v):
            result = False
        elif op == ">" and not (c > v):
            result = False
        elif op == "<" and not (c < v):
            result = False
    if not result:
        warning = f"WARNING ⚠️ {name}{op}{version} is required, but {name}=={current} is currently installed {msg}"
        if hard:
            raise ModuleNotFoundError(emojis(warning))  # assert version requirements met
        if verbose:
            LOGGER.warning(warning)
    return result

def check_requirements(requirements=ROOT.parent / "requirements.txt", exclude=(), install=True, cmds=""):
    """
    Check if installed dependencies meet YOLOv8 requirements and attempt to auto-update if needed.

    Args:
        requirements (Union[Path, str, List[str]]): Path to a requirements.txt file, a single package requirement as a
            string, or a list of package requirements as strings.
        exclude (Tuple[str]): Tuple of package names to exclude from checking.
        install (bool): If True, attempt to auto-update packages that don't meet requirements.
        cmds (str): Additional commands to pass to the pip install command when auto-updating.

    Example:
        ```python
        from ultralytics.utils.checks import check_requirements

        # Check a requirements.txt file
        check_requirements("path/to/requirements.txt")

        # Check a single package
        check_requirements("ultralytics>=8.0.0")

        # Check multiple packages
        check_requirements(["numpy", "ultralytics>=8.0.0"])
        ```
    """
    prefix = colorstr("red", "bold", "requirements:")
    if isinstance(requirements, Path):  # requirements.txt file
        file = requirements.resolve()
        assert file.exists(), f"{prefix} {file} not found, check failed."
        requirements = [f"{x.name}{x.specifier}" for x in parse_requirements(file) if x.name not in exclude]
    elif isinstance(requirements, str):
        requirements = [requirements]

    pkgs = []
    for r in requirements:
        r_stripped = r.split("/")[-1].replace(".git", "")  # replace git+https://org/repo.git -> 'repo'
        match = re.match(r"([a-zA-Z0-9-_]+)([<>!=~]+.*)?", r_stripped)
        name, required = match[1], match[2].strip() if match[2] else ""
        try:
            assert check_version(metadata.version(name), required)  # exception if requirements not met
        except (AssertionError, metadata.PackageNotFoundError):
            pkgs.append(r)
            
GITHUB_ASSETS_NAMES = (
    [f"yolov8{k}{suffix}.pt" for k in "nsmlx" for suffix in ("", "-cls", "-seg", "-pose", "-obb", "-oiv7")]
    + [f"yolo11{k}{suffix}.pt" for k in "nsmlx" for suffix in ("", "-cls", "-seg", "-pose", "-obb")]
    + [f"yolov5{k}{resolution}u.pt" for k in "nsmlx" for resolution in ("", "6")]
    + [f"yolov3{k}u.pt" for k in ("", "-spp", "-tiny")]
    + [f"yolov8{k}-world.pt" for k in "smlx"]
    + [f"yolov8{k}-worldv2.pt" for k in "smlx"]
    + [f"yolov9{k}.pt" for k in "tsmce"]
    + [f"yolov10{k}.pt" for k in "nsmblx"]
    + [f"yolo_nas_{k}.pt" for k in "sml"]
    + [f"sam_{k}.pt" for k in "bl"]
    + [f"FastSAM-{k}.pt" for k in "sx"]
    + [f"rtdetr-{k}.pt" for k in "lx"]
    + ["mobile_sam.pt"]
    + ["calibration_image_sample_data_20x128x128x3_float32.npy.zip"]
)
GITHUB_ASSETS_STEMS = [Path(k).stem for k in GITHUB_ASSETS_NAMES]

st.set_page_config(
    page_title="Create Task",
    page_icon="📌",
)
st.title("Create Task")

st.sidebar.header("Tasks")

st.write("""In this area you can register different computer vision tasks to be executed on your video source. """)

st.write("## Choose task type.")

selectBox_options = ["YOLO model"]

task_type = st.selectbox("Select one of the task types", selectBox_options, index=None, key=None, help=None, on_change=None, args=None, kwargs=None, placeholder="Choose an option")

task_name = st.text_input("Task name", placeholder="Insert task name")

if task_type == "YOLO model":

    from ultralytics import YOLO
    # Add dropdown menu for model selection
    available_models = [x.replace("yolo", "YOLO") for x in GITHUB_ASSETS_STEMS if x.startswith("yolo11")]

    selected_model = st.sidebar.selectbox("Model", available_models)
    
    with st.form("task"):

        # Upload model file
        #model_file = st.file_uploader("Upload model file")

        # Upload model config file
        #model_config = st.file_uploader("Upload model configuration file")

        # Set iou_thres
        iou = float(st.slider("Select confidence threshold",0.0, 1.00, 0.60))

        # set conf_thres
        conf = float(st.slider("Confidence Threshold", 0.0, 1.0, 0.25, 0.01))

        submit = st.form_submit_button(label="Create task")

        
        class_names = ["person"]

        # Multiselect box with class names and get indices of selected classes
        selected_classes = st.sidebar.multiselect("Classes", class_names, default=class_names)
        selected_ind = [class_names.index(option) for option in selected_classes]

        if submit: 

            detection_task = ObjectDetection(id=task_name, pos=(300,200), data={'content': task_name}, conf=conf, iou=iou)

            detection_task.load_model(selected_model)
               
            st.session_state['nodes'].append(detection_task.node)
            st.session_state['node_object'].append(detection_task)


    
