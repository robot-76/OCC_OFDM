import cv2
import numpy as np
from pypylon import pylon
from frame_decode import process_image  # Import the frame processing function

# Function to render the QAM constellation in a new OpenCV window
def plot_qam_constellation(qam_data):
    """Plot QAM constellation on a blank OpenCV image."""
    if qam_data is None or len(qam_data) == 0:
        return
    
    # blank image for the QAM plot
    qam_window = np.ones((480, 480, 3), dtype=np.uint8) * 255  # White background
    
    # Normalize the QAM data for display
    max_value = max(np.abs(qam_data.real).max(), np.abs(qam_data.imag).max())
    normalized_qam = qam_data / max_value * (qam_window.shape[0] // 2 - 20)
    center_x, center_y = qam_window.shape[1] // 2, qam_window.shape[0] // 2

    # Draw QAM points
    for symbol in normalized_qam:
        x = int(center_x + symbol.real)
        y = int(center_y - symbol.imag)
        cv2.circle(qam_window, (x, y), 5, (0, 0, 255), -1)  # Red circles
    
    cv2.line(qam_window, (center_x, 0), (center_x, qam_window.shape[0]), (0, 0, 0), 1)  # Vertical axis
    cv2.line(qam_window, (0, center_y), (qam_window.shape[1], center_y), (0, 0, 0), 1)  # Horizontal axis
    
    cv2.putText(qam_window, "In-phase (Real)", (10, qam_window.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    cv2.putText(qam_window, "Quadrature (Imag)", (qam_window.shape[1] - 150, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    cv2.imshow("Without AI QAM Constellation Diagram", qam_window)

# Initialize Pylon camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

# Configure default resolution and frame rate
camera.Open()
camera.Width.Value = 1920  # Set image width
camera.Height.Value = 1080  # Set image height
camera.AcquisitionFrameRateEnable.SetValue(True)
frame_rate = 26.11  # Target frame rate
camera.AcquisitionFrameRate.SetValue(frame_rate)  # Set frame rate

# Set Gamma
# camera.GammaEnable.SetValue(True)  # Enable Gamma
# camera.Gamma.SetValue(1.13792)  # Adjust Gamma value (Default is usually 1.0)

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
        rx_messages,qamc = process_image(raw_frame)

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

        try:
            # If QAM constellation data exists, plot it in a new window
            if qamc is not None and len(qamc) > 0:
                plot_qam_constellation(qamc)

        except Exception:
            pass

        # Check for key press to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break

    grab_result.Release()

# Release the camera
camera.StopGrabbing()
camera.Close()
cv2.destroyAllWindows()
