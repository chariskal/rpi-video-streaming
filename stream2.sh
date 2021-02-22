#!/bin/bash
sudo python /home/pi/Documents/connect.py
#ffmpeg -i rtsp://192.168.1.88 -s 480x320 -pix_fmt yuv420p -vcodec copy -r 15 -f flv rtmp://62.74.232.210:9000/live/stream
sudo python3 /home/pi/Documents/run_command.py &
