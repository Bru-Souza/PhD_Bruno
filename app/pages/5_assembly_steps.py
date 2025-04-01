import os
import logging
import streamlit as st

from PIL import Image
from lib.nodes import *
from lib.utils import update_project_file

# Set page configuration
st.set_page_config(
    page_title="Assembly steps",
    page_icon="📌",
)

# Set page title
st.title("Assembly steps registration")

st.write("""In this area you can configure and register different steps to the assembly process.""")

# Store the counter and step IDs
if 'steps_id' not in st.session_state:
    st.session_state['steps_id'] = []
    st.session_state['count'] = 0

# Retrieving step name directly from session_state
step_name = st.text_input("Create a step name", value=st.session_state.get('step_name', ""))

# Load the template file
template_file = st.file_uploader("Select template image", type=["jpg", "jpeg", "png"], key="template_uploader")

# Load the instruction file
instruction_file = st.file_uploader("Select instruction image", type=["jpg", "jpeg", "png"], key="instruction_uploader")

# Set base path to save images
save_path = os.path.join(st.session_state.project_folder, "imgs")
# Create the folder if it does not exist
os.makedirs(save_path, exist_ok=True)

# Initialize columns for side-by-side display
col1, col2 = st.columns(2)

# Process and display the template image
if template_file is not None:
    template_img = Image.open(template_file)
    st.session_state['template_filename'] = os.path.join(save_path, template_file.name)
    template_img.save(st.session_state['template_filename'])

    # Resize the template image
    resized_template = template_img.resize((280, 280))

    # View on Streamlit
    with col1:
        st.image(resized_template, caption="Template Image")

# Process and display the instruction image
if instruction_file is not None:
    instruction_img = Image.open(instruction_file)
    st.session_state['instruction_filename'] = os.path.join(save_path, instruction_file.name)
    instruction_img.save(st.session_state['instruction_filename'])

    # View on Streamlit
    with col2:
        st.image(instruction_img, caption="Instruction Image")

# Defines the class of the object
obj_cls = model_type = st.selectbox("Select the object class", st.session_state['selected_classes'], index=None, key=None, help=None, on_change=None, args=None, kwargs=None, placeholder="Choose an option")

# Create an assembly instruction
instruction_text = st.text_input("Assembly Instruction", "")
if instruction_text is not None:
    st.session_state['instruction_text'] = instruction_text

# Creates the step and clears the fields
if st.button("Create step"):
    logging.info(f"Creating step_{st.session_state['steps_id'][-1]}.")
    # Update the  counter and steps ID
    st.session_state['count'] += 1
    st.session_state['steps_id'].append(st.session_state['count'])

    # Create the step node
    assembly_step = AssemblyStepNode(
        id="step_" + str(st.session_state['steps_id'][-1]),
        pos=[400, 200 + (100 * (st.session_state['count'] -1))], 
        node_type='default', 
        source_position='right', 
        target_position='left', 
        data={'content': step_name}
    )

    obj_idx = st.session_state['selected_classes'].index(obj_cls)

    assembly_step.obj_cls = obj_cls
    assembly_step.obj_idx = obj_idx
    assembly_step.template_img_path = st.session_state['template_filename']
    assembly_step.instruction_img_path = st.session_state['instruction_filename']
    assembly_step.instruction_text = st.session_state['instruction_text']

    # Update node list
    st.session_state['nodes'].append(assembly_step.node)

    #Add the complete node object to the node object list
    st.session_state['node_object'].append(assembly_step)

    # Save step to project_file
    update_project_file({"step_" + str(st.session_state['steps_id'][-1]): {"id": "step_" + str(st.session_state['steps_id'][-1]), "template_file": st.session_state['template_filename'], "instruction_file": st.session_state['instruction_filename'], "obj_cls": obj_cls, "instruction_text": st.session_state['instruction_text'] ,"obj_idx": obj_idx, "content": step_name}})

    logging.info(f"Step info - id: {st.session_state['steps_id'][-1]}, obj_cls: {obj_cls}, instruction_text: {st.session_state['instruction_text']} ,obj_idx: {obj_idx}, content: {step_name}.")
    logging.info(f"Step info - template_file: {st.session_state['template_filename']}, instruction_file: {st.session_state['instruction_filename']}.")

    