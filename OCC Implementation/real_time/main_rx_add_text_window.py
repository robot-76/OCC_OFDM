import cv2
import numpy as np
from pypylon import pylon
from frame_decode import process_image  # Import the frame processing function

# Initialize Pylon camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

# Configure default resolution and frame rate
camera.Open()
camera.Width.Value = 1920  # Set image width
camera.Height.Value = 1080  # Set image height
camera.AcquisitionFrameRateEnable.SetValue(True)
frame_rate = 26.11  # Target frame rate
camera.AcquisitionFrameRate.SetValue(frame_rate)  # Set frame rate

# Set exposure time to 35 microseconds
camera.ExposureAuto.SetValue("Off")  # Turn off auto exposure to set manually
camera.ExposureTime.SetValue(35.0)  # Set exposure time in microseconds

print("Press 'q' to stop capturing frames.")

# Text settings
text_window = np.ones((480, 850, 3), dtype=np.uint8) * 255  # White background
line_height = 25  # Height of each line of text
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.6
font_thickness = 1
font_color = (0, 0, 0)  # Black text

# Variables to manage the displayed text
current_line = ""
all_lines = []  # Store all lines for scrolling

# Maximum number of lines
max_lines = text_window.shape[0] // line_height

# Start capturing video
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

while camera.IsGrabbing():
    grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    if grab_result.GrabSucceeded():
        # Access the raw image data directly
        raw_frame = grab_result.Array  # Get the raw image array in its original format

        # Pass the raw image to the `process_image` function
        rx_messages = process_image(raw_frame)

        # Add new messages to the current line
        try:
            for message in rx_messages:
                current_line += f" {message}"  # Append message with a space
                # Check if the line exceeds the window width
                text_size = cv2.getTextSize(current_line, font, font_scale, font_thickness)[0]
                if text_size[0] > text_window.shape[1] - 10:  # -10 for margin
                    all_lines.append(current_line.strip())  # Save the current line
                    current_line = ""  # Start a new line

        except Exception:
            pass

        # If there are more lines than the window can show, remove the oldest
        if len(all_lines) > max_lines - 1:
            all_lines = all_lines[-(max_lines - 1):]

        # Prepare the text window
        text_window.fill(255)  # Clear the window (white background)
        y_offset = line_height
        for line in all_lines:
            cv2.putText(text_window, line, (10, y_offset), font, font_scale, font_color, font_thickness)
            y_offset += line_height

        # Add the current (incomplete) line
        cv2.putText(text_window, current_line, (10, y_offset), font, font_scale, font_color, font_thickness)

        # Resize the raw frame before displaying
        desired_width = 850  # Example desired width
        desired_height = 480  # Example desired height
        resized_frame = cv2.resize(raw_frame, (desired_width, desired_height))

        # Display the raw video and the messages
        cv2.imshow("Captured Video (Raw)", resized_frame)
        cv2.imshow("Extracted Messages", text_window)

        # Check for key press to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break

    grab_result.Release()

# Release the camera
camera.StopGrabbing()
camera.Close()
cv2.destroyAllWindows()
