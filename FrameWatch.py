import cv2
import os
from datetime import datetime, timedelta
import time

# Set the path to save the recorded videos
current_directory = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(current_directory, "CCTV_recordings")
os.makedirs(save_path, exist_ok=True)

# Maximum disk space to be used (in bytes)
max_disk_space = 50 * 1024 * 1024 * 1024  # 50GB

# Duration of each video file (in seconds)
video_duration = 24 * 60 * 60  # 24 hours

# Font properties for the timestamp
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
font_color = (0, 0, 255)  # Red color (BGR format)
font_thickness = 2

# Frame skipping parameters
# Capture and save every nth frame (e.g., 1 for every frame, 2 for every other frame, etc.)
frame_skip_interval = 3
frame_counter = 0

# Initializing variables
current_disk_space = 0
current_video_duration = 0
video_start_time = datetime.now()

# Capturing video from the default camera
cap = cv2.VideoCapture(0)

# Initialize video writer
video_writer = None

while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    # Increment frame counter
    frame_counter += 1

    # Check if the frame should be captured and saved
    if frame_counter % frame_skip_interval == 0:
        # Add timestamp to the frame
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, 30), font,
                    font_scale, font_color, font_thickness)

        # Display the frame
        cv2.imshow("CCTV", frame)

        # Calculate the disk space used by the recordings
        current_disk_space = sum(os.path.getsize(os.path.join(save_path, f)) for f in os.listdir(
            save_path) if os.path.isfile(os.path.join(save_path, f)))

        # Calculate the video duration
        current_video_duration = (
            datetime.now() - video_start_time).total_seconds()

        # Check if the disk space limit has been reached
        if current_disk_space > max_disk_space:
            # Get the oldest video file
            oldest_file = min(os.listdir(save_path), key=lambda f: os.path.getctime(
                os.path.join(save_path, f)))
            oldest_file_path = os.path.join(save_path, oldest_file)

            # Delete the oldest video file
            os.remove(oldest_file_path)

        # Create a new video writer if needed
        if video_writer is None or current_video_duration >= video_duration:
            # Release the current video writer if it exists
            if video_writer is not None:
                video_writer.release()

            # Reset video start time
            video_start_time = datetime.now()

            # Create a new video file
            video_filename = datetime.now().strftime("%Y.%m.%d__%H%M%S") + ".avi"
            video_filepath = os.path.join(save_path, video_filename)
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            video_writer = cv2.VideoWriter(
                video_filepath, fourcc, 24, (640, 480))  # third param is fps

        # Save the frame as a video file
        video_writer.write(frame)

        # Check if the video duration limit has been reached
        if current_video_duration >= video_duration:
            # Release the current video writer
            video_writer.release()
            video_writer = None

    # Check for the 'q' key to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video writer, capture, and close any open windows
if video_writer is not None:
    video_writer.release()
cap.release()
cv2.destroyAllWindows()
