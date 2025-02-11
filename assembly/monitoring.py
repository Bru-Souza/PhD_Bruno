import streamlit as st

# Dados de exemplo para tarefas de montagem
tarefas = [
    {"id": 1, "nome": "Instalar peças base", "status": False},
    {"id": 2, "nome": "Conectar cabos", "status": False},
    {"id": 3, "nome": "Fixar componentes", "status": False},
    {"id": 4, "nome": "Testar funcionamento", "status": False},
]

# Caminhos das imagens
imagem_concluida = "https://upload.wikimedia.org/wikipedia/commons/4/4d/Check_mark_icon_%28green%29.svg"  # Exemplo de imagem de concluído
imagem_pendente = "https://upload.wikimedia.org/wikipedia/commons/e/e6/Red_X.svg"  # Exemplo de imagem de pendente

# Função para atualizar o status da tarefa
def atualizar_status(id_tarefa):
    for tarefa in tarefas:
        if tarefa["id"] == id_tarefa:
            tarefa["status"] = not tarefa["status"]

# Título do app
st.title("Monitoramento de Tarefas de Montagem")

# Exibir as tarefas
st.subheader("Lista de Tarefas")
for tarefa in tarefas:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(tarefa["nome"])
    with col2:
        # Definir imagem com base no status da tarefa
        if tarefa["status"]:
            imagem = imagem_concluida
            status = "Completada"
        else:
            imagem = imagem_pendente
            status = "Pendente"
        
        # Exibir a imagem
        st.image(imagem, width=30)

        # Botão para alternar o status da tarefa
        if st.button(f"Marcar como {status} - Tarefa {tarefa['id']}", key=f"btn_{tarefa['id']}"):
            atualizar_status(tarefa["id"])

# Mostrar o progresso da montagem
total_tarefas = len(tarefas)
tarefas_completadas = sum([1 for tarefa in tarefas if tarefa["status"]])
progresso = tarefas_completadas / total_tarefas * 100

st.subheader("Progresso da Montagem")
st.progress(progresso)

st.write(f"{tarefas_completadas}/{total_tarefas} tarefas completadas")
