#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Pines del Lector RFID
#define SS_PIN 10
#define RST_PIN 9

// Pines de LEDs, Buzzer, y Botón
#define LED_VERDE 6
#define LED_ROJO 7
#define BUZZER 8
#define BOTON 4

MFRC522 mfrc522(SS_PIN, RST_PIN);
LiquidCrystal_I2C lcd(0x27, 16, 2);

// UID de la tarjeta maestra
String masterUID = "5363f0757101";

bool modoAlta = false;
bool modoBaja = false;

unsigned long lastButtonPress = 0;
unsigned long debounceTime = 200;
unsigned long doublePressInterval = 800;

void setup() {
    Serial.begin(9600);
    SPI.begin();
    mfrc522.PCD_Init();
    lcd.init();
    lcd.backlight();

    pinMode(LED_VERDE, OUTPUT);
    pinMode(LED_ROJO, OUTPUT);
    pinMode(BUZZER, OUTPUT);
    pinMode(BOTON, INPUT);

    lcd.setCursor(0, 0);
    lcd.print("Bienvenido a");
    lcd.setCursor(0, 1);
    lcd.print("Estetica Mari");
}

void loop() {
    detectarModo();
    verificarAcceso();
}

void detectarModo() {
    if (digitalRead(BOTON) == HIGH) {
        unsigned long currentTime = millis();

        if (currentTime - lastButtonPress < doublePressInterval) {
            modoBaja = true;
            modoAlta = false;
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("Borrar usuario:");
            lcd.setCursor(0, 1);
            lcd.print("Pase la tarjeta");
        } else {
            modoAlta = true;
            modoBaja = false;
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("Nueva alta:");
            lcd.setCursor(0, 1);
            lcd.print("Pase la tarjeta");
        }

        lastButtonPress = currentTime;
        delay(debounceTime);
    }
}

void verificarAcceso() {
    if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
        return;
    }

    String uid = obtenerUID();
    Serial.println(uid);

    if (modoAlta) {
        Serial.println("Alta UID: " + uid);

        while (Serial.available() > 0) {
            Serial.read();
        }

        delay(500);
        String respuesta = esperarRespuesta();
        respuesta.trim();

        if (respuesta.startsWith("Nuevo UID registrado")) {
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("UID registrado!");
            delay(2000);
        } else {
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("Registrando...");
            delay(2000);
        }

        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Bienvenido a");
        lcd.setCursor(0, 1);
        lcd.print("Estetica Mari");

        modoAlta = false;

    } else if (modoBaja) {
        Serial.println("Baja UID: " + uid);

        while (Serial.available() > 0) {
            Serial.read();
        }

        delay(500);
        String respuesta = esperarRespuesta();
        respuesta.trim();

        if (respuesta.startsWith("UID eliminado")) {
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("UID eliminado!");
            delay(2000);
        } else {
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("Eliminando...");
            delay(2000);
        }

        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Bienvenido a");
        lcd.setCursor(0, 1);
        lcd.print("Estetica Mari");

        modoBaja = false;

    } else {
        while (Serial.available() > 0) {
            Serial.read();
        }

        delay(500);
        String respuesta = esperarRespuesta();
        respuesta.trim();

        if (respuesta.startsWith("Acceso permitido")) {
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("Tenga buen dia");
            lcd.setCursor(0, 1);
            int idx = respuesta.indexOf(":");
            String nombre = respuesta.substring(idx + 2);
            lcd.print(nombre);
            digitalWrite(LED_VERDE, HIGH);
            digitalWrite(BUZZER, HIGH);
            delay(3000);
            digitalWrite(LED_VERDE, LOW);
            digitalWrite(BUZZER, LOW);
        } else {
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("Acceso");
            lcd.setCursor(0, 1);
            lcd.print("Denegado");
            digitalWrite(LED_ROJO, HIGH);
            digitalWrite(BUZZER, HIGH);
            delay(4000);
            digitalWrite(LED_ROJO, LOW);
            digitalWrite(BUZZER, LOW);
        }

        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Bienvenido a");
        lcd.setCursor(0, 1);
        lcd.print("Estetica Mari");
    }

    mfrc522.PICC_HaltA();
}

String obtenerUID() {
    String uid = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) {
        uid += String(mfrc522.uid.uidByte[i], HEX);
    }
    return uid;
}

String esperarRespuesta() {
    String respuesta = "";
    unsigned long startTime = millis();
    while (millis() - startTime < 1000) {
        if (Serial.available() > 0) {
            respuesta = Serial.readStringUntil('\n');
            break;
        }
    }
    return respuesta;
}
