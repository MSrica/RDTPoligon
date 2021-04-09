#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define CE_PIN   9
#define CSN_PIN 10
#define trigPin1 2
#define echoPin1 3

long duration, distance, sensor;
int senderId;
RF24 radio(CE_PIN, CSN_PIN); // Create a Radio

const uint64_t pipe = 0xE8E8F0F0E1LL; //postavljamo sve kanale s kojih ce RF24 reciever citat
bool krenuo = 0; // varijabla koja provjera ako se digo sa zadanog postolja ( dron treba postavit tako da mu jedan od propelera bude ispred senzora)
int connected = 0;

void setup() {
  Serial.begin(9600);
  radio.begin();
  radio.setPayloadSize(2);
  radio.openReadingPipe(1, pipe);
  radio.setPALevel(RF24_PA_HIGH);
  radio.startListening();

  pinMode(trigPin1, OUTPUT);
  pinMode(echoPin1, INPUT);
}

void loop(void) {
  if(connected == 0){
    connected = 1;
    Serial.println("connected");  
  }
  if (krenuo == 0) { // provjra ukoliko se dron dignuo sa pocetne platforme ukoliko je salje "Start\n0"
    SonarSensor(trigPin1, echoPin1);
    sensor = distance;
    while (sensor > 10){
      SonarSensor(trigPin1, echoPin1);
      sensor = distance;
    }
    while (sensor < 10){
      SonarSensor(trigPin1, echoPin1);
      sensor = distance;
    }
    SonarSensor(trigPin1, echoPin1);
    sensor = distance;
    if(krenuo == 0 && sensor > 10){
      krenuo = 1;
      Serial.println(0);
    }
  } else if (krenuo == 1) {
    if (radio.available()) {
      bool done = false;
      radio.read(&senderId, 2);
      Serial.println(senderId);
      delay(100);
    }
  }
}

void SonarSensor(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  distance = (duration / 2) / 29.1;
}
