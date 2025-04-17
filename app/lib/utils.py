'''
Lib for util functions

'''
import os
import json
import logging
import streamlit as st

from lib.nodes import InputNode, AssemblyStepNode
from tasks.detection.detection import *


def setup_logger():
    """
    Creates a log file for the given project. Configures the logging system to write logs to the specified file.

    Returns:
        str: The path to the log file.
    """
    log_file = os.path.join(st.session_state.project_folder, f"{st.session_state.project_file}.log")

    # Configure logging
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode="a",  # "a" para append, garantindo que não sobrescreva o log anterior
    )

    logging.info("Log file created for project: %s", st.session_state.project_file)
    
    return log_file

    
def dfs(graph, start, end, path, all_paths):
    '''
    # Função de DFS
    '''
    path.append(start)

    if start == end:
        all_paths.append(list(path))
    elif start in graph:
        for neighbor in graph[start]:
            if neighbor not in path:  # Evitar ciclos
                dfs(graph, neighbor, end, path, all_paths)
    
    path.pop()  # Voltar um passo na recursão


def find_all_paths(graph, start_node, end_node):
    '''
    Função que aplica o DFS para encontrar todos os caminhos
    '''
    all_paths = []
    dfs(graph, start_node, end_node, [], all_paths)
    return all_paths


def find_terminal_nodes(graph):
    # Finds nodes that have no outgoing connections (terminals)
    all_sources = set(graph.keys())  # Nodes that are the source of a connection
    all_targets = {target for targets in graph.values() for target in targets} # All nodes that are targets of connections
    terminal_nodes = list(all_targets - all_sources)  # Nodes that are only targets (have no way out)
    return terminal_nodes


def save_project_to_json(project_name):
    """
    Function to save the project dictionary to a JSON file
    """

    # Define o caminho da pasta do projeto
    st.session_state.project_folder = os.path.join(os.getcwd(), f"projects/project_{project_name}")
    
    # Cria a pasta se ela não existir
    os.makedirs(st.session_state.project_folder, exist_ok=True)
    
    # Define o caminho do arquivo JSON dentro da pasta
    file_name = os.path.join(st.session_state.project_folder, f"{project_name}.json")
    
    # Estrutura de dados do projeto
    project_dict = {"project_name": project_name}
    
    # Salva o JSON no arquivo
    with open(file_name, 'w') as json_file:
        json.dump(project_dict, json_file, indent=4)
    
    return file_name


def update_project_file(new_data):
    # Abrir o arquivo JSON
    with open(st.session_state.project_file, 'r') as f:
        project_data = json.load(f)
    
    # Adiciona os novos dados ao JSON carregado
    project_data.update(new_data)  

    # Salvar os dados modificados de volta ao arquivo JSON
    with open(st.session_state.project_file, 'w') as f:
        json.dump(project_data, f, indent=4)

    st.success("Novos dados foram adicionados e o arquivo JSON foi atualizado!")


def get_project_data(project_data):
    logging.info("Getting project data.")
    # Initialize session variables if they do not exist
    if 'nodes' not in st.session_state:
        st.session_state['nodes'] = []
    if 'node_object' not in st.session_state:
        st.session_state['node_object'] = []
    if 'selected_classes' not in st.session_state:
        st.session_state['selected_classes'] = []
    if 'selected_ind' not in st.session_state:
        st.session_state['selected_ind'] = []
    if 'canvas_result' not in st.session_state:
        st.session_state['canvas_result'] = {}
    if 'count' not in st.session_state:
        st.session_state['count'] = 0
    
    # Assign core session variables
    st.session_state.videoSrc_type = project_data.get('videoSrc_type', None)
    st.session_state.uploaded_file_path = project_data.get('source', None)
    st.session_state.video_running = False
    
    if st.session_state.videoSrc_type == "Video file":
        st.session_state.uploaded_file_path = st.session_state.project_folder + st.session_state.uploaded_file_path

    # Create Input Node
    input_node = InputNode(
        id="input_1",
        pos=(100, 200),
        data={'source_type': st.session_state.videoSrc_type, 'source': st.session_state.uploaded_file_path, 'content': 'Video Source'}
    )
    
    st.session_state['nodes'].append(input_node.node)
    st.session_state['node_object'].append(input_node)
    
    # Restore canvas information
    st.session_state["canvas_result"] = project_data.get("canvas_result", {})
    
    # Model configuration
    model_data = project_data.get("model", {})
    selected_model = model_data.get("selected_model", "")
    st.session_state.model_iou = model_data.get("iou", 0.7)
    st.session_state.model_conf = model_data.get("conf", 0.6)
    selected_classes = model_data.get("selected_classes", [])
    selected_ind = model_data.get("selected_ind", [])
    
    detection_task = ObjectDetection(
        id=selected_model,
        pos=(250, 200),
        data={'content': selected_model},
        conf=st.session_state.model_conf,
        iou=st.session_state.model_iou 
    )
    
    st.session_state['nodes'].append(detection_task.node)
    st.session_state['node_object'].append(detection_task)
    st.session_state['selected_classes'] = selected_classes
    st.session_state['selected_ind'] = selected_ind
    st.session_state['selected_model'] = selected_model

    # Initializes variable to store the model
    if 'model' not in st.session_state:
        st.session_state['model'] = detection_task

    # Load the steps
    for key, value in project_data.items():
        if key.startswith("step_"):

            st.session_state['count']+=1
            step_id = value.get("id", "")
            content = value.get("content", "")
            
            assembly_step = AssemblyStepNode(
                id=step_id,
                pos=[400, 200 + (100 * (st.session_state['count'] -1))], 
                node_type='default',
                source_position='right',
                target_position='left',
                data={'content': content}
            )
            assembly_step.obj_cls = value.get("obj_cls", "")
            assembly_step.obj_idx = value.get("obj_idx", "")
            assembly_step.obj_match_conf = value.get("obj_match_conf", "")
            assembly_step.template_img_path =  value.get("template_file", "")
            assembly_step.instruction_img_path = value.get("instruction_file", "")
            assembly_step.instruction_text = value.get("instruction_text", "")

            st.session_state['nodes'].append(assembly_step.node)
            st.session_state['node_object'].append(assembly_step)


def print_session_state():
    """ Função para imprimir todas as variáveis de sessão """
    for key, value in st.session_state.items():
        print(f"{key}: {value}")


def get_next_experiment_filename(base_folder, extension):
    os.makedirs(base_folder, exist_ok=True)
    exp_num = 1
    while os.path.exists(os.path.join(base_folder, f"exp_{exp_num:02d}.{extension}")):
        exp_num += 1
    return os.path.join(base_folder, f"exp_{exp_num:02d}.{extension}")


def append_to_json(json_path, new_data):
    if os.path.exists(json_path):
        with open(json_path, "r") as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    # Update the data
    data.update(new_data)

    # Rewrites the JSON with the updated data
    with open(json_path, "w") as json_file:
        json.dump(data, json_file, indent=4)