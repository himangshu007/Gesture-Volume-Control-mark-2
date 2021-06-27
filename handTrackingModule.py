# write in terminal: pip install mediapipe
# write in terminal: pip install opencv-python

import cv2 
import time
import mediapipe as mp
import math

class handDectector():
    def __init__(self , mode =False , maxHands = 2 , detectionCon=0.5 , trackCon = 0.5 ):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode ,self.maxHands ,self.detectionCon,self.trackCon )
        self.mpDraw = mp.solutions.drawing_utils
        self.handLine = self.mpHands.HAND_CONNECTIONS
        self.tipIds = [4,8,12,16,20]

    def findHands(self , img , draw = True):
        imgRGB = cv2.cvtColor(img , cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

            # to check if we hand multiple hands
        if self.results.multi_hand_landmarks:
            for eachHand in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img , eachHand , self.handLine) 
            
        return img

    def findPosition(self , img ,handNo=0 , draw=True):
        xList = []
        yList = []
        self.lmList = []
        boundingbox = []

        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]

            for id , lm in enumerate(myHand.landmark):
                # print(id , lm)
                h , w , c = img.shape
                cx , cy = int(lm.x*w) , int(lm.y*h)
                xList.append(cx)
                yList.append(cy)
                # print(id ,cx,cy)
                self.lmList.append([id,cx,cy])
                if draw:
                    cv2.circle(img , (cx,cy) , 5 , (255,0,255) , cv2.FILLED)
            
            xmin , xmax =min(xList) , max(xList)
            ymin , ymax =min(yList) , max(yList)
            boundingbox = xmin , ymin , xmax , ymax

            if draw:
                cv2.rectangle( img , (boundingbox[0]-20 , boundingbox[1]-20),(boundingbox[2]+20 , boundingbox[3]+20)  , (0 , 255, 0) , 2)

        return self.lmList , boundingbox

    def fingersUp(self):
        fingers = []
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0]-1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        for id in range(1,5):
            if self.lmList[self.tipIds[id]][2]< self.lmList[self.tipIds[id]-2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers


    def findDistance(self,p1,p2,img,draw=True):
        x1,y1 = self.lmList[p1][1] , self.lmList[p1][2] #for thumb
        x2,y2 = self.lmList[p2][1] , self.lmList[p2][2] #for index-finger
        cx , cy = (x1+x2)//2 , (y1+y2)//2
        
        if draw:
            cv2.circle(img,(x1,y1),15,(255,0,255) , cv2.FILLED)
            cv2.circle(img,(x2,y2),15,(255,0,255) , cv2.FILLED)
            cv2.line(img , (x1,y1) , (x2,y2)  , (255 , 0 ,255), 3)
            cv2.circle(img,(cx,cy),15,(255,0,255) , cv2.FILLED)

        length = math.hypot(x2-x1 , y2-y1)
        return length , img , [x1 , y1 , x2 , y2 , cx , cy]


def main():
    prevTime = 0
    currTime = 0
    cap = cv2.VideoCapture(0)

    
    detector = handDectector()
    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        
        if len(lmList)!=0:
            # print(lmList[4])
            pass

        currTime = time.time()
        fps = 1/(currTime - prevTime)
        prevTime = currTime

        cv2.putText( img , str(int(fps)) , (10 , 70) , cv2.FONT_HERSHEY_PLAIN , 3 , (255,0,255),3)

        cv2.imshow("Image",img)
        if cv2.waitKey(1)== ord('q'):
            break



if __name__ == "__main__":
    main()
