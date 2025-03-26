import cv2

class AssemblyVerification:
    def __init__(self, method=cv2.TM_CCOEFF_NORMED, threshold=0.5):
        """
        Initialize the AssemblyVerification class.

        :param method: Matching method for cv2.matchTemplate.
        :param threshold: Threshold for detection.
        """
        self.method = method
        self.threshold = threshold
        self.template = None
        self.template_shape = None

    def set_template(self, template_frame):
        """
        Set or update the template frame for verification.

        :param template_frame: Frame to be used as the template.
        """
        if template_frame is None:
            raise ValueError("Template frame cannot be None.")
        
        self.template = cv2.cvtColor(template_frame, cv2.COLOR_BGR2GRAY)
        self.template_shape = self.template.shape[::-1]

    def verify(self, frame):
        """
        Verify the given frame against the stored template.

        :param frame: Frame to be compared with the template.
        :return: Tuple containing (is_match, max_probability, annotated_frame).
        """
        if self.template is None:
            raise ValueError("Template is not set. Use set_template() to define a template.")

        # Convert the frame to grayscale
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Perform template matching
        res = cv2.matchTemplate(frame_gray, self.template, self.method)

        # Find matches above the threshold
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # Check if the match exceeds the threshold
        is_match = max_val >= self.threshold

        # Annotate the frame if a match is found
        annotated_frame = frame.copy()
        if is_match:
            top_left = max_loc
            bottom_right = (top_left[0] + self.template_shape[0], top_left[1] + self.template_shape[1])
            cv2.rectangle(annotated_frame, top_left, bottom_right, (0, 0, 255), 4)

        return is_match, max_val, annotated_frame

# if __name__ == "__main__":
#     # Inicializa a classe de verificação
#     verifier = AssemblyVerification(threshold=0.5)
    
#     # Carrega o template
#     template_image = cv2.imread('templates_crop/template_02.png')
#     verifier.set_template(template_image)
    
#     # Captura da câmera
#     cap = cv2.VideoCapture(6)  # 0 para webcam padrão
    
#     if not cap.isOpened():
#         print("Erro ao acessar a câmera.")
#         exit()
    
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
        
#         # Realiza a verificação
#         match, probability, result_frame = verifier.verify(frame)
        
#         # Exibe os resultados
#         cv2.putText(result_frame, f"Match: {match}, Prob: {probability:.2f}", (10, 30),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if match else (0, 0, 255), 2)
#         cv2.imshow("Verification", result_frame)
        
#         # Pressione 'q' para sair
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
    
#     cap.release()
#     cv2.destroyAllWindows()
# Example usage
if __name__ == "__main__":
    # Initialize the verification class
    verifier = AssemblyVerification(threshold=0.5)

    # Load the template and the test frame
    template_image = cv2.imread('/home/bruno/projects/PhD_Bruno/app/lib/template_matching/template.jpeg')
    # test_frame = cv2.imread('templates_test/template_11.png')
    test_frame = cv2.imread('testx.png')
    

    # Set the template
    verifier.set_template(template_image)

    # Perform verification
    match, probability, result_frame = verifier.verify(test_frame)

    # Output results
    print(f"Match: {match}, Probability: {probability}")
    cv2.imwrite('result_with_bbox.png', result_frame)