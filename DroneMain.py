import time

from VideoStream import VideoCapture

cap = VideoCapture('192.168.1.65')
cap.start()

time.sleep(10)
print(cap.readFrame())