import cv2
import numpy as np
import sys
import struct
from datetime import datetime
timestamp = str(datetime.now())
timestamp = timestamp.replace(".", "")
timestamp = timestamp[0:16]
name = '/home/pi/Videos/vid' + timestamp.replace(" ", "_") + '.avi'
print(name)
cap = cv2.VideoCapture('rtsp://192.168.1.88')
fps = 24
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

cnt = 0
duration = fps*30
out = cv2.VideoWriter(name, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 24, (420, 300))

while(cnt < duration):
  try:
    ret, frame = cap.read()
    frame_resized = cv2.resize(frame, (420, 300))
    out.write(frame_resized)
    cv2.imshow('frame', frame_resized)
    cv2.waitKey(1)
    
    cnt = cnt + 1
  except KeyboardInterrupt:
    cap.release()
    cv2.destroyAllWindows()
    out.release()
    break

