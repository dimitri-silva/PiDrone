import json
import request
import paho.mqtt.client as paho
from VideoStream import VideoCapture


import threading
import memcache
import time
import json
class Video(threading.Thread):

    def __init__(self, on_message, on_publish):
        threading.Thread.__init__(self)
        self.on_message = on_message
        self.on_publish = on_publish

    def run(self):
        print('hi')
        clientVideo = paho.Client()
        clientVideo.on_message = self.on_message
        clientVideo.on_publish = self.on_publish
        clientVideo.connect("192.168.1.102", 1883, 60)
        clientVideo.subscribe("videoRecord", 0)
        while clientVideo.loop() == 0:
            pass

class Drone(threading.Thread):

    def __init__(self, on_message, on_publish):
        threading.Thread.__init__(self)
        self.on_message = on_message
        self.on_publish = on_publish

    def run(self):
        print('hi')
        clientVideo = paho.Client()
        clientVideo.on_message = self.on_message
        clientVideo.on_publish = self.on_publish
        clientVideo.connect("192.168.1.102", 1883, 60)
        clientVideo.subscribe("droneCommand", 0)
        while clientVideo.loop() == 0:
            pass


GS_IP = None
cap = None
def on_message_video(mosq, obj, msg):
        print ("%s" % ( msg.payload))
        print('im mosquito')
        code=msg.payload.decode("utf-8")
        print("got new messaage")
        if code=="start":
            print("started video")
            cap.recordLaunch()
        elif code=="stop":
            print("stopping video")
            print("Stopping Recording")
            cap.stopRecordLaunchAndTransmit()
            print("Done")
            
def on_publish(mosq, obj, mid):
        pass

def on_message_drone(mosq,obj,msg):
    print ("%s" % ( msg.payload))
    print('im mosquito')
    dict=json.loads(msg.payload.decode("utf-8"))
    print("got new messaage")
    if dict["module_type"]=="move":
        print("going")
        #request.startFollowing(1,15000)

    elif dict["module_type"]=="return":
        print("stopping")



if __name__ == '__main__':
    GS_IP = '192.168.1.65'
    cap = VideoCapture(GS_IP)
    cap.start()    
    video = Video(on_message_video, on_publish)
    video.start()
    drone = Drone(on_message_drone, on_publish)
    drone.start()
    
