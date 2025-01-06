"""
Script com objetivo principal de gerenciar o fluxo de imagens - Streaming

Author: Bruno J. Souza

"""

# Import libs
import os
import cv2
import numpy as np
import pyrealsense2 as rs

output_dir = 'dataset/'

def capture_video():
    # Create a VideoWriter object to save the video
    idx = 1
    while os.path.exists(os.path.join(output_dir, f"video_{idx}.avi")):
        idx += 1
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(os.path.join(output_dir, f"video_{idx}.avi"), fourcc, 30, (1280, 720))

    # Capture and save frames for 5 seconds
    start_time = cv2.getTickCount()
    while (cv2.getTickCount() - start_time) / cv2.getTickFrequency() < 80:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()

        if not color_frame:
            print("No RGB image received")
            continue

        color_image = np.asanyarray(color_frame.get_data())

        # Write the frame to the video file
        out.write(color_image)

        # Display the frame
        cv2.imshow('RealSense', color_image)
        key = cv2.waitKey(1)

        # Press esc or 'q' to stop capturing
        if key & 0xFF == ord('q') or key == 27:
            break

    out.release()


# Configure depth and color streams
config   = rs.config()
pipeline = rs.pipeline()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)

device = pipeline_profile.get_device()

found_rgb = False
found_rgb = any(sensor.get_info(rs.camera_info.name) == 'RGB Camera' for sensor in device.sensors)

if not found_rgb:
    print("Could not find camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

# Start streaming
pipeline.start(config)

idx = 0

try:
    while True:

        # Wait for a coherent color frame
        frames      = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()

        if not color_frame:
            print("No RGB image received")
            continue

        # Convert image to numpy array
        color_image        = np.asanyarray(color_frame.get_data())
        color_colormap_dim = color_image.shape

        # Show frames
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', color_image)
        key = cv2.waitKey(1)

        # Press esc or 'q' to close the image window
        if key & 0xFF == ord('q') or key == 27:
            cv2.destroyAllWindows()
            break
        
        # Save 5s video
        if key & 0xFF == ord('x') or key == 27:
            #capture_video()
            idx = idx +1
            frame_name = "output/frame_" + str(idx) + ".jpg"
            cv2.imwrite(frame_name, color_image)

finally:

    # Stop streaming
    pipeline.stop()