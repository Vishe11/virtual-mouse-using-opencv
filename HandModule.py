import mediapipe as mp  #importing mediapipe library
import cv2              #importing computer vision
import time             #importing time library
import math             #imporiting math library


class handDetector():
    def __init__(self, static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5,min_tracking_confidence=0.5, model_complexity=1):
        self.static_image_mode = static_image_mode
        self.max_num_hands = max_num_hands
        self.model_complexity = model_complexity
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence

        self.mpHands = mp.solutions.hands    
        self.hands = self.mpHands.Hands(self.static_image_mode, self.max_num_hands, self.model_complexity, self.min_detection_confidence, self.min_tracking_confidence)

        self.mpDraw = mp.solutions.drawing_utils     #draws connections and other parts
        self.pTime = 0 #initial previous time

        '''finger tips'''
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw= True):
        #img = cv2.flip(img,1)  #image fliping  
        imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)#BGR to RGB image  
        self.results = self.hands.process(imgRGB) #detection process
        '''print(results.multi_hand_landmarks)'''
        
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks: #each hand marks
                if draw:
                    self.mpDraw.draw_landmarks(img,handLms ,
                                               self.mpHands.HAND_CONNECTIONS)#draws hand marks

        return img

    def findPosition(self, img, handNo=0, draw=True):

        self.lmlist = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]

            #identification  of finger id and its land marks position
            for id,lm in enumerate(myHand.landmark):
                #print(id,lm)
                h, w, c = img.shape #returns the height,width and channel of image
                cx,cy = int(lm.x * w),int(lm.y * h)
                '''print(id, cx, cy)'''
                self.lmlist.append([id, cx, cy])
                if draw:
                    cv2.circle(img,(cx,cy),10,(255,0,255),cv2.FILLED)

        return self.lmlist  
    
    def fingersUp(self):
        self.fingers = [] 
        '''codes for only one specific hand'''
        '''thumb'''
        if self.lmlist[self.tipIds[0]][1] > self.lmlist[self.tipIds[0] - 1][1]:
            self.fingers.append(1)
        else:
            self.fingers.append(0)

        '''other four fingers'''
        for id in range(1, 5):
            if self.lmlist[self.tipIds[id]][2] < self.lmlist[self.tipIds[id] - 2][2]:
                self.fingers.append(1)
            else:
                self.fingers.append(0)

        return self.fingers

    def findDistance(self, p1, p2, img, draw=True,r=15, t=3):
        x1, y1 = self.lmlist[p1][1:]
        x2, y2 = self.lmlist[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        #print(cx,cy)

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)

        return length, img, [x1, y1, x2, y2, cx, cy]
        
    def fps(self,img):
        '''showing fps'''
        cTime = time.time()
        fps = 1/(cTime-self.pTime)
        self.pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (10,30),cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 3)

        return img

    

def main():
    pTime = 0   #previous time
    cTime = 0   #current time
    vid = cv2.VideoCapture(0)   #Captures Video
    detector = handDetector()   #object for detection
    l = []
    length_list=[]
    while True:
        success,img = vid.read()    #storing video image
        img = detector.findHands(img)   #detected object 
        lmlist = detector.findPosition(img)
        #print(lmlist)
        '''
        if len(lmlist) != 0:
            length1,img,l1 = detector.findDistance(2,4,img)
            length_list.append(length1)
            print(length_list)
        '''

    
        img = detector.fps(img)



        cv2.imshow("Hand Detection",img)     #showing output
    
        if cv2.waitKey(1) & 0xFF == ord('b'): #break condtion
            break
        
    vid.release()   #release the output
    cv2.destroyAllWindows() #removes all output windows
            
if __name__ == "__main__":
    main()
