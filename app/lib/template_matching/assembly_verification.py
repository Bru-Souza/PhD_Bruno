"""
Example usage

# Initialize the verification class
verifier = AssemblyVerification(threshold=0.5)

# Load the template and the test frame
template_image = cv2.imread('template.png')
test_frame = cv2.imread('test.png')

# Set the template
verifier.set_template(template_image)

# Perform verification
match, probability, result_frame = verifier.verify(test_frame)

# Output results
print(f"Match: {match}, Probability: {probability}")
cv2.imwrite('result_with_bbox.png', result_frame)

"""

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
        self.region_points = None
    
    def preprocess(self, img):
        """
        Preprocess img: grayscale + blur + edges (Canny).
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        edges = cv2.Canny(blur, 25, 0)
        return edges

    
    def set_region_points(self, roi):
        """
        Set the region points to perform template matching
        """
        self.region_points = roi

    
    def set_template(self, template_frame):
        """
        Set or update the template frame for verification.

        :param template_frame: Frame to be used as the template.
        """
        if template_frame is None:
            raise ValueError("Template frame cannot be None.")
        
        self.template = self.preprocess(template_frame)
        self.template_shape = self.template.shape[::-1]

    
    def verify(self, frame):
        """
        Verify the given frame against the stored template.

        :param frame: Frame to be compared with the template.
        :return: Tuple containing (is_match, max_probability, annotated_frame).
        """
        if self.template is None:
            raise ValueError("Template is not set. Use set_template() to define a template.")

        # Converte pontos em bounding box
        x1 = int(self.region_points[0][0])
        y1 = int(self.region_points[0][1])
        x2 = int(self.region_points[2][0])
        y2 = int(self.region_points[2][1])

        frame = frame[y1:y2, x1:x2]  # Crop da região de interesse
        
        # Preprocess frame
        actual_frame = self.preprocess(frame)

        # Perform template matching
        res = cv2.matchTemplate(actual_frame, self.template, self.method)

        # Find matches above the threshold
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # Check if the match exceeds the threshold
        is_match = max_val >= self.threshold

        # Annotate the frame if a match is found
        annotated_frame = frame.copy()
        if is_match:
            top_left = max_loc
            bottom_right = (top_left[0] + self.template_shape[0], top_left[1] + self.template_shape[1])
            cv2.rectangle(annotated_frame, top_left, bottom_right, (0, 0, 255), 2)

        return is_match, max_val, annotated_frame

