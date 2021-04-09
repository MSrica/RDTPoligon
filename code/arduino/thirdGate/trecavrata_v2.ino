#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define CE_PIN   9
#define CSN_PIN 10

#define trigPin1 2
#define echoPin1 3
#define trigPin2 4
#define echoPin2 5
long duration, distance, RightSensor,LeftSensor;
int transmitterId;

RF24 radio(CE_PIN, CSN_PIN); // Create a Radio

const uint64_t pipe = 0xE8E8F0F0E1LL;

void setup(){
  Serial.begin(9600);
  radio.begin();
  radio.setPayloadSize(2);
  radio.setPALevel(RF24_PA_HIGH);
  radio.openWritingPipe(pipe);
    
  pinMode(trigPin1, OUTPUT);
  pinMode(echoPin1, INPUT);
  pinMode(trigPin2, OUTPUT);
  pinMode(echoPin2, INPUT); 

  transmitterId = 3;
}

void loop(){
  SonarSensor(trigPin1, echoPin1);
  RightSensor = distance;
  SonarSensor(trigPin2, echoPin2);
  LeftSensor = distance;
  
  if(RightSensor <= 28 | LeftSensor <= 27){
    radio.powerUp();
    Serial.println("Poslano");
    const char ispis[32] = "1";
    radio.write(&transmitterId, 2);
  }
}

void SonarSensor(int trigPin,int echoPin){
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  distance = (duration/2) / 29.1;
}
