import time

from VideoStream import VideoCapture

cap = VideoCapture('192.168.1.65')
cap.start()

cap.recordLaunch()
time.sleep(10)
cap.stopRecordLaunchAndTransmit()
print("Done")