import cv2
import numpy as np
from pyzbar.pyzbar import decode
from optparse import OptionParser

parser = OptionParser()

parser.add_option('-t', '--target', dest='target', help='Number of target object', type='string', default='0')
parser.add_option('-v', '--video-device', dest='vid_id', help='Id of video capture', type='int', default=0)
parser.add_option('-s', '--source-image', dest='src_img', help='A relative path to pre-capture image that use for calibrate process', default='')
parser.add_option('--verbose', dest='verbose', help='Show image', action='store_true', default=False)
 
def finder(capture, target:str, verbose:bool = False):
    item_dic = {}
    centroid = []
    flag = True
    while flag:
        _, img = capture.read()
        for barcode in decode(img):
            myData = barcode.data.decode('utf-8')
            item_dic[myData]=[barcode.polygon]
            pts = np.array([barcode.polygon],np.float64)
            pts = pts.reshape((-1,1,2))
            pts2 = barcode.rect
            milli2pixel_factor = ((pts2[2]+pts2[3])/2)/76 # 76 millimeter in real world
            if int(myData) == int(target):
                padd_x = 21*milli2pixel_factor
                padd_y = 9*milli2pixel_factor
                centroid.append(int(pts[1][0][0]+padd_x))
                centroid.append(int(pts[1][0][1]+padd_y))
                if verbose:
                    cv2.circle(img, centroid, radius=5, color=(0, 0, 255), thickness=-1)
                    cv2.imshow('Result',img)
                    cv2.waitKey()
                    cv2.destroyAllWindows
                flag = False
                break
        if verbose:
            cv2.imshow('Result',img)
            cv2.waitKey(1)
    return centroid

def finder_from_image(img, target:str, verbose:bool = False):
    item_dic = {}
    centroid = []
    for barcode in decode(img):
        myData = barcode.data.decode('utf-8')
        item_dic[myData]=[barcode.polygon]
        pts = np.array([barcode.polygon],np.float64)
        pts = pts.reshape((-1,1,2))
        pts2 = barcode.rect
        milli2pixel_factor = ((pts2[2]+pts2[3])/2)/76 # 76 millimeter in real world
        if int(myData) == int(target):
            padd_x = 21*milli2pixel_factor
            padd_y = 9*milli2pixel_factor
            centroid.append(int(pts[1][0][0]+padd_x))
            centroid.append(int(pts[1][0][1]+padd_y))
            if verbose:
                img = cv2.circle(img, centroid, radius=5, color=(0, 0, 255), thickness=-1)
            break
    if verbose:
        cv2.imshow('Result',img)
        cv2.waitKey(0)
        cv2.destroyAllWindows
    return centroid

if __name__ == '__main__':
    (options, args) = parser.parse_args()
    if options.src_img:
        img = cv2.imread(options.src_img)
        centroid = finder_from_image(img, options.target, options.verbose)
    else:
        cap = cv2.VideoCapture(options.vid_id)
        cap.set(3,1920)
        cap.set(4,1080)
        #cap.set(3,640)
        #cap.set(4,480)
        centroid = finder(cap, options.target, options.verbose)
        cap.release()
    print(f'centroid x = {centroid[0]}, y = {centroid[1]}')
