'''Importing all required libraries'''
from tkinter import Image
import cv2                  #For image processing
import numpy as np          #For mathematical calculations
import HandModule as hm    #For hand traking
import time                 #For calculating time
import pyautogui as pag     #For controlling mouse

class virtualMouse():
    def __init__(self, wCam=640, hCam=480):

        '''Object Variables'''
        self.frameR = 100                 #Frame reduction
        self.smoothening =  8             #Smoothen the mouse movements
        self.clocX, self.clocY = 0, 0     #Initial current location of mouse (x-axis, y-axis)
        self.plocX, self.plocY = 0, 0     #Initial previous location of mouse (x-axis, y-axis)
        self.wScr, self.hScr = pag.size()  #Width & height of user's system
        self.wCam, self.hCam = wCam, hCam # width & height of output window
        self.pTime=0                      #Initial previous time

        self.detector = hm.handDetector(max_num_hands=1) #Creating hand detection object

    '''function to find handLandmark'''
    def handLandMarks(self,img):
        img = self.detector.findHands(img)             #Hand tracking of image              
        self.lmlist = self.detector.findPosition(img)  #List of all finger position
        return img, self.lmlist

    '''function for finger tip detection'''
    def fingerTip(self, img, draw = True):
        ''' Get the tip of the index and middle fingers '''
        self.finger_Location=[]
        if len(self.lmlist) != 0:            #To avoid error when there is no finger/hand for processing

            x1, y1 = self.lmlist[8][1:]      #Tip of Index finger
            self.finger_Location.append(x1)
            self.finger_Location.append(y1) 

            x2, y2 = self.lmlist[12][1:]     #Tip of Middle finger
            self.finger_Location.append(x2)
            self.finger_Location.append(y2)  
 
            if draw:
                cv2.rectangle(img, (self.frameR, self.frameR), (self.wCam - self.frameR, self.hCam - self.frameR),(255, 0, 255), 2)   #Area where finger can be detected with pink color
        return self.finger_Location

    '''function to move cursor'''
    def moveMode(self, img): 
        '''Check which fingers are up'''
        self.finger = self.detector.fingersUp()    #Finger Detector object

        '''  Moving Mode : Only Index Finger   '''
        if self.finger[1] == 1 :  #Check fingers 1:Up & 0:Down
            '''distance between tip of finger and bottom of finger'''
            length1, img, lineInfo = self.detector.findDistance(8, 6, img, False) # returns lenth between 2 fingers, processed image, information of line
            #print(length1)
            if length1 > 85:

                '''  Convert Coordinates : detected finger location into desired location in monitor/system 
                x3 = np.interp(self.finger_Location[0], (self.frameR*(3/2), self.wCam - self.frameR*(3/2)), (0, self.wScr))  #X-axis
                y3 = np.interp(self.finger_Location[1], (self.frameR*(3/2), self.hCam - self.frameR*(3/2)), (0, self.hScr))  #Y-axis
                '''

                x3 = np.interp(self.finger_Location[0], (self.frameR, self.wCam/2), (0,self.wScr))  #X-axis
                y3 = np.interp(self.finger_Location[1], (self.frameR, self.hCam/2), (0,self.hScr))  #Y-axis

                '''  Smoothen Values : For mouse to move continous without any glitch/hesitation'''
                self.clocX = self.plocX + (x3 - self.plocX) / self.smoothening #X-axis
                self.clocY = self.plocY + (y3 - self.plocY) / self.smoothening  #Y-axis
                
                '''  Move Mouse '''
                cv2.circle(img, (self.finger_Location[0], self.finger_Location[1]), 15, (0, 255, 255), cv2.FILLED)    #Draws a circle on index finger
                pag.moveTo(self.wScr - self.clocX, self.clocY)                             #Using pyautogui move mouse to where index finger is
                self.plocX, self.plocY = self.clocX, self.clocY                                 #Now current location becomes previous location when time/program goes on

    '''function for click'''
    def clickMode(self,img):           
        '''  Clicking Mode : Both Index and middle fingers are up '''
        if self.finger[1] == 1 and self.finger[2] == 1:                         #Check fingers 1:Up & 0:Down
            '''distance between tip & bottom of a finger'''
            length1, img, lineInfo = self.detector.findDistance(8, 5, img, False) # returns lenth between 2 fingers, processed image, information of line
            length2, img, lineInfo = self.detector.findDistance(12, 9, img, False) # returns lenth between 2 fingers, processed image, information of line
            #print(length2)
            if (length1 > 85) & (length2 > 130):
                '''  Find distance between fingers '''
                length3, img, lineInfo = self.detector.findDistance(8, 12, img) # returns lenth between 2 fingers, processed image, information of line

                #print(length3)
                '''  Click left mouse if distance short '''
                if length3 < 45:     #If distance between finger is short or less than specific unit. 
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)    #Draws a click green circle
                    pag.click(button = 'left')     #click operation using  pyautogui
                
        '''Click right if both index and little finger is up'''
        if self.finger[1]==1 and self.finger[4]==1:
            '''  Find distance between fingers '''
            lengthIL, img, lineInfo = self.detector.findDistance(8, 20, img) # returns lenth between 2 fingers, processed image, information of line
            lengthI, img, lineInfo = self.detector.findDistance(8, 5, img) # returns lenth between 2 fingers, processed image, information of line
            lengthL, img, lineInfo = self.detector.findDistance(20, 17, img) # returns lenth between 2 fingers, processed image, information of line
            print(lengthL)
            if (lengthI > 85) & (lengthL > 80):
            #    if lengthIL < 60: 
                cv2.circle(img, (self.lmlist[8][1], self.lmlist[8][2]), 15, (0, 100, 0), cv2.FILLED)    #Draws a click circle on index finge
                cv2.circle(img, (self.lmlist[20][1], self.lmlist[20][2]), 15, (0, 100, 0), cv2.FILLED)    #Draws a click circle on little finger
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 8, (0, 255, 0), cv2.FILLED)    #Draws a click green circle
                pag.click(button = 'right')     #click operation using  pyautogui
        
    '''function for close window'''
    def closeMode(self,cap):
        '''check if both index and little fingers are up'''
        while True:
            if sum(self.finger) == 0:
                return True
            else:
                return False

    '''function for screenshot'''
    def screenShot(self, img, fps, folderPath = r'C:\Users\Samata\Desktop\screenshot', fileExtension = "png"):
        '''Check  index, middle & ring finger are up '''
        if self.finger[1] == 1 and self.finger[2] == 1 and self.finger[3] == 1:
         
            '''ScreenShot Process'''
            '''Find distance between index & middle fingers''' 
            length1, img, lineInfo = self.detector.findDistance(8, 5, img, False) # returns lenth between 2 fingers, processed image, information of line
            length2, img, lineInfo = self.detector.findDistance(12, 9, img, False) # returns lenth between 2 fingers, processed image, information of line
            length3, img, lineInfo = self.detector.findDistance(16, 13, img, False) # returns lenth between 2 fingers, processed image, information of line


            if (length1 >85) and (length2 > 130) and (length3 > 105) :
                for i in range(int(fps/fps)):

                    '''Show screenshot message on outpt window'''
                    cv2.putText(img, str("screenshot saved....."), (20, 430), cv2.FONT_HERSHEY_PLAIN, 2,(255, 0, 0), 2)
                    break
                '''draw white color on fingers'''
                cv2.circle(img, (self.lmlist[8][1], self.lmlist[8][2]), 15, (255, 255, 255), cv2.FILLED)    #Draws a circle
                cv2.circle(img, (self.lmlist[12][1], self.lmlist[12][2]), 15, (255, 255, 255), cv2.FILLED)    #Draws a circle
                cv2.circle(img, (self.lmlist[16][1], self.lmlist[16][2]), 15, (255, 255, 255), cv2.FILLED)    #Draws a circle

                timeStr =  time.ctime(time.time())
                timeStr = timeStr.replace(':','')
                fileName = 'Screenshot ' + timeStr
                folderPath = r'C:\Users\Samata\Desktop\screenshot'
                #folderPath = 'F:\PROGRAM FILES\OpenCV\images'
                fileExtension = "png"
                fileDirectory = f"{folderPath}\{fileName}.{fileExtension}"
                pic = pag.screenshot()
                pic.save(fileDirectory)
                #time.sleep(2)
                 

    '''function for scroll'''
    def scroll(self,img):
        '''Check for thumb'''
        if self.finger[0] == 1:
            '''Check for thumb'''
            lengthT,  img, linrInfo = self.detector.findDistance(4,2,img)
            if lengthT > 82:
                '''scroll up in which y value of thumb is less than index finger'''
                if (self.lmlist[4][2] < self.lmlist[8][2]):
                    pag.scroll(100)
                    '''scroll down in which y value of thumb is greater than index finger'''
                elif (self.lmlist[4][2] > self.lmlist[8][2]):
                    pag.scroll(-100)
                cv2.circle(img, (self.lmlist[4][1], self.lmlist[4][2]), 15, (0, 255, 255), cv2.FILLED)    #Draws a click circle on index finge
    
    '''function for fps'''
    def fps(self,img):
        '''showing fps'''
        cTime = time.time()
        fps = 1/(cTime-self.pTime)
        self.pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (10,30),cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 3)

        return img

            


def main():
    close = False
    wCam, hCam = 640, 480   #Width & Height of output window
    fps = 1

    '''Video Capturing'''
    cap = cv2.VideoCapture(0)
    cap.set(3, wCam)                        #Setting width 
    cap.set(4, hCam)                        #Setting height

    pag.FAILSAFE = False

    mouse = virtualMouse(wCam, hCam)

    '''Back Processing'''
    while True:
        ''' 1. Find hand Landmarks '''
        success, img = cap.read()   #Reads each image
        #img = cv2.flip(img,1)       #flip image
        '''hand detection & finger position '''
        img, lmlist = mouse.handLandMarks(img)  #lmlist contains info of landmarks of each finger of given input image


        '''2. Get the tip of the index & middle fingers'''
        if len(lmlist) != 0:
            '''
            finger_location : location of finger at goven screen area
            fingers         : Checks which fingers are up
            '''
            finger_Location = mouse.fingerTip(img, False)
            
            '''3. Mouse operation 1: Move Mode'''
            move = mouse.moveMode(img)

            '''4. Mouse operation 2: Click Mode'''
            click = mouse.clickMode(img)

            '''5. Mouse Operation 3: Screenshot'''
            screenshot = mouse.screenShot(img, fps)

            '''6. Mouse Operation $: Scroll'''
            scroll = mouse.scroll(img)

            '''Break Condition'''
            #close = mouse.closeMode(cap)


        '''7. Frame Rate '''
        img = mouse.fps(img)

        ''' 8. Display '''
        cv2.imshow("Virtual Mouse", img)                          #Output window

        if  (cv2.waitKey(1) & 0xFF == ord('b')) or close == True: #Break condition
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
        





