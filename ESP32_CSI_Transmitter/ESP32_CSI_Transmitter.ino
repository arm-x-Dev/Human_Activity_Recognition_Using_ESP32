#include "WiFi.h"

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Initializing CSI Transmitter...");

  // Set Wi-Fi to Access Point mode
  WiFi.mode(WIFI_AP);
  
  // Configure an open AP named "ESP32_CSI_Beacon" on Channel 1
  // We lock it to Channel 1 so the receiver always knows where to listen
  WiFi.softAP("ESP32_CSI_Beacon", "", 1, 0, 4); 

  Serial.println("Transmitter active. Broadcasting on Channel 1.");
}

void loop() {
  // The ESP32 hardware natively broadcasts beacon packets automatically 
  // every ~100ms in AP mode. We can leave loop empty or print a heartbeat.
  Serial.println("Broadcasting beacon frame...");
  delay(2000);
}