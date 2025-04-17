import cv2

class VideoManager:
    def __init__(self, source_type, source):
        """
        source_type: str, define o tipo de fonte de vídeo ("file", "youtube", "ip").
        source: str, o caminho do arquivo, link do YouTube, ou endereço IP.
        """
        self.source_type = source_type
        self.source = source
        self.cap = None

    def initialize(self):
        """Inicializa a fonte de vídeo de acordo com o tipo"""
        if self.source_type == "file":
            self.cap = cv2.VideoCapture(self.source)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        elif self.source_type == "ip":
            self.cap = cv2.VideoCapture(f"http://{self.source}/video")
        else:
            raise ValueError("Invalid video source type")

        if not self.cap.isOpened():
            raise Exception("Unable to open video source")

    def get_frame(self):
        """Captura um frame da fonte de vídeo"""
        if self.cap:
            ret, frame = self.cap.read()
            if not ret:
                return None
            return frame
        return None

    def release(self):
        """Libera o vídeo quando não for mais necessário"""
        if self.cap:
            self.cap.release()

    def __del__(self):
        self.release()
