import cv2
import numpy as np

class AssemblyVerification:
    def __init__(self, threshold=0.5):
        self.threshold = threshold
        self.template = None
        self.sift = cv2.SIFT_create()
        self.bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)

    def set_template(self, template_image):
        self.template = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
        self.kp_template, self.des_template = self.sift.detectAndCompute(self.template, None)

    def verify(self, frame):
        if self.template is None:
            raise ValueError("Template not set.")

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        kp_frame, des_frame = self.sift.detectAndCompute(gray_frame, None)
        
        if des_frame is None or self.des_template is None:
            return False, 0, frame
        
        matches = self.bf.match(self.des_template, des_frame)
        matches = sorted(matches, key=lambda x: x.distance)
        
        match_score = len(matches) / max(len(self.kp_template), 1)
        match = match_score >= self.threshold
        
        result_frame = cv2.drawMatches(self.template, self.kp_template, frame, kp_frame, matches[:10], None, flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        
        return match, match_score, result_frame

if __name__ == "__main__":
    # Inicializa a classe de verificação
    verifier = AssemblyVerification(threshold=0.8)
    
    # Carrega o template
    template_image = cv2.imread('/home/bruno/projects/PhD_Bruno/app/lib/template_matching/templates_crop/template_04.png')
    verifier.set_template(template_image)
    
    test_frame = cv2.imread('/home/bruno/projects/PhD_Bruno/app/lib/template_matching/templates_test/template_04.png')
    verifier.set_template(template_image)
    match, probability, result_frame = verifier.verify(test_frame)
    cv2.putText(result_frame, f"Match: {match}, Prob: {probability:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if match else (0, 0, 255), 2)
    cv2.imshow("Verification", result_frame)
        
    # Pressione 'q' para sair
    if cv2.waitKey(0) & 0xFF == ord('q'):

        cv2.destroyAllWindows()
    # # Captura da câmera
    # cap = cv2.VideoCapture(6)  # 0 para webcam padrão
    
    # if not cap.isOpened():
    #     print("Erro ao acessar a câmera.")
    #     exit()
    
    # while True:
    #     ret, frame = cap.read()
    #     if not ret:
    #         break
        
    #     # Realiza a verificação
    #     match, probability, result_frame = verifier.verify(frame)
        
    #     # Exibe os resultados
    #     cv2.putText(result_frame, f"Match: {match}, Prob: {probability:.2f}", (10, 30),
    #                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if match else (0, 0, 255), 2)
    #     cv2.imshow("Verification", result_frame)
        
    #     # Pressione 'q' para sair
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break
    
    # cap.release()
    # cv2.destroyAllWindows()
