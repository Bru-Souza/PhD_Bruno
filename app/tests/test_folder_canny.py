import cv2
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def preprocess(image_path, save_name, output_dir="outputs/preprocessed"):
    """Pré-processa imagem (Canny) e salva a imagem de bordas."""
    os.makedirs(output_dir, exist_ok=True)
    
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blur, 25, 0)

    save_path = os.path.join(output_dir, f'{save_name}.png')
    cv2.imwrite(save_path, edges)
    return img, edges

def draw_match(img_rgb, top_left, template_shape, color=(0, 255, 0), thickness=2):
    """Desenha bounding box."""
    h, w = template_shape
    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv2.rectangle(img_rgb, top_left, bottom_right, color, thickness)

# Diretórios
template_dir = '/home/bruno/projects/PhD_Bruno/app/lib/template_matching/test_template/video_frames_crop'
test_dir = '/home/bruno/projects/PhD_Bruno/app/lib/template_matching/test_template/video_frames'
output_dir = 'outputs/results'
os.makedirs(output_dir, exist_ok=True)

# Quantidade de templates
n_templates = 18

# Tabela para armazenar os scores
results = []

# Loop incremental
for template_idx in range(0, n_templates + 1):
    template_name = f"frame_{template_idx:02d}.jpg"
    template_path = os.path.join(template_dir, template_name)
    
    # Pré-processar o template
    template_rgb, template_edges = preprocess(template_path, f"template_{template_idx:02d}_edges")
    
    for test_idx in range(0, template_idx + 1):
        test_name = f"frame_{test_idx:02d}.jpg"
        test_path = os.path.join(test_dir, test_name)

        # Pré-processar a imagem de teste
        test_rgb, test_edges = preprocess(test_path, f"test_{test_idx:02d}_edges")

        # Matching
        result = cv2.matchTemplate(test_edges, template_edges, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # Salvar resultado com bounding box
        matched_img = test_rgb.copy()
        draw_match(matched_img, max_loc, template_edges.shape)
        result_name = f"result_template_{template_idx:02d}_test_{test_idx:02d}.png"
        cv2.imwrite(os.path.join(output_dir, result_name), matched_img)

        # Salvar resultado na tabela
        results.append({
            "template": f"template_{template_idx:02d}",
            "test_image": f"template_{test_idx:02d}",
            "score": max_val
        })

        print(f"[MATCH] Template {template_idx:02d} vs Teste {test_idx:02d} → Score: {max_val:.3f}")

# Criar DataFrame e salvar CSV
df = pd.DataFrame(results)
df.to_csv(os.path.join(output_dir, "template_matching_scores_x.csv"), index=False)
print("[SALVO] Resultados salvos em outputs/results/template_matching_scores_x.csv")
