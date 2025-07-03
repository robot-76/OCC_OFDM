#include <SoftwareSerial.h>

#define LED_PIN 9  // PWM output pin

String receivedData = "";
bool dataComplete = false;
int values[150]; // Array to store received values
int valueCount = 0;
bool newDataReceived = false;  // Flag to indicate new data has been received

void setup() {
    Serial.begin(9600);  // Serial communication with Python
    pinMode(LED_PIN, OUTPUT);

    // Set Timer 1 to 16kHz for PWM frequency adjustment
    TCCR1B = (TCCR1B & 0b11111000) | 0x01;
}

void loop() {
    // Check for incoming data from Python
    while (Serial.available()) {
        char c = Serial.read();
        if (c == '\n') {  // End of transmission
            dataComplete = true;
            break;
        }
        receivedData += c;
    }

    // Process received data
    if (dataComplete) {
        Serial.println("Data Received: " + receivedData);
        valueCount = 0;  // Reset count

        // Convert received string to integer array
        char *ptr = strtok((char *)receivedData.c_str(), ", ");
        while (ptr != NULL && valueCount < 150) {
            values[valueCount++] = atoi(ptr);
            ptr = strtok(NULL, ", ");
        }

        receivedData = "";  // Clear received data buffer
        dataComplete = false;
        newDataReceived = true; // Mark new data as available
    }

    // If data is available, keep transmitting it continuously
    if (newDataReceived) {
        for (int i = 0; i < valueCount; i++) {
            analogWrite(LED_PIN, values[i]); // Write PWM value
            delayMicroseconds(70); // Small delay

            // Turn off LED briefly
            analogWrite(LED_PIN, 0);
            delayMicroseconds(35);
        }

        // Ensure LED is off between loops
        analogWrite(LED_PIN, 0);
        delayMicroseconds(500);
    }
}
