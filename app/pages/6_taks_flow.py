import logging
import streamlit as st

from lib.nodes import *
from lib.utils import *

from streamlit_flow import streamlit_flow
from streamlit_flow.state import StreamlitFlowState
from streamlit_flow.elements import StreamlitFlowEdge


if 'flow_initialized' not in st.session_state:
    st.session_state['flow_initialized'] = False


if 'edges' not in st.session_state:
    # Create output node
    output_node = OutputNode(id="output_1", pos=(600, 200), data={'content': 'Output Node'})

    # Add output node to session state
    st.session_state['node_object'].append(output_node)
        
    # Add the complete node object to the session
    st.session_state['nodes'].append(output_node.node)

    # Define edges as an empty list
    st.session_state['edges'] = []
    # Create initial workflow
    st.session_state.flow_state = StreamlitFlowState(st.session_state['nodes'], st.session_state['edges'])


# Create a new flow chart
if st.button("New"):
    st.session_state['edges'] = []
    # Define the new flow state
    st.session_state.flow_state = StreamlitFlowState(st.session_state['nodes'], st.session_state['edges'])
    st.session_state['flow_initialized'] = True
    logging.info("Creating new workflow.")

st.info('Load your workflow', icon=None)
# Get json filename
loaded_workflow = st.file_uploader("Upload your project (JSON file)", type="json")

if loaded_workflow is not None:
    try:
        # Define workflow project name
        edge_filename = st.session_state.project_folder +loaded_workflow.name

        if os.path.exists(edge_filename):
            with open(edge_filename, "r") as f:
                saved_edges = json.load(f)
            st.session_state['edges'] = [StreamlitFlowEdge(**edge_dict) for edge_dict in saved_edges]
            logging.info("Workflow loaded successfully.")
        else:
            st.session_state['edges'] = []
            logging.info("File saved_edges.json did not exists.")
            st.error("No edges file available.")
        
        st.session_state.flow_state = StreamlitFlowState(st.session_state['nodes'], st.session_state['edges'])
        st.session_state['flow_initialized'] = True
        st.success("Workflow loaded successfully!")

    
    except Exception as e:
            st.error(f"Error: {str(e)}")
            logging.error(f"Error: {str(e)}")


if st.session_state['flow_initialized']:
    # Renders the current workflow
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


# Button to save the new task flow
if st.button("Define flow", type="primary"):
    # Check connections
    edges = st.session_state.flow_state.edges
    
    # Step 1: Construct the graph as an adjacency dictionary
    graph = {}
    for edge in edges:
        source = edge.source
        target = edge.target
        
        if source not in graph:
            graph[source] = []
        graph[source].append(target)

    start_node = 'input_1'
    terminal_nodes = find_terminal_nodes(graph)
    # Execute the search
    all_possible_branches = []
    for end_node in terminal_nodes:
        paths = find_all_paths(graph, start_node, end_node)
        all_possible_branches.extend(paths)

    print(f'[INFO] Possible flow branches: {all_possible_branches}')

    # Save edges in project folder
    edge_filename = st.session_state.project_folder + "/saved_edges.json"
    with open(edge_filename, "w") as f:
        json.dump([edge.__dict__ for edge in edges], f)
        logging.info("Current flow edges saved to project folder.")
        
    # Set env variable
    st.session_state['all_possible_branches'] = all_possible_branches

    st.success("The new task flow was defined.")
    logging.info("The new task flow was defined.")
    logging.info(f"Possible flow branchs: {all_possible_branches}.")
