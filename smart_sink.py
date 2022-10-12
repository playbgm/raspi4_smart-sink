from collections import Counter
import RPi.GPIO as GPIO
import math
import csv
import cv2
import mediapipe
import os
import pigpio
import time
from time import sleep
from RpiMotorLib import RpiMotorLib

pi = pigpio.pi()

servo_pin = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.OUT)
GPIO.output(24, True)

servo_min_duty = 1000
servo_max_duty = 1800


drawingModule = mediapipe.solutions.drawing_utils
handsModule = mediapipe.solutions.hands
mod=handsModule.Hands()



h=480
w=640
cap = cv2.VideoCapture(-1)
tip=[8,12,16,20]
tipname=[8,12,16,20]
fingers=[]
finger=[]
listgest=[]

state = 1
LED_ON_counter = 0
LED_OFF_counter = 0
STOP_counter = 0
START_counter = 0

ret, frame = cap.read()
rows, cols, _ = frame.shape

x_medium = int(cols / 2)
x_center = int(cols / 2)
y_medium = int(rows / 2)
y_center = int(rows / 2)

x_position = 1400

def stepm(turn,range):
    GPIO_pins=(14,15,18)
    direction=20
    step=21

    mymotortest=RpiMotorLib.A4988Nema(direction,step,GPIO_pins,"A4988")
    mymotortest.motor_go(turn,'Full',range,.007,False,.05)
    
def initializing():
    stepm(1, 50)
    while (True):
        stepm(0, 10)
        if (GPIO.input(6) == False):
            print("button")
            stepm(1,20)
            break
        
def findpostion(frame1):
    list=[]
    results = mod.process(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))
    if results.multi_hand_landmarks != None:
       for handLandmarks in results.multi_hand_landmarks:
           drawingModule.draw_landmarks(frame1, handLandmarks, handsModule.HAND_CONNECTIONS)
           list=[]
           for id, pt in enumerate (handLandmarks.landmark):
                x = int(pt.x * w)
                y = int(pt.y * h)
                list.append([id,x,y])

    return list            

def findnameoflandmark(frame1):
     list=[]
     results = mod.process(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))
     if results.multi_hand_landmarks != None:
        for handLandmarks in results.multi_hand_landmarks:
            for point in handsModule.HandLandmark:
                 list.append(str(point).replace ("< ","").replace("HandLandmark.", "").replace("_"," ").replace("[]",""))
     return list


def maybeMakeNumber(s):


    if not s:
        return s

    try:
        f = float(s)
        i = int(f)
        return i if f == i else f
    except ValueError:
        return s

step_counter = 0

initializing()

while True:
     ret, frame = cap.read() 
     frame1 = cv2.resize(frame, (640, 480))

     
     a=findpostion(frame1)
     b=findnameoflandmark(frame1)
     
     if len(b and a)!=0:
        finger=[]
        if a[0][1:] < a[4][1:]: 
           finger.append(1)
          
        else:
           finger.append(0)
        
        
        
        fingers=[]
        listgest=[]
        for id in range(0,4):
            if a[tip[id]][2:] < a[tip[id]-2][2:]:
               listgest.append(b[tipname[id]])
               fingers.append(1)
    
            else:
               fingers.append(0)
          

     x=fingers + finger
     c=Counter(x)
     up=c[1]
     down=c[0]


     listgest.append(up)
     listgest.append(down)


     if len(listgest) > 6:
        listgest = []
        
        
   
     with open('./model.csv',encoding='utf-8-sig') as f:
        keypoint_classifier_labels = csv.reader(f)
        for row in keypoint_classifier_labels:
            gesturecsv = row[:(len(row)-1)]
            gest = row[(len(row)-1):]

            gesturecsv = list(map(maybeMakeNumber, gesturecsv))
            if listgest == gesturecsv:
                cv2.putText(frame1, "GESTE :"+str(gest), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
                
                if(str(gest) == "['"+'start'+"']"):
                    START_counter += 1
                    STOP_counter = 0
                    LED_OFF_counter = 0
                    LED_ON_counter = 0
                    if START_counter == 10:
                        state = 1
                        print("tracking start")
                        START_counter = 0
                        
                    
                elif(str(gest) == "['"+'stop'+"']"):
                    STOP_counter += 1
                    START_counter = 0
                    LED_OFF_counter = 0
                    LED_ON_counter = 0
                    if STOP_counter == 10:
                        state = 0
                        print("tracking stop")
                        STOP_counter = 0
                    
                elif(str(gest) == "['"+'WATER_ON'+"']"):
                    LED_ON_counter += 1
                    LED_OFF_counter = 0
                    STOP_counter =0
                    START_counter = 0
                    if LED_ON_counter == 10:
                        GPIO.output(24, False)
                        LED_ON_counter == 0
                        
                elif(str(gest) == "['"+'WATER_OFF'+"']"):
                    LED_OFF_counter += 1
                    LED_ON_counter = 0
                    STOP_counter =0
                    START_counter = 0
                    if LED_OFF_counter == 10:
                        GPIO.output(24, True)
                        LED_OFF_counter == 0
            
            if state == 1:
                cv2.putText(frame1, "TRACKING : START", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2, cv2.LINE_AA)
            elif state == 0:
                cv2.putText(frame1, "TRACKING : STOP", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 0, 0), 2, cv2.LINE_AA)
      
     
    
     cv2.imshow("Frame", frame1);
     key = cv2.waitKey(1) & 0xFF
     if key == ord("1"):
        print("<-Learning Mode->")
        if len(listgest)<=6:
           gest = str(input("Name : "))
           csv_path = './model.csv'
           with open(csv_path,'a', encoding='utf-8', newline="") as f:
              writer = csv.writer(f)
              listgest.append(gest)
              writer.writerow(listgest)
        else: 
           print("IMPOSSIBLE")
     if key == ord("2"):
        print("Bye")
        break
     
     if len(a) != 0:
         if(state == 1):
            x_medium = a[9][1]
            y_medium = a[9][2]
            
        #move servo motor x
            if x_medium < x_center - 30:
                if x_medium < x_center - 120:
                    x_position += 20
                else:
                    x_position += 10
                
                if x_position >= servo_max_duty:
                    x_position = servo_max_duty
                
                pi.set_servo_pulsewidth(servo_pin, x_position)

            
            elif x_medium > x_center + 30:
            
                if x_medium > x_center + 120:
                    x_position -= 20
                else:
                    x_position -= 10
            
                if x_position <= servo_min_duty:
                    x_position = servo_min_duty
                
                pi.set_servo_pulsewidth(servo_pin, x_position)
                
            if y_medium < y_center - 20:
                y_position = 20
                step_counter += 1
                print(step_counter)
        
                if(step_counter < 30):
                    stepm(1, y_position)
                else:
                    step_counter = 29

        
            elif y_medium > y_center + 20:
                y_position = 20
                step_counter -= 1
                print(step_counter)
        
                if(step_counter > 0):
                    stepm(0, y_position)
                else:
                    step_counter=1



