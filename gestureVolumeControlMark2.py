# write on terminal : pip install opencv-python
# write on terminal : pip install mediapipe

import cv2 
import time
import numpy as np
import handTrackingModule as htm
import math

####  pycaw  ###
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
############

cap = cv2.VideoCapture(0)

wCam , hCam = 640 , 480

cap.set(3,wCam)
cap.set(4,hCam)
prevTime = 0

detector = htm.handDectector(detectionCon=0.7 , maxHands=1)


#############  pycaw  ##################
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()  #(-65 , 0)
# volume.SetMasterVolumeLevel(0, None)
########################################

minVol = volRange[0]
maxVol = volRange[1]
volBar = 400
vol = 0
volPercent = 0
area = 0
colorVol = (255,0,0)

while True:
    success , img = cap.read()
    img = detector.findHands(img)
    lmList,boundingbox = detector.findPosition(img , draw=True)

    if len(lmList)!=0:
        
        #FILTER BASED ON SIZE
        area = (boundingbox[2]-boundingbox[0])*(boundingbox[3] - boundingbox[1])//100
        # print(boundingbox[])
        # print(area)
        if 200<area<1000:
            # print('yes')
            
            #FIND THE DISTANCE BETWEEN INDEX N THUMB
            length,img, lineInfo =  detector.findDistance(4,8,img)
            # print(length)

            #CONVERT VOLUME 
            # print(lmList[4],lmList[8])
            # Hand range 50-300
            # vol range -65 0
            volBar = np.interp(length , [50,200] , [400 , 150])
            volPercent = np.interp(length , [50,200] , [0 , 100])
            # print(vol)
                   
            #REDUCE THE RESOLUTION TO MAKE IT SMOOTHER
            smoothness =10
            volPercent= smoothness*round(volPercent/smoothness)

            #CHECK FINGERS UP2
            fingers = detector.fingersUp()
            #print(fingers)

            #IF PINKY IS DOWN->SET VOLUME
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volPercent/100 , None)
                cv2.circle(img,(lineInfo[4],lineInfo[5]),15,(0,255,0) , cv2.FILLED)
                colorVol = (0,255,0)
                # time.sleep(0.25)
            else:
                colorVol = (255,0,0)
    

    #DRAWINGS
    cv2.rectangle(img , (50 , 150) , (35, 400) , (0,255 ,0) , 3)
    cv2.rectangle(img , (50 , int(volBar)) , (35, 400) , (0,255 ,0) , cv2.FILLED)
    cv2.putText(img , f'Vol % : {int(volPercent)}' , (40,450) , cv2.FONT_HERSHEY_PLAIN , 1.5,(255 , 0 , 0) , 2)
    currVol = int(volume.GetMasterVolumeLevelScalar()*100)
    cv2.putText(img , f'Vol Set : {int(currVol)}%' , (450,50) , cv2.FONT_HERSHEY_PLAIN , 1.5,colorVol , 2)
    

    #FRAMERATE
    currTime = time.time()
    fps = 1/(currTime - prevTime)
    prevTime = currTime

    cv2.putText(img , f'FPS : {int(fps)}%' , (40,50) , cv2.FONT_HERSHEY_PLAIN , 1,(255 ,0 , 0) , 2)

    cv2.imshow("Frame" , img)

    if cv2.waitKey(1) == ord('q'):
        break