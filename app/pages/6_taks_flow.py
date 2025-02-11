import random
import streamlit as st

from lib.nodes import *
from lib.utils import *

from streamlit_flow import streamlit_flow
from streamlit_flow.state import StreamlitFlowState

# Inicializa o estado da sessão
if 'edges' not in st.session_state and "output_1" not in st.session_state['node_object']:
    st.session_state['edges'] = []
    st.session_state.flow_state = StreamlitFlowState(st.session_state['nodes'], st.session_state['edges'])
    
    output_node = OutputNode(id="output_1", pos=(600, 200), data={'content': 'Output Node'})

    st.session_state.flow_state.nodes.append(output_node.node)
        
    # Adiciona o objeto node completo a sessão
    st.session_state['node_object'].append(output_node)


# Renderiza o fluxo de trabalho atual
st.session_state.flow_state = streamlit_flow('flow', 
								st.session_state.flow_state,
								fit_view=False, 
								enable_node_menu=True,
								enable_edge_menu=True,
								enable_pane_menu=True,
								get_edge_on_click=True,
								get_node_on_click=True, 
								hide_watermark=True, 
								allow_new_edges=True,
                                )


# Botão para salvar o novo flow de tasks
if st.button("Define flow", type="primary"):
    
    # Verificar conexões
    edges = st.session_state.flow_state.edges
    
    # Passo 1: Construir o grafo como um dicionário de adjacências
    graph = {}
    for edge in edges:
        source = edge.source
        target = edge.target
        
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
