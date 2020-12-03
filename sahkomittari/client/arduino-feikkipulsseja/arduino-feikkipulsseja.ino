/*
 feikkimittari

 antaa pulsseja pinniin DPIN
 yhdistä mittari-arduinon ja tän arduinon pinnit D2-DPIN ja GND-GDN
*/

#define DPIN 2
void setup() {
 
  pinMode(DPIN, OUTPUT);
}

// the loop function runs over and over again forever
void loop() {
  digitalWrite(DPIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(60);                       // wait for a second
  digitalWrite(DPIN, LOW);    // turn the LED off by making the voltage LOW
  delay(240);                       // wait for a second
}
