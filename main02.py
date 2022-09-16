from tkinter import Y
import cv2
from time import sleep
from rich import pretty
from rich.console import Console
from rich.progress import track
from rich.traceback import install
# import UR_Controller
from src.ObjectFinder import ObjectFinder
from src.Client import Client
from src.Queue import Queue
from configs import CalibrateConfig
import UR_Controller_Metamarket
console = Console()
pretty.install()
install()


def main(verbose=False):
    # เชคสถานะเปิดกล้อง
    console.print('\nEstasblishing camera...\n', style='bold cyan')
    # please execute the calibrate.py script first for initialze camera setting
    cap = cv2.VideoCapture(CalibrateConfig.CaptureId + cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CalibrateConfig.CaptureWidth)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CalibrateConfig.CaptureHeight)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    # cap = None
    while not cap.isOpened():
        # loop until can open the camera successfully
        cap = cv2.VideoCapture(CalibrateConfig.CaptureId)
        cap = cv2.VideoCapture(CalibrateConfig.CaptureId + cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, CalibrateConfig.CaptureWidth)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CalibrateConfig.CaptureHeight)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    client = Client()
    finder = ObjectFinder(cap, CalibrateConfig.FocalLength,
            CalibrateConfig.ScaleFactor, CalibrateConfig.ObjectWidth, verbose=verbose)

    # เชคการเชื่อต่อ MQTT
    client.loop_start()
    console.print('\nEstasblishing connection to MQTT Broker\n', style='bold cyan')
    for step in track(range(3)):
        sleep(.1)
    else:
        client.pub({'Status':'','Product':''})
        #client.pub({'Status':'','Meta/Robot':''})
    try:
        while True:
            ret = client.sub(['Product', 'Status'])
            #ret = client.sub(['Meta/Robot', 'Status'])
            #if ret['Meta/Robot'] != None:
            if ret['Product'] != None:
                console.print('\nStatus : Start Working\n', style='bold cyan')
                #client.pub({'Meta/Robot':''})
                client.pub({'Product':''})
                #product_queue = Queue(ret['Meta/Robot'].split(','))
                product_queue = Queue(ret['Product'].split(','))
                while not product_queue.is_empty():
                    client.pub({'Status':'Working'})
                    img = None
                    prod = None
                    while img is None:
                        _, img = cap.read()
                    decoded = finder.decode(img)
                    # print(decoded[0][0])
                    for d in decoded:
                        if product_queue.head() == d.data.decode('utf-8'):
                            prod = product_queue.dequeue()
                            console.print(f'\nCurrent queue: {prod}\n', style='bold cyan')
                            break
                        #if verbose:
                        #    finder.show(drawrect=True, show_size=.4)
                    else:
                        #if verbose:
                        #    console.log(log_locals=True)
                        continue
                    # centroids = finder.centroid(axis='xyz', padding_mm_x=10, padding_mm_y=50)
                    centroids = finder.centroid(axis='xyz', padding_mm_x=0, padding_mm_y=0)
                    centroids_reaxis = dict()
                    
                    for k, v in zip(centroids.keys(), centroids.values()):
                        centroids_reaxis[k] = (
                                -780,
                                (0.823*int(v[0]))-530,
                                (0.823*int((1080-v[1])))-45                               
                                # (0.835*int(v[0]))-554,
                                # (0.835*int((1080-v[1])))-77.8

                                # finder.pixel2mm(v[0]), #+122,
                                # finder.pixel2mm(v[1]) #- 126
                                # CalibrateConfig.CaptureHeight - v[1] + 79
                            )
                    if verbose:
                        #console.print('Meta/Robot : ', centroids_reaxis[prod])
                        console.print('Product : ', centroids_reaxis[prod])
                        x,y,z=centroids_reaxis[prod]
                        #console.log(log_locals=True)

                    # Do command robot here, and wait for it
                    UR_Controller_Metamarket.gripper_open()
                    UR_Controller_Metamarket.path2grip_3product(x,y,z)
                    
                    # Public status back to mqtt server
                    client.pub({'Status':'Done'})
                    console.print('\nStatus : Done Working\n', style='bold cyan')
                    # texts = list(centroids_reaxis.keys())
                    # finder.show(centroids=list(centroids_reaxis.values()), texts=texts, drawrect=True, show_size=.1)
    except KeyboardInterrupt:
        cap.release()
        #client.pub({'Status':'','Meta/Robot':''})
        client.pub({'Status':'','Product':''})
        if verbose:
            console.log(log_locals=True)
    except Exception as e:
        console.log(e)
        if verbose:
            console.log(log_locals=True)
        cap.release()

if __name__ == '__main__':
    main(verbose=True)
