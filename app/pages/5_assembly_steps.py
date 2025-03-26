import os
import streamlit as st

from PIL import Image
from lib.nodes import *
from lib.utils import update_project_file

st.set_page_config(
    page_title="Assembly steps",
    page_icon="📌",
)
st.title("Assembly steps registration")

st.write("""In this area you can configure and register different steps to the assembly process.""")

# Armazenar o contador e os IDs dos steps
if 'steps_id' not in st.session_state:
    st.session_state['steps_id'] = []
    st.session_state['count'] = 0

# Recuperando o nome do step diretamente do session_state
step_name = st.text_input("Create a step name", value=st.session_state.get('step_name', ""))

# Carregar o arquivo de template
template_file = st.file_uploader("Select template image", type=["jpg", "jpeg", "png"], key="template_uploader")

# Carregar o arquivo de instrução
instruction_file = st.file_uploader("Select instruction image", type=["jpg", "jpeg", "png"], key="instruction_uploader")

# Definir caminho base para salvar as imagens
save_path = os.path.join(st.session_state.project_folder, "imgs")
os.makedirs(save_path, exist_ok=True)  # Criar a pasta caso não exista

# Inicializar colunas para exibição lado a lado
col1, col2 = st.columns(2)

# Processar e exibir a imagem do template
if template_file is not None:
    template_img = Image.open(template_file)
    st.session_state['template_filename'] = os.path.join(save_path, template_file.name)
    template_img.save(st.session_state['template_filename'])

    # Redimensionar a imagem do template
    resized_template = template_img.resize((280, 280))

    # Exibir no Streamlit
    with col1:
        st.image(resized_template, caption="Template Image")

# Processar e exibir a imagem de instrução
if instruction_file is not None:
    instruction_img = Image.open(instruction_file)
    st.session_state['instruction_filename'] = os.path.join(save_path, instruction_file.name)
    instruction_img.save(st.session_state['instruction_filename'])

    # Exibir no Streamlit
    with col2:
        st.image(instruction_img, caption="Instruction Image")

# Define a classe do objeto
obj_cls = model_type = st.selectbox("Select the object class", st.session_state['selected_classes'], index=None, key=None, help=None, on_change=None, args=None, kwargs=None, placeholder="Choose an option")

# Create an assembly instruction
instruction_text = st.text_input("Assembly Instruction", "")
if instruction_text is not None:
    st.session_state['instruction_text'] = instruction_text

# Cria o step e limpa os campos
if st.button("Create step"):
    # Atualizar o contador e o ID dos steps
    st.session_state['count'] += 1
    st.session_state['steps_id'].append(st.session_state['count'])

    # Criar o nó do step
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

    # Atualizar listas de nós
    st.session_state['nodes'].append(assembly_step.node)

    # Adicionar o objeto node completo à sessão
    st.session_state['node_object'].append(assembly_step)

    # Save step to project_file
    update_project_file({"step_" + str(st.session_state['steps_id'][-1]): {"id": "step_" + str(st.session_state['steps_id'][-1]), "template_file": st.session_state['template_filename'], "instruction_file": st.session_state['instruction_filename'], "obj_cls": obj_cls, "instruction_text": st.session_state['instruction_text'] ,"obj_idx": obj_idx, "content": step_name}})