#include <Ultrasonic.h>

#define TRIGGER_PIN_1 9
#define ECHO_PIN_1 10
#define TRIGGER_PIN_2 5
#define ECHO_PIN_2 6

Ultrasonic ultrasonic_1(TRIGGER_PIN_1, ECHO_PIN_1);
Ultrasonic ultrasonic_2(TRIGGER_PIN_2, ECHO_PIN_2);

const int buttonPin = 2;
int buttonState;
int lastButtonState = LOW;
unsigned long lastDebounceTime = 0;
const long debounceDelay = 50;

bool isRunning = false;


unsigned long lastMeasureTime = 0;

unsigned long startTime = 0; // To reset time on every new run
const long interval = 200;   // 500ms interval

void setup() {
  Serial.begin(9600);
  Serial.println("--- READY ---");
  pinMode(buttonPin, INPUT_PULLUP);
}

void loop() {
  int reading = digitalRead(buttonPin);

  // --- Debouncing ---


  if (reading != lastButtonState) {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (reading != buttonState) {
      buttonState = reading;

      if (buttonState == LOW) {
        isRunning = !isRunning;
        if (isRunning) {
          startTime = millis(); // Reset timer to 0


          Serial.println("--- STARTED ---");
        } else {
          Serial.println("--- STOPPED ---");
        }
      }
    }
  }
  lastButtonState = reading;

  // --- Measurement ---
  if (isRunning) {


    if (millis() - lastMeasureTime >= interval) {

      lastMeasureTime = millis();

      // Calculate accurate relative time
      long currentTime = millis() - startTime;



      float s1 = ultrasonic_1.read();
      delay(40);

      float s2 = ultrasonic_2.read();

      // Output Format: Time_ms, Sensor1, Sensor2
      Serial.print(currentTime);
      Serial.print(",");


      Serial.print(s1);
      Serial.print(",");
      Serial.println(s2);

      Serial.print("/");

      Serial.flush();

}}}
