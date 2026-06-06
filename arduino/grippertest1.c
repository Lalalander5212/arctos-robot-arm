/*
 * Gripper Servo Test
 *
 * This sketch tests the gripper servo independently.
 * During early testing, some axis motors were unintentionally active,
 * so related motor/control pins were set LOW to keep them disabled.
 */

 #include <Servo.h>

Servo myServo;

void setup() {
    // Pins used to keep other motor drivers inactive during gripper-only testing
    int offPins[] = {26, 28, 34, 36, 46, 48, 49, 51};

    pinMode(A0, INPUT);
    digitalWrite(A0, LOW);
    pinMode(A1, INPUT);
    digitalWrite(A1, LOW);
    pinMode(A6, INPUT);
    digitalWrite(A6, LOW);
    pinMode(A7, INPUT);
    digitalWrite(A7, LOW);

    for (int i = 0; i < 8; i++) {
        pinMode(offPins[i], OUTPUT);
        digitalWrite(offPins[i], LOW);
    }

    myServo.attach(6);

    myServo.write(0);
    delay(2000);
    // myServo.write(45);
    // delay(1000);
    // myServo.write(90);
    // delay(1000);
    // myServo.write(100);
    // delay(1000);
    // myServo.write(110);
    // delay(1000);
    // myServo.write(120);
    // delay(1000);
    // myServo.write(130);
    // delay(1000);
    // myServo.write(140);
    // delay(1000);
    // myServo.write(150);
    // delay(1000);

}

void loop() {
    // do nothing
}