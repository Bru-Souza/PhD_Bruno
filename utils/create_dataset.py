import cv2
import os

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

# Criar diretório 'frames' caso não exista
output_dir = "frames"
os.makedirs(output_dir, exist_ok=True)

frame_count = 0

while True:
    # Capture o próximo frame
    ret, frame = cap.read()

    # Verifique se o frame foi capturado com sucesso
    if not ret:
        print("Falha ao capturar o frame")
        break

    # Exiba o frame
    cv2.imshow("frame", frame)

    # Captura a tecla pressionada
    key = cv2.waitKey(1) & 0xFF
    
    # Se a tecla 'q' for pressionada, saia do loop
    if key == ord('q'):
        break
    
    # Se a tecla 'x' for pressionada, salve o frame
    if key == ord('x'):
        frame_name = os.path.join(output_dir, f"frame_{frame_count}.jpeg")
        cv2.imwrite(frame_name, frame)
        print(f"Frame salvo: {frame_name}")
        frame_count += 1

# Libere o dispositivo e feche a janela
cap.release()
cv2.destroyAllWindows()