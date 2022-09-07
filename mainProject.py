from tkinter import *
import cv2
import virtualMouseModule 
import virtualPaintModule 
import volumeHandControlModule

'''Functions'''

'''function for colour conversion'''
def rgb_hack(rgb):
    return "#%02x%02x%02x" % rgb

def startCamera():
    #pTime = 0
    #close = False
    '''Width & Height of output window'''
    wCam, hCam = 640, 480   
    #fps = 1
   
    cap = cv2.VideoCapture(0)
    '''Setting height & Setting width'''
    cap.set(3, wCam)                         
    cap.set(4, hCam)                        
    return cap

'''function for Virtual mouse'''
def VirtualMouse():
    mouse = virtualMouseModule.virtualMouse()
    '''Initial previous time'''
    pTime = 0
    fps=1
    '''use of startCamera function'''
    cap = startCamera()
    '''Back Processing'''
    while True:
        ''' 1. Find hand Landmarks '''
        success, img = cap.read()   #Reads each image
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

        '''7.Display FPS'''
        img = mouse.fps(img)

        ''' 8. Display '''
        cv2.imshow("Virtual Mouse", img)                          #Output window

        if  (cv2.waitKey(1) & 0xFF == ord('b')): #Break condition
            break

    cap.release()
    cv2.destroyAllWindows()

'''function for Virtual paint'''
def VirtualPaint():
    cap = startCamera()
    paint = virtualPaintModule.virtualPaint()
    while True:
        success, img = cap.read()

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

    cap.release()
    cv2.destroyAllWindows()

'''function for Volume control'''
def VolumeControl():
    volControl = volumeHandControlModule.volumeControl()
    cap = startCamera()
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
        
        cv2.imshow('Volume Control',img)
        if cv2.waitKey(1) & 0xFF == ord('b'):       
            break

    cap.release()
    cv2.destroyAllWindows()    

'''Dummy Click function'''
def click():
    clickedMsg = Label(text="Button was clicked").pack()

'''creating a GUI window & it's dimension'''
main_window = Tk()
width, height = 390,420

'''dimension of main GUI window'''
main_window.geometry(f'{width}x{height}')
main_window.minsize(width,height)
main_window.maxsize(width,height)
main_window.configure(bg=rgb_hack((230,230,230)))
'''Name of GUI window'''
main_window.title("MoVir")

'''Frame 1: Hand Detection'''
# F1 = Frame(main_window, bg=rgb_hack((0,255,255)), height=40,width=100)
# F1.place(x=60, y=50)
# L1 = Label(F1, text="Hand Detection", fg = "black", height=2,width=16, font='Helvetica 10 bold', bg=rgb_hack((127,255,0))).pack()
# c= Canvas(main_window,width=40, height=34, bg=rgb_hack((127,255,0)))
# c.pack()
#Draw an Oval in the canvas
#c.place(x=180, y=50)
#c.create_oval(35,35,6,4)

'''Frame 2: FPS Counter'''
# F2 = Frame(main_window, bg=rgb_hack((255, 102, 178)), height=40, width=100)
# F2.place(x=270, y=50)
# L2 = Label(F2, text="FPS Counter", fg = "black", height=2,width=16, font='Helvetica 10 bold', bg=rgb_hack((0,255,255))).pack()

'''Button 1: Virtual Mouse'''
Virmouse = Button(main_window, text="Virtual Mouse",relief=SUNKEN,borderwidth=6,  height=2,width=16, activebackground="light blue",command=VirtualMouse, font='Helvetica 10 bold', bg=rgb_hack((255,153,221)))
Virmouse.place(x=90,y=90)

'''Button 2: Virtual Paint'''
paint = Button(main_window, text="Virtual Paint",relief=SUNKEN,borderwidth=6, height=2,width=16, activebackground="Lime",command=VirtualPaint, font='Helvetica 10 bold', bg=rgb_hack((255,215,0)))
paint.place(x=90,y=170)    

'''Button 3: Volume Control'''
volume = Button(main_window, text="Volume Control", relief=SUNKEN,borderwidth=6, height=2,width=16, activebackground="cyan" , command=VolumeControl, font='Helvetica 10 bold', bg=rgb_hack((153,187,255)))
volume.place(x=90,y=250)

'''GUI window loop'''
main_window.mainloop()