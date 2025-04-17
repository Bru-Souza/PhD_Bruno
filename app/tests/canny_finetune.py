import cv2

def nothing(x):
    pass

# Carrega a imagem
image_path = '/home/bruno/projects/PhD_Bruno/app/lib/template_matching/test_03.png'  # Troque pelo caminho da sua imagem
img = cv2.imread(image_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (3, 3), 0)

# Cria janela e trackbars
cv2.namedWindow('Canny Preview')
cv2.createTrackbar('Min Threshold', 'Canny Preview', 25, 255, nothing)
cv2.createTrackbar('Max Threshold', 'Canny Preview', 0, 255, nothing)

print("[INFO] Ajuste os valores com os sliders e pressione ESC para sair e salvar a imagem.")

while True:
    # Lê valores dos trackbars
    min_val = cv2.getTrackbarPos('Min Threshold', 'Canny Preview')
    max_val = cv2.getTrackbarPos('Max Threshold', 'Canny Preview')

    # Aplica Canny
    edges = cv2.Canny(blur, min_val, max_val)

    # Mostra resultado
    cv2.imshow('Canny Preview', edges)

    # Tecla ESC para sair e salvar
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        break

# Salva imagem final
cv2.imwrite("canny_ajustada.png", edges)
print("[SALVO] Imagem de bordas ajustada salva como canny_ajustada.png")

cv2.destroyAllWindows()
