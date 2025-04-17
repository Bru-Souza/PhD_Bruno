import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Carregar os resultados
df = pd.read_csv("outputs/results/template_matching_scores_x.csv")

# Criar a matriz (pivot table)
heatmap_data = df.pivot(index='template', columns='test_image', values='score')

# Plotar o heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="viridis", cbar_kws={'label': 'Score'})
plt.title("Template Matching - Score Heatmap")
plt.xlabel("Imagem de Teste")
plt.ylabel("Template")
plt.tight_layout()
plt.show()
