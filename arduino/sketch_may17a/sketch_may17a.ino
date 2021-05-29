String text;

void setup() {
    pinMode(13,OUTPUT);
    Serial.begin(9600);
}

void loop() {
    while (Serial.available()) {
        delay(10);
        char c = Serial.read();
        text += c;
    }  

    if (text.length()>0) {
        Serial.println(text);
        if (text=="red") {
          digitalWrite(13,HIGH);
        }
        if (text=="green") {
          digitalWrite(12,HIGH);
        }
        if (text=="blue") {
          digitalWrite(11,HIGH);
        }
        if (text=="red off") {
          digitalWrite(13,LOW);
        }
        if (text=="blue off") {
          digitalWrite(11,LOW);
        }
        if (text=="green off") {
          digitalWrite(12,LOW);
        }
        if (text=="off") {
          digitalWrite(13,LOW);
          digitalWrite(12,LOW);
          digitalWrite(11,LOW);
        }
        if (text=="on") {
          digitalWrite(13,HIGH);
          digitalWrite(12,HIGH);
          digitalWrite(11,HIGH);
        }
                
        text = "";
    }
}
