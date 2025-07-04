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

# Figure
![Figure 1: System Architecture](/OCC_Implementation/figure/OCC_architecture.png)
![Figure 2: OCC Implementation setup](/OCC_Implementation/figure/OCC_Implementation_setup.JPG)
![Figure 3: Advantages of Zerro padding](/OCC_Implementation/figure/Zero-padding_avdvantages.png)
![Figure 4: Visualization of the OCC data decoding](/OCC_Implementation/figure/Visualization_OCC_data_decoding.png)


## 📄 Related Paper

**Title:**
Real-time implementation of OFDM modulation for an OCC system: UNet-based equalizer for signal denoising and BER optimization  

**Journal:** 
ICT Express(IF: 4.2), Elsevier 2025  

**DOI:** 
[https://doi.org/10.1016/j.icte.2025.06.002](https://doi.org/10.1016/j.icte.2025.06.002)


### 📚 Cite This Paper (BibTeX)

```bibtex
@article{rahman2025real,
  title={Real-time implementation of OFDM modulation for an OCC system: UNet-based equalizer for signal denoising and BER optimization},
  author={Rahman, Md Minhazur and Nazim, Md Shahriar and Joha, Md Ibne and Jang, Yeong Min},
  journal={ICT Express},
  year={2025},
  publisher={Elsevier}
}
```






 

