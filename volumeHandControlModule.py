import cv2
import time
import numpy as np
import HandModule as hm
import math
'''pycaw library'''
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class volumeControl():
    def __init__(self):
        '''previous time'''
        self.pTime = 0

        '''creating object using  HandModule and pycaw'''
        self.detector = hm.handDetector(min_detection_confidence=0.7)
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))

        self.volRange = self.volume.GetVolumeRange()
        self.minVol = self.volRange[0]
        self.maxVol = self.volRange[1]

        self.vol = 0
        self.volBar = 400
        self.volPer = 0



    '''Hand Tracking'''
    def handLandMark(self,img):
        '''hand tracking'''
        img = self.detector.findHands(img)
        lmList = self.detector.findPosition(img, draw=False)

        return  img, lmList

    '''LandMarking'''
    def  fingerPosition(self,img,lmList):
        '''land marking'''
        if len(lmList) != 0:
            #print(lmList[4],lmList[8])
            '''position of middle finger as well as thumb'''
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]
            '''center between middle finger and  thumb'''
            cx, cy = (x1+x2)//2, (y1+y2)//2
            '''drawing landmarks'''
            
            cv2.circle(img, (x1,y1), 15, (255,0,0), cv2.FILLED)
            cv2.circle(img, (x2,y2), 15, (255,0,0), cv2.FILLED)
            cv2.line(img, (x1,y1), (x2,y2), (255,0,255), 3)
            cv2.circle(img, (cx,cy), 7, (255,0,0), cv2.FILLED)
            '''to find length of line'''
            length = math.hypot(x2-x1, y2-y1)
            current_xy_position_and_length = [cx,cy,length]
            #print(length)

        return img,current_xy_position_and_length

    '''function or displaying volume'''
    def volumeProcess(self,img,current_xy_position_and_length):
        '''find distance between index and thum's top and bottom part'''
        lengthT, img, lineinfo1 = self.detector.findDistance(4,2,img,draw=False)
        lengthI, img, lineinfo2 = self.detector.findDistance(8,6,img,draw=False)
        #print(lengthT,lengthI)
        if (lengthT > 60)  and (lengthI > 50):
            '''
            hand  range from 35 to 130
            volume range from  -65 to 0
            '''
            self.vol = np.interp(current_xy_position_and_length[2], [35,130], [self.minVol, self.maxVol])
            self.volBar = np.interp(current_xy_position_and_length[2], [35,130], [400, 150])
            self.volPer = np.interp(current_xy_position_and_length[2], [35,130], [0, 100])
            #print(int(length), vol)
            '''volume controlling'''
            self.volume.SetMasterVolumeLevel(self.vol, None)


            '''button effect'''
            if current_xy_position_and_length[2]<35:
                cv2.circle(img, (current_xy_position_and_length[0],current_xy_position_and_length[1]), 7, (0,255,0), cv2.FILLED)
            elif current_xy_position_and_length[2]>130:
                cv2.circle(img, (current_xy_position_and_length[0],current_xy_position_and_length[1]), 7, (0,0,255), cv2.FILLED)
            
            '''volume bar'''
            if self.volPer > 95:
                color=(0,0,255)
            elif self.volPer < 10:
                color=(0,255,0)
            else:
                color=(255,0,255)
            cv2.rectangle(img, (50,150),(85,400), color, 3)
            cv2.rectangle(img, (50,int(self.volBar)),(85,400), color, cv2.FILLED)


        return img

    def fps(self,img):
        '''showing fps'''
        cTime = time.time()
        fps = 1/(cTime-self.pTime)
        self.pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (10,30),cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 3)
        '''volume percentage'''
        if self.volPer > 95:
            color=(0,0,255)
        elif self.volPer < 10:
            color=(0,255,0)
        else:
            color=(255,0,255)

        cv2.putText(img, f'{int(self.volPer)}%', (45,430),cv2.FONT_HERSHEY_COMPLEX, 1, color, 2)

        return img

def main():
    '''Video Capturing'''
    cap = cv2.VideoCapture(0)
    cap.set(3,640)
    cap.set(4,480)



    volControl = volumeControl()

    while True:
        success, img = cap.read()

        '''Hand Detection'''
        img, lmlist = volControl.handLandMark(img)

        if len(lmlist) != 0:

            '''finger detection'''
            img, current_location = volControl.fingerPosition(img,lmlist)

            '''Dispaly Volume Control'''
            img = volControl.volumeProcess(img,current_location)
            
        '''Display FPS'''
        img = volControl.fps(img)
        
        cv2.imshow('Volume Hand Control',img)
        if cv2.waitKey(1) & 0xFF == ord('b'):       
            break

    cap.release()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()