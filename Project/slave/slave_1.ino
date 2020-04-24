// CONSTANTS
#define AUTO 20010
#define MANUAL_ON 20011
#define MANUAL_OFF 20012
#define VALVE 11
#define TRANSCEIVE 7
#define MOISTURE A0

// Variables
unsigned long moisture = 0;
unsigned long now = 0;
unsigned long percent = 0;
int receive = 0;
int current = 0;

void setup() {
  // put your setup code here, to run once:
  pinMode(TRANSCEIVE, OUTPUT);
  pinMode(MOISTURE, INPUT);
  pinMode(VALVE, OUTPUT);
  Serial.begin(9600);
  digitalWrite(TRANSCEIVE, LOW);
  digitalWrite(VALVE, LOW);
}

unsigned long percentRH(unsigned long val){
  Serial.print("val: ");
  Serial.println(val);
  unsigned long temp = (val*100)/1023;
  temp = 100-temp;
  return temp+10;
}

void autoValve(unsigned long percent){
  if(percent<50){
    digitalWrite(VALVE, HIGH);
  }
  else if(percent>=65){
    digitalWrite(VALVE, LOW);
  }
//    digitalWrite(VALVE, HIGH);  
}

void sendToMaster(){
   while(receive!=9){
//      moisture = analogRead(MOISTURE);
//      percent = percentRH(moisture);
//      autoValve(percent);
      //Serial.end();
      //Serial.begin(9600);
      digitalWrite(7, HIGH);
      now = millis();
      while(millis()-now<1000){
        Serial.print("1,");
        Serial.print(percent);
        Serial.println(",2");
      }
      digitalWrite(7, LOW);
      receive = Serial.parseInt();
      if(receive>20000 and receive!=current){
//        current = receive;
        return;
      }
      now = millis();
      while(millis()-now<1000)
        Serial.println(receive);
    }
    receive = 0;
    now = millis();
    while(millis()-now<1000)
    Serial.println("Hello");
}

void testValve(){
  while(true){
    digitalWrite(VALVE, HIGH);
    delay(1000);
    digitalWrite(VALVE, LOW);
    delay(1000);  
//      moisture = analogRead(MOISTURE);
//      Serial.println(percentRH(moisture));
  }  
}

void loop() {
  // put your main code here, to run repeatedly:
//  testValve();
//  digitalWrite(VALVE, HIGH);
  Serial.end();
  Serial.begin(9600);
  digitalWrite(7, LOW);
  receive = Serial.parseInt();
  Serial.println(receive);
  if(receive==AUTO){
      current = AUTO;
      moisture = analogRead(MOISTURE);
      percent = percentRH(moisture);
      autoValve(percent);
      sendToMaster();
//      autoValve(percent);  
  }
  
  else if(receive==MANUAL_ON){
      current = MANUAL_ON;
      moisture = analogRead(A0);
      percent = percentRH(moisture);
      digitalWrite(VALVE, HIGH);
      sendToMaster();
  }

  else if(receive==MANUAL_OFF){
      current = MANUAL_OFF;
      moisture = analogRead(A0);
      percent = percentRH(moisture);
      digitalWrite(VALVE, LOW);
      sendToMaster();
  }
  receive = 0;
  Serial.println("Hello");
}
