'''
Lib functions

'''

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
    # Encontra nós que não têm conexões de saída (terminais)
    all_sources = set(graph.keys())  # Nós que são fonte de uma conexão
    all_targets = {target for targets in graph.values() for target in targets}  # Todos os nós que são alvo de conexões
    terminal_nodes = list(all_targets - all_sources)  # Nós que só são alvo (não têm saída)
    return terminal_nodes