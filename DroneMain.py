import time

from VideoStream import VideoCapture


GS_IP = '192.168.1.65'
cap = VideoCapture(GS_IP)
cap.start()

cap.recordLaunch()
time.sleep(10)
print("Stopping Recording")
cap.stopRecordLaunchAndTransmit()
print("Done")