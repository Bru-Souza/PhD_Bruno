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

# Inicializa o estado dos campos se não existir
st.session_state.setdefault('step_name', "")
st.session_state.setdefault('match_conf', "")
st.session_state.setdefault('instruction_text', "")
st.session_state.setdefault('template_filename', None)
st.session_state.setdefault('instruction_filename', None)

# Input de nome do passo
step_name = st.text_input("Create a step name", key="step_name")

# Uploads
template_file = st.file_uploader("Select template image", type=["jpg", "jpeg", "png"], key="template_uploader")
instruction_file = st.file_uploader("Select instruction image", type=["jpg", "jpeg", "png"], key="instruction_uploader")

# Set iou_thres
match_conf = float(st.slider("Select Template Matching threshold",0.0, 1.00, 0.50))

# Base path
save_path = os.path.join(st.session_state.project_folder, "imgs")
os.makedirs(save_path, exist_ok=True)

# Layout lado a lado
col1, col2 = st.columns(2)

# Processa e exibe template image
if template_file is not None:
    template_img = Image.open(template_file)
    st.session_state['template_filename'] = os.path.join(save_path, template_file.name)
    template_img.save(st.session_state['template_filename'])

    resized_template = template_img.resize((280, 280))
    with col1:
        st.image(resized_template, caption="Template Image")

# Processa e exibe instruction image
if instruction_file is not None:
    instruction_img = Image.open(instruction_file)
    st.session_state['instruction_filename'] = os.path.join(save_path, instruction_file.name)
    instruction_img.save(st.session_state['instruction_filename'])

    with col2:
        st.image(instruction_img, caption="Instruction Image")

# Classe do objeto
obj_cls = st.selectbox(
    "Select the object class",
    st.session_state['selected_classes'],
    index=0,
    key="obj_cls_select",
    placeholder="Choose an option"
)

# Instrução de montagem
instruction_text = st.text_input("Assembly Instruction", key="instruction_text")

# Botão de criação
if st.button("Create step"):
    st.session_state['count'] += 1
    step_id = "step_" + str(st.session_state['count'])
    st.session_state['steps_id'].append(st.session_state['count'])

    logging.info(f"Creating {step_id}.")

    assembly_step = AssemblyStepNode(
        id=step_id,
        pos=[400, 200 + (100 * (st.session_state['count'] - 1))],
        node_type='default',
        source_position='right',
        target_position='left',
        data={'content': step_name},
    )

    obj_idx = st.session_state['selected_classes'].index(obj_cls)

    assembly_step.obj_cls = obj_cls
    assembly_step.obj_idx = obj_idx
    assembly_step.obj_match_conf = match_conf
    assembly_step.template_img_path = st.session_state['template_filename']
    assembly_step.instruction_img_path = st.session_state['instruction_filename']
    assembly_step.instruction_text = instruction_text

    # Atualiza listas
    st.session_state['nodes'].append(assembly_step.node)
    st.session_state['node_object'].append(assembly_step)

    # Atualiza arquivo do projeto
    update_project_file({
        step_id: {
            "id": step_id,
            "template_file": st.session_state['template_filename'],
            "instruction_file": st.session_state['instruction_filename'],
            "obj_cls": obj_cls,
            "instruction_text": instruction_text,
            "obj_idx": obj_idx,
            "content": step_name,
            "obj_match_conf" :match_conf
        }
    })

    logging.info(f"Step info - id: {step_id}, obj_cls: {obj_cls}, obj_match_conf: {match_conf}, instruction_text: {instruction_text}, obj_idx: {obj_idx}, content: {step_name}.")
    logging.info(f"Files - template: {st.session_state['template_filename']}, instruction: {st.session_state['instruction_filename']}.")

    # Resetar campos após criação do step com segurança
    for key in ["step_name", "instruction_text", "template_filename", "instruction_filename",
                "template_uploader", "instruction_uploader", "obj_cls_select"]:
        if key in st.session_state:
            del st.session_state[key]

    st.rerun()

