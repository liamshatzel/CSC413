#include <Stepper.h>
#include <LiquidCrystal.h>

// LCD setup
const int rs = 13, en = 6, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

// Stepper setup
const int stepsPerRevolution = 2048;
Stepper myStepper = Stepper(stepsPerRevolution, 8, 10, 9, 11);
const int totalZSteps = 3;
const int stepsPerZ = stepsPerRevolution / totalZSteps;
const int maxSteps = stepsPerZ * (totalZSteps - 1);

// RGB LED pins
const int RED_PIN = A1;
const int GREEN_PIN = A0;
const int BLUE_PIN = A2;
const int PEN_PIN = A3;

// Z-score data
float zScores[] = {
  0.87332895,0.889352198,0.889040602,0.716437758,0.684046019,0.763490088,1.266358935,0.778016123,2.925540184,
  3.596718377,0.773321676,0.848511543,2.356405407,0.783159973,0.897564633,0.606004514,0.265622666,0.131338468,
  -0.005618831,-0.08455527,-0.222278731,-0.2700225,-0.420249975,0.501609247,-0.785626388,-0.945745385,-0.911017748,
  -0.898645583,-0.76758894,-0.669781792,-0.861818182,-0.86860426,-0.512936986,-0.726670694,-0.671898335,-0.716769646,
  0.162739803,-0.748059921,-0.740877783,-0.929895709,-0.97667537,-0.926983675,-0.875904214,-0.544205718,-0.423217284,
  -0.453314121,-0.450461503,-0.605372827,-0.689426082,-0.662193346,-0.669850278,-0.672340088
};

const int numValues = 51;
int currentIndex = 0; // Global index
unsigned long lastPotChangeTime = 0;
int lastPotValue = -1;
bool autoMode = true;
int currentStep = 0;

int initialStep = stepsPerZ*3;

int stepsInDir = 8;
bool shouldStep = false;

//CHANGE TO PREVENT SETUP
bool setupMode = false;

void setup() {
  Serial.begin(9600);
  myStepper.setSpeed(10);
  lcd.begin(16, 2);

  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);
  pinMode(PEN_PIN, INPUT);

   if(setupMode){
    setColor(0, 255, 0);
    delay(1000);
    setColor(0, 0, 0);
    delay(1000);
    setColor(0, 255, 0);
    delay(1000);
    setColor(0, 0, 0);
    delay(1000);
    setColor(0, 255, 0);
    delay(1000);
    setColor(0, 0, 0);
    delay(1000);
    
    myStepper.step(stepsPerZ);
    delay(1000);
    myStepper.step(stepsPerZ);
    delay(1000);
    myStepper.step(stepsPerZ);
    delay(1000);

   

    for(int i = 0; i < stepsInDir; i++){
       myStepper.step(stepsPerRevolution / 10);
    }
    }
}

void loop() {
  int potValue = analogRead(PEN_PIN);
  Serial.println(potValue);
  int mappedIndex = map(potValue, 0, 1023, 0, numValues - 1);
  Serial.println(mappedIndex);


  if (autoMode) {
    currentIndex = (currentIndex + 1) % numValues;
  }

   // Detect potentiometer activity
  if (abs(potValue - lastPotValue) > 30) {
    currentIndex = mappedIndex;
    lastPotChangeTime = millis();
    lastPotValue = potValue;
    autoMode = false;
  }

  // Check for 5 seconds of inactivity
  if (!autoMode && (millis() - lastPotChangeTime > 5000)) {
    autoMode = true;
  }


  float value = zScores[currentIndex];
  int year = 1970 + currentIndex;

  // LED Stepper logic
  if (value < -0.5) {
    setColor(0, 255, 0); // Green


    if(stepsInDir <= 8){
      stepsInDir++;
      currentStep = stepsPerRevolution / 10;
      shouldStep = true;
    }

  } else if (value >= -0.5 && value <= 0.5) {
    setColor(255, 255, 0); // Yellow
    // No step
  } else {
    setColor(255, 0, 0); // Red
    if(stepsInDir >= 0){
      stepsInDir--;
      currentStep = -stepsPerRevolution / 20;
      shouldStep = true;
    }
  }


  // Display on LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Z: ");
  lcd.print(value, 2);
  lcd.setCursor(0, 1);
  lcd.print("Year: ");
  lcd.print(year);

  if(shouldStep){
      myStepper.step(currentStep);
      Serial.println("Stepping");
  }
  shouldStep = false;

  // Allow stepper to finish updating before next task
  delay(1000); // Moderate update rate
}

// Helper function to set RGB LED
void setColor(int red, int green, int blue) {
  analogWrite(RED_PIN, red);   // For common anode LEDs
  analogWrite(GREEN_PIN, green);
  analogWrite(BLUE_PIN, blue);
}