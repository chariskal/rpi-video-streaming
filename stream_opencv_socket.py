import cv2 as cv
import numpy as np
import socket
import sys
import pickle
import struct



cap=cv.VideoCapture('rtsp://192.168.1.88')
clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientsocket.connect(('10.42.0.1',8089))
while(True):
  try:
    ret, frame = cap.read()
    print("Frame read!")
    frame_resized = cv.resize(frame, (420, 300))
    data = pickle.dumps(frame_resized)
    message_size = struct.pack("=L", len(data)) ### CHANGED
    clientsocket.sendall(message_size + data)
    #if cv.waitKey(1) & 0xFF == ord('q'):
          #break
  except KeyboardInterrupt:
    cap.release()
    cv.destroyAllWindows()
    break

