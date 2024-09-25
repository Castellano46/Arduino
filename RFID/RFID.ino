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

// Inicialización del Lector RFID y la Pantalla LCD
MFRC522 mfrc522(SS_PIN, RST_PIN);
LiquidCrystal_I2C lcd(0x27, 16, 2); // 0x27 es la dirección I2C de la pantalla, puede variar

// UID de la tarjeta maestra (debe ser modificada con el UID de tu tarjeta maestra)
String masterUID = "A1B2C3D4";

void setup() {
  // Configuración inicial
  Serial.begin(9600);
  SPI.begin();
  mfrc522.PCD_Init();
  
  // Inicialización de la Pantalla LCD
  lcd.init();
  lcd.backlight();
  
  // Configuración de pines
  pinMode(LED_VERDE, OUTPUT);
  pinMode(LED_ROJO, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  pinMode(BOTON, INPUT);
  
  // Mensaje de bienvenida
  lcd.setCursor(0, 0);
  lcd.print("Bienvenido al");
  lcd.setCursor(0, 1);
  lcd.print("Gym");
  delay(2000);
  lcd.clear();
}

void loop() {
  // Si el botón es presionado, entra en modo de programación
  if (digitalRead(BOTON) == HIGH) {
    agregarTarjeta();
  } else {
    verificarAcceso();
  }
}

void verificarAcceso() {
  // Verificar si hay una tarjeta presente y leer su UID
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    return;
  }

  // Obtener el UID de la tarjeta
  String uid = obtenerUID();
  Serial.println("UID leido: " + uid);

  // Comparar el UID con el UID maestro
  if (uid == masterUID) {
    accesoPermitido();
  } else {
    accesoDenegado();
  }

  // Detener la lectura de la tarjeta
  mfrc522.PICC_HaltA();
}

void agregarTarjeta() {
  // Modo de programación: agregar una nueva tarjeta
  Serial.println("Modo de programación: Pasa una nueva tarjeta");

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Modo Programac.");
  lcd.setCursor(0, 1);
  lcd.print("Pasa la Tarjeta");

  // Esperar hasta que se lea una nueva tarjeta
  while (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    delay(10);
  }

  // Leer el UID de la nueva tarjeta
  String nuevoUID = obtenerUID();
  Serial.println("Nuevo UID registrado: " + nuevoUID);

  // Aquí se puede guardar el nuevo UID en una lista o base de datos
  accesoPermitido();

  // Detener la lectura de la tarjeta
  mfrc522.PICC_HaltA();
}

String obtenerUID() {
  // Función para obtener el UID de la tarjeta
  String uid = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    uid += String(mfrc522.uid.uidByte[i], HEX);
  }
  return uid;
}

void accesoPermitido() {
  // Función para indicar que el acceso es permitido
  Serial.println("Acceso permitido");
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Acceso");
  lcd.setCursor(0, 1);
  lcd.print("Permitido");
  
  digitalWrite(LED_VERDE, HIGH);
  digitalWrite(BUZZER, HIGH);
  delay(1000);
  digitalWrite(LED_VERDE, LOW);
  digitalWrite(BUZZER, LOW);
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Bienvenido al");
  lcd.setCursor(0, 1);
  lcd.print("Gym");
  delay(2000);
  lcd.clear();
}

void accesoDenegado() {
  // Función para indicar que el acceso es denegado
  Serial.println("Acceso denegado");
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Acceso");
  lcd.setCursor(0, 1);
  lcd.print("Denegado");
  
  digitalWrite(LED_ROJO, HIGH);
  digitalWrite(BUZZER, HIGH);
  delay(1000);
  digitalWrite(LED_ROJO, LOW);
  digitalWrite(BUZZER, LOW);
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Bienvenido al");
  lcd.setCursor(0, 1);
  lcd.print("Gym");
  delay(2000);
  lcd.clear();
}
