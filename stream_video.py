from flask import Flask, Response, redirect, url_for
import cv2

app = Flask(__name__)

def generate_frames():
    # Abre o vídeo
    video = cv2.VideoCapture('WIN_20240803_22_56_13_Pro.mp4')
    while True:
        success, frame = video.read()
        if not success:
            break
        else:
            # Codifica o frame em formato JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return redirect(url_for('video_feed'))

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
