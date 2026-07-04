#include <Wire.h>
#include <MPU6050_tockn.h>

#define SDA_PIN 21
#define SCL_PIN 22

MPU6050 mpu(Wire);

unsigned long previousTime = 0;

float roll = 0;
float pitch = 0;
float yaw = 0;

void setup()
{
    Serial.begin(115200);

    Wire.begin(SDA_PIN, SCL_PIN);

    mpu.begin();

    Serial.println("Calibration...");
    mpu.calcGyroOffsets(true);
    Serial.println("OK");

    previousTime = micros();

    Serial.println("AX,AY,AZ,GX,GY,GZ,TEMP,ROLL,PITCH,YAW");
}

void loop()
{
    mpu.update();

    unsigned long now = micros();
    float dt = (now - previousTime) / 1000000.0f;
    previousTime = now;

    float accX = mpu.getAccX();
    float accY = mpu.getAccY();
    float accZ = mpu.getAccZ();

    float gyroX = mpu.getGyroX();
    float gyroY = mpu.getGyroY();
    float gyroZ = mpu.getGyroZ();

    float temp = mpu.getTemp();

    float accRoll =
        atan2(accY, accZ) * 180.0 / PI;

    float accPitch =
        atan2(-accX,
              sqrt(accY * accY + accZ * accZ))
        * 180.0 / PI;

    roll =
        0.98f * (roll + gyroX * dt)
        + 0.02f * accRoll;

    pitch =
        0.98f * (pitch + gyroY * dt)
        + 0.02f * accPitch;

    yaw += gyroZ * dt;

    Serial.print(accX, 4);
    Serial.print(",");

    Serial.print(accY, 4);
    Serial.print(",");

    Serial.print(accZ, 4);
    Serial.print(",");

    Serial.print(gyroX, 3);
    Serial.print(",");

    Serial.print(gyroY, 3);
    Serial.print(",");

    Serial.print(gyroZ, 3);
    Serial.print(",");

    Serial.print(temp, 2);
    Serial.print(",");

    Serial.print(roll, 2);
    Serial.print(",");

    Serial.print(pitch, 2);
    Serial.print(",");

    Serial.println(yaw, 2);

    delay(10);
}
