
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import sys
 
#img = cv2.imread('1.png')
cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
# cap.set(3,4416)
# cap.set(4,1242)
 
def show(A,scale=50):
    scale_percent = scale
    width = int(A.shape[1] * scale_percent / 100)
    height = int(A.shape[0] * scale_percent / 100)
    dim = (width, height)
    resize = cv2.resize(A, dim, interpolation = cv2.INTER_AREA)
    cv2.imshow("All QR",resize)
    cv2.waitKey()
    cv2.destroyAllWindows()

#def F_pos(seek)
seek = ''
while seek != '-1':
    seek = input('What you want to find?')
    #seek = sys.argv[1]
    seek = str(seek)
    if seek == 'exit':
        exit()
    item_dic = {}
    isBreak = False
    while not isBreak:
        
        success, img = cap.read()
        for barcode in decode(img):
            myData = barcode.data.decode('utf-8')
            item_dic[myData]=[barcode.polygon]
            pts = np.array([barcode.polygon],np.int32)
            pts = pts.reshape((-1,1,2))
            cv2.polylines(img,[pts],True,(255,0,255),5)
            pts2 = barcode.rect
            cv2.putText(img,myData,(pts2[0],pts2[1]),cv2.FONT_HERSHEY_SIMPLEX, 0.9,(255,0,255),2)
            if str(myData) == seek:
                print(seek + 'position is ' + str(item_dic[myData]))
                exit()
                isBreak = True
                break
        
        scale_percent = 50
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        resize = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)


        cv2.imshow('Result',resize)
        #cv2.imshow('Result',img)
        cv2.waitKey(1)
