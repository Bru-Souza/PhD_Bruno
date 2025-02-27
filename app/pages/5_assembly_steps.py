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

# Carregar o arquivo de imagem
uploaded_file = st.file_uploader("Selecione uma imagem de template", type=["jpg", "jpeg", "png"], key="file_uploader")

# Verificar se o arquivo foi carregado
if uploaded_file is not None:
    # Ler a imagem usando o PIL
    image = Image.open(uploaded_file)
    #  Salvar a imagem
    save_path = os.path.join(st.session_state.project_folder, "imgs")
    # Criar a pasta caso não exista
    os.makedirs(save_path, exist_ok=True)
    
    st.session_state['image_filename'] = os.path.join(save_path, uploaded_file.name)
    image.save(st.session_state['image_filename'])

    # Resize image
    new_size = (280,280)
    resized_img = image.resize(new_size)
    
    # Exibir a imagem no Streamlit
    st.image(resized_img, caption="Imagem carregada")

# Define a classe do objeto
obj_cls = model_type = st.selectbox("Select the object class", st.session_state['selected_classes'], index=None, key=None, help=None, on_change=None, args=None, kwargs=None, placeholder="Choose an option")

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
    assembly_step.template_img_path = st.session_state['image_filename']

    # Atualizar listas de nós
    st.session_state['nodes'].append(assembly_step.node)

    # Adicionar o objeto node completo à sessão
    st.session_state['node_object'].append(assembly_step)

    # Save step to project_file
    update_project_file({"step_" + str(st.session_state['steps_id'][-1]): {"id": "step_" + str(st.session_state['steps_id'][-1]), "uploaded_file": st.session_state['image_filename'], "obj_cls": obj_cls, "obj_idx": obj_idx, "content": step_name}})