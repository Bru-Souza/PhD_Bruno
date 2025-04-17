import cv2

# Indica o dispositivo de vídeo que você deseja acessar
video_device = 6

# Tente abrir o dispositivo de vídeo
cap = cv2.VideoCapture(video_device)

# Verifique se o dispositivo foi aberto com sucesso
if not cap.isOpened():
    print(f"Erro ao abrir o dispositivo {video_device}")
    exit()

# Define a resolução da câmera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Largura (1280p)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Altura (720p)

# Define a taxa de quadros (30 fps)
fps = 30

# Defina o codec e crie o objeto VideoWriter
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec para compressão de vídeo
output_file = 'video_gravado_lab.avi'  # O arquivo de saída (no formato .avi)
out = cv2.VideoWriter(output_file, fourcc, fps, (1280, 720))

while True:
    # Capture o próximo frame
    ret, frame = cap.read()

    # Verifique se o frame foi capturado com sucesso
    if not ret:
        print("Falha ao capturar o frame")
        break

    # Grava o frame no arquivo
    out.write(frame)

    # Exiba o frame
    cv2.imshow("frame", frame)

    # Espera por uma tecla para sair (pressione 'q' para sair)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libere os dispositivos e feche as janelas
cap.release()
out.release()
cv2.destroyAllWindows()
