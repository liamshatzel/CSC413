#include <DHT11.h>

const int redPin = 9;
const int greenPin = 11;
const int bluePin = 10;
const int motorPin = 6;
const int dhtPin = 2;
#define DHTTYPE DHT11

String inputString = "";
bool stringComplete = false;

// LED: Pins 9, 10, 11
// Motor: 13

DHT11 dht11(dhtPin);

void setup() {
  Serial.begin(9600);
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  pinMode(motorPin, OUTPUT);

  inputString.reserve(32); // reserve memory to avoid fragmentation
}

void loop() {
  // DHT Code
  int temperature = 0;
  int humidity = 0;

  // Attempt to read the temperature and humidity values from the DHT11 sensor.
  int result = dht11.readTemperatureHumidity(temperature, humidity);

  // Check the results of the readings.
  // If the reading is successful, print the temperature and humidity values.
  // If there are errors, print the appropriate error messages.
  if (result == 0) {
    Serial.print("data: ");
    Serial.print(temperature);
    Serial.print(" ");
    Serial.print(humidity);
    Serial.println();
  }

  if (stringComplete) {
    int r = 0, g = 0, b = 0, fan = 0;
    if (sscanf(inputString.c_str(), "%d,%d,%d,%d", &r, &g, &b, &fan) == 4) {
      r = constrain(r, 0, 255);
      g = constrain(g, 0, 255);
      b = constrain(b, 0, 255);
      fan = constrain(fan, 0, 255);

      analogWrite(redPin, r);
      analogWrite(greenPin, g);
      analogWrite(bluePin, b);
      analogWrite(motorPin, fan);
    }

    inputString = "";
    stringComplete = false;
  }
}

// collect characters from serial
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }
}
