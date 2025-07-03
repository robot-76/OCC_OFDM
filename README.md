# OCC_OFDM

# 🚀 Execution Steps

# Upload the Arduino Code
Open  "...\real time 128\tx_Arduino_8pilot.ino" in the Arduino IDE.
Select the correct board and port (e.g. Arduino Uno, COM3).
Upload the code to your Arduino.

⚠️ Note: The selected port must match the one used in the Python script.

# Run the Python Transmitter

Make sure tx_8pilot_128.py uses the same serial port as the Arduino (check in the code: serial.Serial(port=...)).
This Python file transmits messages through LED.

Run the script:
python  "...\real time 128\tx_8pilot_128.py"
Run the Python Receiver (Decoder)

Run the main decoding script:
python "...\real time 128\main_rx_add_text_window.py"

# 📌 Notes
# Ensure pyserial is installed(we used Basler camera setup as shown in the paper given below)

pip install pyserial

All serial ports must match between the Arduino and Python scripts.


## 📄 Related Paper

**Title:** Real-time implementation of OFDM modulation for an OCC system: UNet-based equalizer for signal denoising and BER optimization  
**Journal:** ICT Express(IF: 4.2), Elsevier 2025  
**DOI:** ([https://doi.org/10.1016/j.icte.2025.06.002]) 


 

