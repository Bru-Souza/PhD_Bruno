import random
import streamlit as st

from lib.nodes import *
from lib.utils import *

from streamlit_flow import streamlit_flow

# Inicializa o estado da sessão
if 'edges' not in st.session_state:
    st.session_state['edges'] = []
    st.session_state['flow_key'] = f'hackable_flow_{random.randint(0, 1000)}'

# Renderiza o fluxo de trabalho atual
streamlit_flow(
    key=st.session_state['flow_key'],
    init_nodes=st.session_state['nodes'],  # Converte os objetos Node para dicionários
    init_edges=st.session_state['edges'],
    fit_view=False,
    allow_new_edges=True,
    allow_zoom=True,
    pan_on_drag=True,
    enable_node_menu=True,
    enable_edge_menu=True
)

# Botão para criar novos nós
if st.button("Load Nodes"):

    flow_key = st.session_state['flow_key']

    output_node = OutputNode(id="output_1", pos=(600, 200), data={'content': 'Output Node'})

    # Adiciona os nós ao estado da sessão
    st.session_state['nodes'].append(output_node.node)
    # Reseta o fluxo
    del st.session_state[flow_key]
    st.session_state['flow_key'] = f'hackable_flow_{random.randint(0, 1000)}'

    # Adiciona o objeto node completo a sessão
    st.session_state['node_object'].append(output_node)

    st.rerun()


# Botão para salvar o novo flow de tasks
if st.button("Define flow", type="primary"):
    # Verificar conexões
    edges = st.session_state[st.session_state['flow_key']]['edges']
    
    # Passo 1: Construir o grafo como um dicionário de adjacências
    graph = {}
    for edge in edges:
        source = edge['source']
        target = edge['target']
        if source not in graph:
            graph[source] = []
        graph[source].append(target)

    start_node = 'input_1'
    terminal_nodes = find_terminal_nodes(graph)
    # Executar a busca
    print(graph)
    all_possible_branches = []
    for end_node in terminal_nodes:
        paths = find_all_paths(graph, start_node, end_node)
        all_possible_branches.extend(paths)

    print(f'[INFO] Possible flow branches: {all_possible_branches}')

    st.success("The new task flow was defined.")
    # Set env variable
    st.session_state['all_possible_branches'] = all_possible_branches

