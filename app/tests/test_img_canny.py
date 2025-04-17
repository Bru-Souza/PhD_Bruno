import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

def preprocess(image_path, save_name):
    """Lê e pré-processa a imagem: escala de cinza + blur + bordas (Canny)."""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blur, 25, 0)

    # Salvar imagem pré-processada
    save_path = f'preprocess_{save_name}.png'
    cv2.imwrite(save_path, edges)
    print(f"[SALVO] Imagem de bordas salva como {save_path}")

    # Visualizar imagem de bordas
    plt.figure()
    plt.imshow(edges, cmap='gray')
    plt.title(f"Bordas: {save_name}")
    plt.axis('off')
    plt.show()

    return img, edges

def draw_match(img_rgb, top_left, template_shape, color=(0, 255, 0), thickness=2):
    """Desenha um retângulo na imagem onde o template foi encontrado."""
    h, w = template_shape
    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv2.rectangle(img_rgb, top_left, bottom_right, color, thickness)

# Caminhos das imagens
imagem_base_path = '/home/bruno/projects/PhD_Bruno/app/lib/template_matching/Inference_screenshot_15.04.2025.png'
template_path = '/home/bruno/projects/PhD_Bruno/app/data/templates_crop/template_01.png'

# Pré-processamento + visualização + salvamento
img_rgb, img_edges = preprocess(imagem_base_path, "imagem_base")
template_rgb, template_edges = preprocess(template_path, "template")

# Template matching nas bordas
result = cv2.matchTemplate(img_edges, template_edges, cv2.TM_CCOEFF_NORMED)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

# Mostrando resultados
print(f"Melhor correspondência encontrada em: {max_loc} com score {max_val:.3f}")

# Desenhar retângulo de correspondência
draw_match(img_rgb, max_loc, template_edges.shape)

# Exibir resultado final
plt.figure(figsize=(10, 5))
plt.imshow(cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB))
plt.title("Resultado do Template Matching")
plt.axis("off")
plt.show()

# Salvar imagem final com bounding box
cv2.imwrite("resultado_matching.png", img_rgb)
print("[SALVO] Resultado final salvo como resultado_matching.png")
