//SEMAFORO

# define rojoc 4
# define amarilloc 3
# define verdec 2
# define verdep 8
# define rojop 9

void setup() {
pinMode (rojoc, OUTPUT);
pinMode (amarilloc, OUTPUT);
pinMode (verdec, OUTPUT);
pinMode (verdep, OUTPUT);
pinMode (rojop, OUTPUT);
}

void loop() {
  digitalWrite (rojoc, HIGH);
  digitalWrite (verdep, HIGH);
  delay(4000);
  digitalWrite (rojoc, HIGH);
  digitalWrite (verdep, LOW);
  delay(200);
  digitalWrite (rojoc, HIGH);
  digitalWrite (verdep, HIGH);
  delay(200);
  digitalWrite (rojoc, HIGH);
  digitalWrite (verdep, LOW);
  delay(200);
  digitalWrite (rojoc, HIGH);
  digitalWrite (verdep, HIGH);
  delay(200);
  digitalWrite (rojoc, HIGH);
  digitalWrite (verdep, LOW);
  delay(200);
  digitalWrite (rojoc, HIGH);
  digitalWrite (verdep, HIGH);
  delay(200);
  digitalWrite (rojoc, LOW);
  digitalWrite (verdep, LOW);
  delay(200);
  digitalWrite (verdec, HIGH);
  digitalWrite (rojop, HIGH);
  delay(4000);
  digitalWrite (verdec, LOW);
  digitalWrite (rojop, HIGH);
  delay(200);
  digitalWrite (amarilloc, HIGH);
  digitalWrite (rojop, HIGH);
  delay(1000);
  digitalWrite (amarilloc, LOW);
  digitalWrite (rojop, LOW);
  delay(200);
}
