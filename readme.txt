(meta_) C:\Users\bunth\OneDrive\Desktop\fra631\meta\TwinRobotInterface>python calibrate.py --help
Usage: calibrate.py [options]

Options:
  -h, --help            show this help message and exit
  -v VID_ID, --video-device=VID_ID
                        Id of video capture
  -w OBJ_W, --object-width=OBJ_W
                        Width of object in realword size (mm)
  -d DISTANCE, --distance=DISTANCE
                        Distance between camera and object (mm)
  -s SRC_IMG, --source-image=SRC_IMG
                        A relative path to pre-capture image that use for
                        calibrate process
  -r RESIZE, --resize-preview=RESIZE
                        Resize preview image
  --cap-width=CAP_W     Width of capture frame (pixel)
  --cap-height=CAP_H    height of capture frame (pixel)
  --verbose             Show image

python calibrate.py -v 1 -w 76 -d 960 -r 0.4 --cap-width 2304 --cap-height 1296 --verbose

got config file in configs/calibrate.conf

