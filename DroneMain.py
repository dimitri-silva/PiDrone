import json
import request
import paho.mqtt.client as paho
from VideoStream import VideoCapture

import threading
import memcache
import time
import json

#
# Global variables
#
videoRequestTopic = 'videoRequest/+'  # Request comes in here. Note wildcard.
videoResponseTopic = 'videoReply/'  # Response goes here. Request ID will be appended later

GS_IP = '192.168.1.65'
cap = None


#
# Callback that is executed when the client receives a CONNACK response from the server.
#
def onConnectVideo(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(videoRequestTopic, 0)  # topic, QoS


#
# Callback that is executed when a message is received.
#
def onMessageVideo(client, userdata, message):
    requestTopic = message.topic
    requestID = requestTopic.split('/')[1]  # obtain requestID as last field from the topic

    print("Received a request on topic " + requestTopic + ".")

    code = message.payload.decode("utf-8")
    print("got new messaage")
    if code == "start":
        print("started video")
        cap.recordLaunch()
    elif code == "stop":
        print("Stopping Recording")
        cap.stopRecordLaunchAndTransmit()
        print("Done")
    elif code == "videos":
        vidList = cap.listVideos()
        print('Sending vidList ' + str(vidList))
        client.publish((requestTopic + requestID), payload=vidList, qos=0, retain=False)


#
# Callback that is executed when we disconnect from the broker.
#
def onDisconnect(client, userdata, message):
    print("Disconnected from the broker.")


class VideoThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print('hi')
        clientVideo = paho.Client(client_id='raspberrypi', clean_session=True)

        clientVideo.on_connect = onConnectVideo
        clientVideo.on_message = onMessageVideo
        clientVideo.on_disconnect = onDisconnect

        clientVideo.connect("192.168.1.102", 1883, 60)
        clientVideo.subscribe("videoRequest", 0)
        clientVideo.loop_forever()


if __name__ == '__main__':
    GS_IP = '192.168.1.65'
    cap = VideoCapture(GS_IP)
    cap.start()
    video = VideoThread()
    video.start()
