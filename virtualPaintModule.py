'''importing modules'''
import cv2
import numpy as np
import HandModule as hm

class virtualPaint():
    def __init__(self, wCam=640, hCam=480):
        '''Variables'''
        self.wCam, self.hCam = wCam, hCam   #width &  height of output window
        self.drawColor = (0,0,255)   #default colour
        self.brushThickness = 15     #thickness of brush
        self.eraserThickness = 8     #eraser thickness
        self.xp, self.yp = 0,0            #x & y position

        '''for drawing a line'''
        self.imgCanvas = np.zeros((self.hCam,self.wCam,3), np.uint8)

        '''Creating hand detection object'''
        self.detector = hm.handDetector(min_tracking_confidence=0.85)

        '''reading eraser image'''
        eraser_path = r'F:\VIDYA ALL WORK & BACKUP\MainProject\eraser.png'
        self.eraser = cv2.imread(eraser_path)
        self.eraser = cv2.resize(self.eraser, (70,70))

        

    '''Hand Detection'''
    def handLandMark(self,img):
        '''find hand landmarks'''
        img = cv2.flip(img,1)
        img = self.detector.findHands(img)                          #processes image
        self.lmlist = self.detector.findPosition(img,draw=False)    #list of hand landmark position 

        return img, self.lmlist

    '''Colour Menu & other Operation function'''
    def menuBar(self,img):
        '''Colour Options/Plate'''

        '''main rectangle box (blue)'''
        cv2.rectangle(img, (0,0), (640,80), (255,0,255), 3)

        '''color circles'''
        cv2.circle(img, (40,40), 35, (0,0,255), cv2.FILLED)#red
        cv2.circle(img, (150,40), 35, (0,255,0), cv2.FILLED) #green
        cv2.circle(img, (260,40), 35, (255,0,0), cv2.FILLED)#blue
        
        '''eraser'''
        cv2.circle(img, (600,40), 35, (255,255,255), cv2.FILLED)
        img[5:(5 + self.eraser.shape[0]),565:(565 + self.eraser.shape[1])] = self.eraser

        return img

    '''function for finger position'''
    def fingerPosition(self):
        finger_location = []
        if len(self.lmlist) != 0 :

            '''tip of index and middle self.finger'''
            x1, y1 = self.lmlist[8][1:]
            x2, y2 = self.lmlist[12][1:]

            finger_location.append(x1)
            finger_location.append(y1)
            finger_location.append(x2)
            finger_location.append(y2)

        return finger_location

    '''function for colour selection operation'''
    def selectOperation(self, img, finger_location):
        
        '''chexk which self.finger are up'''
        self.finger = self.detector.fingersUp()

        '''Selection Mode : Two self.finger are up'''

        if self.finger[1] and self.finger[2]:
            '''distance between tip & bottom of a finger'''
            length1, img, lineInfo = self.detector.findDistance(8, 5, img, False) # returns lenth between 2 fingers, processed image, information of line
            length2, img, lineInfo = self.detector.findDistance(12, 9, img, False) # returns lenth between 2 fingers, processed image, information of line
            if (length1 > 85) & (length2 > 130):
                self.xp, self.yp = 0,0

                '''checking for click'''
                if finger_location[1] < 80:
                    '''RED'''
                    if 0 < finger_location[0] < 80:
                        cv2.rectangle(img, (0,0), (80,80), (0,0,255), 2) #first box
                        self.drawColor = (0,0,255)
                        '''GREEN'''
                    elif 110 < finger_location[0] < 190:
                        cv2.rectangle(img, (110,0), (190,80), (0,255,0), 2)#second box
                        self.drawColor = (0,255,0)
                        '''BLUE'''
                    elif 220 < finger_location[0] < 300:
                        cv2.rectangle(img, (220,0), (300,80), (255,0,0), 2)#third box
                        self.drawColor = (225,105,65)
                        '''ERASER'''
                    elif 560 < finger_location[0] < 640:
                        cv2.rectangle(img, (560,0), (640,80), (0,0,0), 2)
                        self.drawColor = (0,0,0)

                '''Selected colour will be shown on finger in rectangle'''
                cv2.rectangle(img, (finger_location[0], finger_location[1]-25), (finger_location[2],finger_location[3]+25), self.drawColor, cv2.FILLED)
            
        return img, self.finger
    
    '''function for draw operation'''
    def drawOperation(self, img, finger_location):
        '''Drawing Mode : Index finger is up'''
        if self.finger[1] and self.finger[2]==False:
            '''distance between tip of finger and bottom of finger'''
            length1, img, lineInfo = self.detector.findDistance(8, 6, img, False) # returns lenth between 2 self.finger, processed image, information of line
            #print(length1)
            if length1 > 85:
                '''mount selected colour on index finger'''
                cv2.circle(img, (finger_location[0],finger_location[1]), 15, self.drawColor, cv2.FILLED)

                '''previous value of x and y for starting a line'''
                if self.xp == 0 and self.yp == 0:
                    self.xp,self.yp = finger_location[0],finger_location[1]

                '''for eraser'''
                if self.drawColor == (0,0,0):
                    cv2.line(img, (self.xp,self.yp), (finger_location[0],finger_location[1]), self.drawColor, self.eraserThickness)
                    cv2.line(self.imgCanvas, (self.xp,self.yp), (finger_location[0],finger_location[1]), self.drawColor, self.eraserThickness)

                '''draw line'''
                cv2.line(img, (self.xp,self.yp), (finger_location[0],finger_location[1]), self.drawColor, self.brushThickness)
                cv2.line(self.imgCanvas, (self.xp,self.yp), (finger_location[0],finger_location[1]), self.drawColor, self.brushThickness)

                self.xp, self.yp = finger_location[0],finger_location[1]

        return img
    
    '''draw process'''
    def drawProcess(self, img):
        '''for drawing on same output window'''
        imgGray = cv2.cvtColor(self.imgCanvas, cv2.COLOR_BGR2GRAY)
        _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
        imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
        img = cv2.bitwise_and(img, imgInv)
        img = cv2.bitwise_or(img, self.imgCanvas)

        return img

    def msgDisplay(self,img,msg):
        if len(str(msg)) > 2:
            cv2.putText(img, str(f'{msg} Thickness Reached'), (20,450),cv2.FONT_HERSHEY_PLAIN, 1, (0,0,0), 2)
        else:
            cv2.putText(img, str(msg), (20,450),cv2.FONT_HERSHEY_PLAIN, 2, (0,0,0), 2)

    def toolThickness(self,img):
        '''Check for thumb'''
        lengthT,  img, linrInfo = self.detector.findDistance(4,0,img)
        if lengthT > 200:
            '''scroll up in which y value of thumb is less than index finger'''
            if (self.lmlist[4][2] < self.lmlist[8][2]):
                '''for colour thickness'''
                if self.drawColor in ((225,105,65), (0,255,0), (0,0,255)):
                    self.brushThickness += 2
                    self.msgDisplay(img,self.brushThickness)
                else:
                    self.eraserThickness += 2
                    self.msgDisplay(img,self.eraserThickness)

                '''if maximum brush thickness reached'''
                if (self.brushThickness > 50):
                    self.brushThickness = 50
                    img = self.msgDisplay(img, f'{self.brushThickness} Maximum Brush')

                '''if maximum eraser thickness reached'''
                if  (self.eraserThickness > 30):
                    self.eraserThickness = 30
                    img = self.msgDisplay(img, f'{self.eraserThickness} Maximum Eraser')

            elif (self.lmlist[4][2] > self.lmlist[8][2]):
                '''scroll down in which y value of thumb is greater than index finger'''

                if self.drawColor in ((225,105,65), (0,255,0), (0,0,255)):
                    self.brushThickness -= 2
                    img = self.msgDisplay(img,self.brushThickness)
                else:
                    self.eraserThickness -= 2
                    img = self.msgDisplay(img,self.eraserThickness) #Show thickness on outpt window
                
                '''if minimum brushthick ness reached'''
                if (self.brushThickness < 8):
                    self.brushThickness = 8
                    img = self.msgDisplay(img,f'{self.brushThickness} Minimum Brush')

                '''if minimum eraser thickness reached'''
                if (self.eraserThickness < 4):
                    print('level 5')
                    img = self.msgDisplay(img,f'{self.eraserThickness} Minimum Eraser')
                    self.eraserThickness = 4

def main():
    '''Variables'''
    wCam,hCam = 640,480

    '''Video Capturing'''
    vid = cv2.VideoCapture(0)
    vid.set(3,wCam)
    vid.set(4,hCam)

    paint = virtualPaint(wCam,hCam)

    while True:
        success, img = vid.read()

        '''hand lanmarks'''
        img, lmlist = paint.handLandMark(img)

        '''Menu bar'''
        img = paint.menuBar(img)

        '''Operation: finger position'''
        if len(lmlist) != 0:

            finger_location = paint.fingerPosition()

            '''Operation: Tool Thickness'''
            paint.toolThickness(img)

            '''Operation: Select Mode'''
            img, finger = paint.selectOperation(img, finger_location)

            '''Operation: Draw Mode'''
            img = paint.drawOperation(img, finger_location)

        '''draw process'''
        img = paint.drawProcess(img)

        cv2.imshow('Virtual Paint', img)

        if cv2.waitKey(1) & 0xFF == ord('b'):
            break

    vid.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
