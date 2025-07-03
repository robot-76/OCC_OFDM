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

# Start capturing video
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

while camera.IsGrabbing():
    grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
    if grab_result.GrabSucceeded():
        # Access the raw image data directly
        raw_frame = grab_result.Array  # Get the raw image array in its original format

        # Pass the raw image to the `process_image` function
        rx_messages = process_image(raw_frame)

        # Prepare the text window content
        text_window = np.ones((480, 850, 3), dtype=np.uint8) * 255  # White background
        y_offset = 20  # Starting y position for text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        font_thickness = 1
        font_color = (0, 0, 0)  # Black color for text
        
        # Display the result
        try:
            for i, message in enumerate(rx_messages):
                print(f" {message}")
        except Exception:
            pass  # Ignore if there are no messages

        # Resize the raw frame before displaying (optional)
        desired_width = 850  # Example desired width
        desired_height = 480  # Example desired height
        resized_frame = cv2.resize(raw_frame, (desired_width, desired_height))

        # Optionally display the resized raw frame (visualization/debugging)
        cv2.imshow("Captured Video (Raw)", resized_frame)

        # Check for key press to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting...")
            break

    grab_result.Release()

# Release the camera
camera.StopGrabbing()
camera.Close()
cv2.destroyAllWindows()
