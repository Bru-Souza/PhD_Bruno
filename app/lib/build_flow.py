# Conexões do fluxograma
edges = [
    {'source': '1', 'sourceHandle': None, 'target': '3', 'targetHandle': None, 'animated': False, 'labelShowBg': False, 'id': 'reactflow__edge-1-3', 'labelStyle': {'fill': 'black'}, 'selected': False},
    {'source': '1', 'sourceHandle': None, 'target': '2', 'targetHandle': None, 'animated': False, 'labelShowBg': False, 'id': 'reactflow__edge-1-2', 'labelStyle': {'fill': 'black'}, 'selected': False},
    {'source': '2', 'sourceHandle': None, 'target': '4', 'targetHandle': None, 'animated': False, 'labelShowBg': False, 'id': 'reactflow__edge-2-4', 'labelStyle': {'fill': 'black'}, 'selected': False},
    {'source': '3', 'sourceHandle': None, 'target': '4', 'targetHandle': None, 'animated': False, 'labelShowBg': False, 'id': 'reactflow__edge-3-4', 'labelStyle': {'fill': 'black'}, 'selected': False}
]

# Passo 1: Construir o grafo como um dicionário de adjacências
graph = {}

for edge in edges:
    source = edge['source']
    target = edge['target']
    if source not in graph:
        graph[source] = []
    graph[source].append(target)

# Passo 2: Função de DFS para encontrar todos os caminhos
def dfs(graph, start, end, path, all_paths):
    path.append(start)

    if start == end:
        all_paths.append(list(path))
    elif start in graph:
        for neighbor in graph[start]:
            if neighbor not in path:  # Evitar ciclos
                dfs(graph, neighbor, end, path, all_paths)
    
    path.pop()  # Voltar um passo na recursão

# Passo 3: Encontrar todos os caminhos do nó inicial ao nó final
def find_all_paths(graph, start_node, end_node):
    all_paths = []
    dfs(graph, start_node, end_node, [], all_paths)
    return all_paths

# Passo 4: Encontrar todos os caminhos entre o nó de entrada (nó '1') e os nós finais (nós sem saída)
def find_terminal_nodes(graph):
    # Encontra nós que não têm conexões de saída (terminais)
    all_sources = set(graph.keys())  # Nós que são fonte de uma conexão
    all_targets = {target for targets in graph.values() for target in targets}  # Todos os nós que são alvo de conexões
    terminal_nodes = list(all_targets - all_sources)  # Nós que só são alvo (não têm saída)
    return terminal_nodes

# Executar a busca dos caminhos possíveis começando do nó '1'
start_node = '1'
terminal_nodes = find_terminal_nodes(graph)

all_possible_branches = []
for end_node in terminal_nodes:
    paths = find_all_paths(graph, start_node, end_node)
    all_possible_branches.extend(paths)

print("Ramos possíveis:", all_possible_branches)
