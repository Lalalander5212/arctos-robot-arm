#include <Servo.h>

Servo myServo;

void disableAllExceptServo() {
  // List of all pins to disable (everything except pin 6)
  // Arduino Mega 2560 has digital pins 0-53 + analog A0-A15

  int pinsToDisable[] = {
    // Digital pins (skip 6)
    0, 1, 2, 3, 4, 5, /*6,*/ 7, 8, 9, 10, 11, 12, 13,
    14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
    26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37,
    38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
    50, 51, 52, 53
  };

  int analogPins[] = {A0, A1, A2, A3, A4, A5, A6, A7,
                      A8, A9, A10, A11, A12, A13, A14, A15};

  // Set all digital pins as INPUT (high impedance) and write LOW
  int numDigital = sizeof(pinsToDisable) / sizeof(pinsToDisable[0]);
  for (int i = 0; i < numDigital; i++) {
    pinMode(pinsToDisable[i], INPUT);
    digitalWrite(pinsToDisable[i], LOW); // Disable internal pull-up
  }

  // Set all analog pins as INPUT (high impedance) and write LOW
  int numAnalog = sizeof(analogPins) / sizeof(analogPins[0]);
  for (int i = 0; i < numAnalog; i++) {
    pinMode(analogPins[i], INPUT);
    digitalWrite(analogPins[i], LOW);
  }

  // Explicitly disable all hardware PWM timers except Timer4 (which drives pin 6)
  // Timer0 - pins 4, 13
  TCCR0A = 0;
  TCCR0B = 0;

  // Timer1 - pins 11, 12
  TCCR1A = 0;
  TCCR1B = 0;

  // Timer2 - pins 9, 10
  TCCR2A = 0;
  TCCR2B = 0;

  // Timer3 - pins 2, 3, 5
  TCCR3A = 0;
  TCCR3B = 0;

  // Timer4 - pin 6 (KEEP THIS — used by Servo on pin 6)
  // DO NOT touch TCCR4A/TCCR4B — Servo library configures this

  // Timer5 - pins 44, 45, 46
  TCCR5A = 0;
  TCCR5B = 0;
}

void setup() {
  disableAllExceptServo();

  myServo.attach(6); // Attach servo to pin 6

  Serial.begin(9600);
  Serial.println("All pins disabled except pin 6 (Servo).");
}

void loop() {
  // Sweep servo from 0 to 180 degrees and back
  for (int pos = 0; pos <= 180; pos++) {
    myServo.write(pos);
    delay(10);
  }
  for (int pos = 180; pos >= 0; pos--) {
    myServo.write(pos);
    delay(10);
  }
}