/* 완성본 */

#define ENABLE_B  5
#define IN3_B  7
#define IN4_B  6

int led = 4;
int trigPin = 3;
int echoPin = 2;

int count = 0;
int count_initiate = 0;

byte speedDC = 255;


void setup()
{
  pinMode(ENABLE_B, OUTPUT);    // 모터 ENABLE 핀
  pinMode(IN3_B, OUTPUT);       // 모터 제어 핀1
  pinMode(IN4_B, OUTPUT);       // 모터 제어 핀2
  
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT); // 초음파 센서 Trig 핀
  pinMode(echoPin, INPUT);  // 초음파 센서 Echo 핀
  pinMode(led, OUTPUT);     // LED 핀(초음파 센서 인식됐을 때 켜지게 할 목적)
}

void loop()
{

  digitalWrite(trigPin, HIGH);     // 센서에 Trig 신호 입력
  delayMicroseconds(10);           // 10us 정도 유지
  digitalWrite(trigPin, LOW);      // Trig 신호 off

  long duration = pulseIn(echoPin, HIGH);     // Echo pin: HIGH->Low 간격을 측정
  long distance = duration / 29 / 2;          // 거리(cm)로 변환

  Serial.print(distance);                     // 시리얼 모니터에 거리 출력
  Serial.println("cm");

  analogWrite(ENABLE_B, 255);

  if(count_initiate == 0 )                    // 모터 초기값으로 만듦 (1번만 실행)
  {
     digitalWrite(IN3_B, HIGH);               // 모터 역방향 on
     digitalWrite(IN4_B, LOW);
     delay (3000);
     digitalWrite(IN3_B, LOW);                // 모터 off
     digitalWrite(IN4_B, LOW);

     count_initiate++;
  }

     
  if(distance < 10)                           // 거리가 10cm 이내일 때 실행
  {
    digitalWrite(led, HIGH);                  // 인식 구분을 위한 led on
    count ++;
    
    //Serial.print(count);                     // 시리얼 모니터에 카운트 횟수 출력
    //Serial.println(" count");

    if(count > 80)                             // 80번 이상 세면 실행
    {
    
     digitalWrite(IN3_B, LOW);                // 모터 정방향 on
     digitalWrite(IN4_B, HIGH);
     delay (2000);
     digitalWrite(IN3_B, HIGH);               // 모터 역방향 on
     digitalWrite(IN4_B, LOW);
     delay (2500);
     digitalWrite(IN3_B, LOW);                // 모터 off
     digitalWrite(IN4_B, LOW);

     count = 0;                               // 카운터 초기화
    }
  } 

  else                                        // 거리가 10cm 보다 멀 때 실행                      
  {
    digitalWrite(led, LOW);                  // 인식 구분을 위한 led off
    count = 0;                               // 카운터 초기화
  }
  
}
