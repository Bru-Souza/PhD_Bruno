import cv2

# Captura do vídeo (0 = webcam, ou passe um caminho para vídeo)
cap = cv2.VideoCapture(0)

# Nome da janela
window_name = "Frame Projetado"

# Criar a janela como NORMAL para evitar problemas de exibição
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

# Mover a janela para o projetor (HDMI-2)
cv2.moveWindow(window_name, 1920, 0)

# Ajustar o tamanho manualmente
cv2.resizeWindow(window_name, 1920, 1079)

# Garantir que a janela está em tela cheia no projetor
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Exibir o frame no projetor
    cv2.imshow(window_name, frame)

    # Pressione 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


