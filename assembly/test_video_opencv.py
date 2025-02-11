import cv2

# Indica o dispositivo de vídeo que você deseja acessar
video_device = 6

# Tente abrir o dispositivo de vídeo
cap = cv2.VideoCapture(video_device)

# Verifique se o dispositivo foi aberto com sucesso
if not cap.isOpened():
    print(f"Erro ao abrir o dispositivo {video_device}")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)  # Largura (1080p)

cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Altura (720p)

while True:
    # Capture o próximo frame
    ret, frame = cap.read()

    # Verifique se o frame foi capturado com sucesso
    if not ret:
        print("Falha ao capturar o frame")
        break

    # Exiba o frame
    cv2.imshow("frame", frame)

    # Espera por uma tecla para sair (pressione 'q' para sair)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libere o dispositivo e feche a janela
cap.release()
cv2.destroyAllWindows()
