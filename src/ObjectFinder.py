import numpy as np
import cv2
import tkinter as tk
from pyzbar.pyzbar import decode
from math import sqrt
from rich.console import Console

console = Console()

class ObjectFinder:
    def __init__(self, capture, focal_length, scale_factor, object_width, verbose=False) -> None:
        self.__capture = capture
        self.__focal_length = focal_length
        self.__scale_factor = scale_factor
        self.__object_width = object_width
        self.__verbose = verbose
        self.__decoded = []
        self.__img = None

    def mm2pixel(self, x):
        return abs(x*self.__scale_factor)

    def pixel2mm(self, x):
        return x/self.__scale_factor

    def decode(self, img):
        self.__img = img
        self.__decoded = decode(self.__preprocess_img(img))
        return self.__decoded

    def scan(self):
        img = None
        while img is None:
            _, img = self.__capture.read()
        self.__img = img
        img = self.__preprocess_img(img)
        self.__decoded = decode(img)
        if self.__verbose:
            console.log(self.__decoded)
        return self

    def centroid(self, *, axis:str='xyz', padding_mm_x:int=0, padding_mm_y:int=0):
        # padding has a reference point at top right of the qr code, return coordinates in pixel unit
        founds = {}
        if not self.__decoded:
            self.scan()
        if len(self.__decoded) != 0:
            for d in self.__decoded:
                pts = d.polygon
                data = d.data.decode('utf-8')
                # pth = abs(pts[2].y - pts[0].y) # most case it work fine but some block has weird point placements
                # ptw = abs(pts[1].x - pts[0].x)
                ptx = d.rect[0]
                pty = d.rect[1]
                ptw = d.rect[2]
                pth = d.rect[3]
                flip_direction = 1 if d.orientation == 'UP' else -1 
                #console.log(pts, pth, ptw)
                if padding_mm_x == 0 and padding_mm_y == 0:
                    # x = pts[0].x + (pth+ptw)/4
                    # y = pts[0].y - (pth+ptw)/4
                    x = ptx + (pth+ptw)/4
                    y = pty + (pth+ptw)/4
                else:
                    # x = pts[0].x + (pth+ptw)/4 - padding_mm_x*self.__scale_factor
                    # y = pts[0].y - (pth+ptw)/4 + padding_mm_y*self.__scale_factor
                    x = ptx + (pth+ptw)/4 - flip_direction*padding_mm_x*self.__scale_factor
                    y = pty + (pth+ptw)/4 + flip_direction*padding_mm_y*self.__scale_factor
                z = self.mm2pixel(self.__distance((pth+ptw)/2))
                coor = []
                for c in axis:
                    if c == 'x':
                        coor.append(int(x))
                    if c == 'y':
                        coor.append(int(y))
                    if c == 'z':
                        coor.append(int(z))
                founds[data] = tuple(coor)
            return founds
        else:
            return founds

    def __distance(self, img_width:int) -> float:
        return self.__focal_length*self.__object_width/img_width

    def distance(self):
        # return distance from camera to object in mm unit
        founds = {}
        if not self.__decoded:
            self.scan()
        if len(self.__decoded) != 0:
            for d in self.__decoded:
                # pts = d.polygon
                data = d.data.decode('utf-8')
                ptw = d.rect[2]
                pth = d.rect[3]
                # pth = abs(pts[2].y - pts[0].y)
                # ptw = abs(pts[1].x - pts[0].x)
                distance = self.__distance((pth+ptw)/2)
                founds[data] = distance
            return founds
        else:
            return founds

    def __resize_area_factor(self, img, area:float=.25):
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

    def __apply_brightness_contrast(self, img, brightness = 0, contrast = 0):
        if brightness != 0:
            if brightness > 0:
                shadow = brightness
                highlight = 255
            else:
                shadow = 0
                highlight = 255 + brightness
            alpha_b = (highlight - shadow)/255
            gamma_b = shadow
            buf = cv2.addWeighted(img, alpha_b, img, 0, gamma_b)
        else:
            buf = img.copy()
        if contrast != 0:
            f = 131*(contrast + 127)/(127*(131-contrast))
            alpha_c = f
            gamma_c = 127*(1-f)
            buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)
        return buf

    def __preprocess_img(self, img):
        # img = self.__apply_brightness_contrast(img, 0, 3)
        alpha = 1.0 # Contrast control (1.0-3.0)
        beta = 30 # Brightness control (0-100)
        kernel = np.array([[0, -1, 0],
                          [-1, 5,-1],
                          [0, -1, 0]])

        #img = cv2.GaussianBlur(img, (3, 3), 0)
        # img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # img = cv2.equalizeHist(img)
        # img = cv2.filter2D(src=img, ddepth=-1, kernel=kernel)
        # img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return img

    def show(self, *, centroids=[], texts=[], drawrect=False, show_size=.25):
        if len(centroids) != 0 and len(texts) != 0 and len(centroids) != len(texts):
            raise ValueError('Number of centroid not equal to number of text')
        if self.__img is None:
            raise ValueError('Image not found please do scan() to acquire image data first')
        show_img = self.__img
        if drawrect:
            if self.__decoded:
                for d in self.__decoded:
                    pts = d.polygon
                    show_img = cv2.rectangle(show_img, (pts[0].x, pts[0].y), (pts[2].x, pts[2].y), color=(0, 0, 255), thickness=2)
        for idx, c in enumerate(centroids):
            show_img = cv2.circle(show_img, (c[0], c[1]), radius=5, color=(0, 0, 255), thickness=-1)
            if texts:
                show_img = cv2.putText(
                        show_img, texts[idx], (c[0], c[1]),
                        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=1, color=(0, 0, 255))
        scaling_factor = self.__resize_area_factor(show_img, area=show_size)
        show_img = cv2.resize(show_img, (0, 0), fx=scaling_factor, fy=scaling_factor)
        cv2.imshow('Camera frame (press any key to exit)', show_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows
