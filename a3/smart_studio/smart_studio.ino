#include <Servo.h>

// Pin definitions
const int LED_PIN = 13;   // Built-in LED
const int SERVO_PIN = 9;  // Servo motor pin
const int BUZZER_PIN = 8; // Buzzer pin

// Component objects
Servo myServo;

// Variables
String inputString = "";        // String to hold incoming data
boolean stringComplete = false; // Whether the string is complete
int currentServoAngle = 90;     // Current servo position

void setup() {
  // Initialize serial communication
  Serial.begin(9600);

  // Initialize pins
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  // Attach servo to pin
  myServo.attach(SERVO_PIN);
  myServo.write(currentServoAngle);

  // Initialize components to off state
  digitalWrite(LED_PIN, LOW);
  noTone(BUZZER_PIN);

  // Send ready signal
  Serial.println("Arduino ready");
}

void loop() {
  // Check for serial commands
  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
}

// Serial event handler
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();

    // Add character to input string
    inputString += inChar;

    // If newline character, mark string as complete
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}

// Process incoming commands
void processCommand(String command) {
  command.trim();        // Remove whitespace and newline
  command.toUpperCase(); // Convert to uppercase for consistency

  Serial.print("Received command: ");
  Serial.println(command);

  if (command == "LED_ON") {
    digitalWrite(LED_PIN, HIGH);
    Serial.println("LED turned ON");
  } else if (command == "LED_OFF") {
    digitalWrite(LED_PIN, LOW);
    Serial.println("LED turned OFF");
  } else if (command.startsWith("SERVO_")) {
    // Extract angle from command (e.g., "SERVO_90")
    String angleStr = command.substring(6);
    int angle = angleStr.toInt();

    if (angle >= 0 && angle <= 180) {
      currentServoAngle = angle;
      myServo.write(currentServoAngle);
      Serial.print("Servo moved to ");
      Serial.print(angle);
      Serial.println(" degrees");
    } else {
      Serial.println("Invalid servo angle (0-180)");
    }
  } else if (command == "BUZZER_ON") {
    tone(BUZZER_PIN, 1000); // 1kHz tone
    Serial.println("Buzzer turned ON");
  } else if (command == "BUZZER_OFF") {
    noTone(BUZZER_PIN);
    Serial.println("Buzzer turned OFF");
  } else if (command == "RESPONSE_RECEIVED") {
    // Optional: Add visual feedback for received responses
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    Serial.println("Response received - LED blinked");
  } else if (command == "STATUS") {
    // Report current status of all components
    Serial.print("LED: ");
    Serial.println(digitalRead(LED_PIN) ? "ON" : "OFF");
    Serial.print("Servo: ");
    Serial.print(currentServoAngle);
    Serial.println(" degrees");
    Serial.print("Buzzer: ");
    Serial.println(digitalRead(BUZZER_PIN) ? "ON" : "OFF");
  } else if (command == "RESET") {
    // Reset all components to default state
    digitalWrite(LED_PIN, LOW);
    myServo.write(90);
    noTone(BUZZER_PIN);
    currentServoAngle = 90;
    Serial.println("All components reset to default state");
  } else {
    Serial.print("Unknown command: ");
    Serial.println(command);
  }
}
