import os, cv2
import tkinter as tk
from math import sqrt
from pyzbar.pyzbar import decode
from optparse import OptionParser
from typing import Tuple
from rich.console import Console

console = Console()
parser = OptionParser()

parser.add_option('-v', '--video-device', dest='vid_id', help='Id of video capture', type='int', default=0)
parser.add_option('-w', '--object-width', dest='obj_w', help='Width of object in realword size (mm)', type='int', default=0)
parser.add_option('-d', '--distance', dest='distance', help='Distance between camera and object (mm)', type='int', default=0)
parser.add_option('-s', '--source-image', dest='src_img', help='A relative path to pre-capture image that use for calibrate process', default='')
parser.add_option('-r', '--resize-preview', dest='resize', help='Resize preview image', type='float', default=.8)
parser.add_option('--cap-width', dest='cap_w', help='Width of capture frame (pixel)', type='int', default=640)
parser.add_option('--cap-height', dest='cap_h', help='height of capture frame (pixel)', type='int', default=480)
parser.add_option('--verbose', dest='verbose', help='Show image', action='store_true', default=False)

def resize_area_factor(img, area:float=.25):
    h, w = img.shape[:2]
    root = tk.Tk()
    screen_h = root.winfo_screenheight()
    screen_w = root.winfo_screenwidth()
    scaling_factor = 1
    if area != 0.0:
        vector = sqrt(area)
        window_h = screen_h * vector
        window_w = screen_w * vector
    else:
        return scaling_factor
    if h > window_h or w > window_w:
        if h / window_h >= w / window_w:
            scaling_factor = window_h / h
        else:
            scaling_factor =  window_w / w
    return scaling_factor
 
def calibrate(
        capture, 
        object_width:int, 
        distance:int, 
        resize_factor:float = 0, 
        verbose:bool = False) -> Tuple[float, float]:
    # Calibrate camera with QR Code
    focal_length, scale_factor = 0, 0
    if isinstance(capture, cv2.VideoCapture):
        while True:
            _, img = capture.read()
            decoded = decode(img)
            if len(decoded) != 0:
                d = decoded[0] # just select one of them is enough
                pts = d.polygon
                ptw = d.rect[2]
                pth = d.rect[3]
                # pth = abs(pts[2].y - pts[0].y)
                # ptw = abs(pts[1].x - pts[0].x)
                scale_factor = ((pth+ptw)/2)/object_width # assume both size of qr code are equal
                focal_length = distance*scale_factor
                draw_border_img = cv2.rectangle(img, (pts[0].x, pts[0].y), (pts[2].x, pts[2].y), color=(0, 0, 255), thickness=2)
                scaling_factor = resize_area_factor(draw_border_img, area=resize_factor)
                draw_border_img = cv2.resize(draw_border_img, (0, 0), fx=scaling_factor, fy=scaling_factor)
                cv2.imshow('Camera frame (press q to confirm border)', draw_border_img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cv2.destroyAllWindows
                    if verbose:
                        console.log(log_locals=True)
                    return focal_length, scale_factor
            else:
                scaling_factor = resize_area_factor(img, area=resize_factor)
                img = cv2.resize(img, (0, 0), fx=scaling_factor, fy=scaling_factor)
                cv2.imshow('Camera frame (press q to confirm border)', img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cv2.destroyAllWindows
                    if verbose:
                        console.log(log_locals=True)
                    return focal_length, scale_factor
    else:
        img = capture
        decoded = decode(img)
        if len(decoded) != 0:
            d = decoded[0] # just select one of them is enough
            pts = d.polygon
            ptw = d.rect[2]
            pth = d.rect[3]
            # pth = abs(pts[2].y - pts[0].y)
            # ptw = abs(pts[1].x - pts[0].x)
            scale_factor = ((pth+ptw)/2)/object_width # assume both size of qr code are equal
            focal_length = distance*scale_factor
            draw_border_img = cv2.rectangle(img, (pts[0].x, pts[0].y), (pts[2].x, pts[2].y), color=(0, 0, 255), thickness=2)
            scaling_factor = resize_area_factor(draw_border_img, area=resize_factor)
            draw_border_img = cv2.resize(draw_border_img, (0, 0), fx=scaling_factor, fy=scaling_factor)
            cv2.imshow('Camera frame (press q to confirm border)', draw_border_img)
            if cv2.waitKey(0) & 0xFF == ord('q'):
                cv2.destroyAllWindows
                if verbose:
                    console.log(log_locals=True)
                return focal_length, scale_factor

if __name__ == '__main__':
    (options, args) = parser.parse_args()
    cap_w = options.cap_w
    cap_h = options.cap_h
    focal_length, scale_factor, img = 0, 0, None
    if options.obj_w == 0 or options.distance == 0:
        raise ValueError('Option --object-width and --distance must be specify.')
    if options.src_img:
        if not os.path.exists(options.src_img):
            raise IOError('Can\'t open image from given source')
        img = cv2.imread(options.src_img)
        cap_w = img.shape[1]
        cap_h = img.shape[0]
        focal_length, scale_factor = calibrate(img, options.obj_w, options.distance, options.resize,options.verbose)
    else:
        cap = cv2.VideoCapture(options.vid_id + cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, cap_w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_h)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        if not cap.isOpened():
            raise IOError('Cannot open camera')
        focal_length, scale_factor = calibrate(cap, options.obj_w, options.distance, options.resize, options.verbose)
        cap.release()
    print(focal_length, scale_factor)
    template = f'''
        FOCAL_LENGTH={focal_length}\n
        SCALE_FACTOR={scale_factor}\n
        OBJECT_WIDTH={options.obj_w}\n
        CAPTURE_WIDTH={cap_w}\n
        CAPTURE_HEIGHT={cap_h}\n
        CAPTURE_ID={options.vid_id}\n
    '''
    if options.verbose:
        console.log(log_locals=True)
        print(template)
    if not os.path.exists('./configs'):
        os.mkdir('./configs')
    with open('./configs/calibrate.conf', 'w') as f:
        f.write(template.replace(' ',''))
