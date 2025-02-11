import cv2

# URL do stream de vídeo
stream_url = 'http://127.0.0.1:5000/video_feed'

# Abre o stream de vídeo
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    print("Erro ao abrir o stream de vídeo")
    exit()

while True:
    # Captura frame a frame
    ret, frame = cap.read()
    if not ret:
        print("Erro ao capturar frame")
        break

    # Exibe o frame resultante
    cv2.imshow('Video Stream', frame)

    # Pressione 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera o objeto de captura de vídeo
cap.release()
cv2.destroyAllWindows()
