import paho.mqtt.client as paho
from VideoStream import VideoCapture
import MSP_Thread
import threading
import json
import UdpServer
import UdpController
import memcache
from droneDataBroker import droneDataBroker


class Video(threading.Thread):
    def __init__(self, on_message, on_publish):
        threading.Thread.__init__(self)
        self.on_message = on_message
        self.on_publish = on_publish

    def run(self):
        print('Starting broker client')
        clientVideo = paho.Client()
        clientVideo.on_message = self.on_message
        clientVideo.on_publish = self.on_publish
        clientVideo.connect("192.168.1.102", 1883, 60)
        clientVideo.subscribe("videoRequest", 0)
        print(cap.listVideos())
        sendStorageData(clientVideo)
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
    print("Message")
    dict = json.loads(msg.payload.decode("utf-8"))
    print("Received new message on video topic: " + str(dict))
    if dict["type"] == "start_recording_launch":
        if cap.recordLaunch(dict["name"]):
            print("Launch Recording Started")
        else:
            print("Launch Recording is already running")
    elif dict["type"] == "stop_recording_launch":
        name = cap.stopRecordLaunch()
        if name:
            mosq.publish("GS_TOPIC", payload='{"type": "launch_ready_for_transmit", "name": "' + name + '"}', qos=2,
                         retain=True)
            cap.sendFile(name + '.mp4')
            print("Launch Recording Stopped")
        else:
            print("Launch Recording already stopped")
    elif dict["type"] == "start_recording_main":
        if cap.record(dict['name']):
            print("Main Recording Started")
        else:
            print("Main Recording is already running")
    elif dict["type"] == "stop_recording_main":
        if cap.stopRecord():
            sendStorageData(mosq)
            print("Main Recording Stopped")
        else:
            print("Main Recording is already stopped")
    elif dict["type"] == "process_video":
        print("Processing video file" + dict['name'])
        cap.processVideo(dict['name'])
        mosq.publish("GS_TOPIC", payload='{"type": "video_ready_for_transmit", "name": "' + dict['name'] + '"}', qos=2,
                     retain=True)
        print("Sending video file")
        cap.sendFile('Processing/' + dict['name'] + '.mp4')
        sendStorageData(mosq)


def sendStorageData(mosq):
    out = cap.listVideos()
    mosq.publish("GS_TOPIC",
                 payload='{"type": "video_list_updated", "list":' + str(out[0]) + ', "storage":' + str(
                     out[1]) + '}',
                 qos=2,
                 retain=True)


def on_publish(mosq, obj, mid):
    pass


def on_message_drone(mosq, obj, msg):
    dict=json.loads(msg.payload)
    if dict["type"] == "calibration":
        calib = dict["calib"]
        mc = memcache.Client(['127.0.0.1:11211'], debug=0)
        mc.set("calibration", calib)
        return
    msp=MSP()
    if dict["type"]=="moveBoat":
        t = threading.Thread(target=RPI.MSP_Thread.MSP_Thread.startFollowing, args=(msp, dict['id']))
        t.start()

    elif dict["type"]=="return":
        t = threading.Thread(target=RPI.MSP_Thread.MSP_Thread.stopFollowing, args=())
        t.start()

    elif dict["type"] == "moveBuoy":
        t = threading.Thread(target=RPI.MSP_Thread.MSP_Thread.go_to_buoy, args=(msp, dict['id']))
        t.start()




class ControllerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
       UdpController.udp_server()

class UDPServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
       UdpServer.runServer()


if __name__ == '__main__':

    #MSP_Thread.start_sending()
    #controller = ControllerThread()
    #controller.start()
    server = UDPServerThread()
    server.start()
    print('██▓███   ██▓▓█████▄  ██▀███   ▒█████   ███▄    █ ▓█████\n▓██░  ██▒▓██▒▒██▀ ██▌▓██ ▒ ██▒▒██▒  ██▒ ██ ▀█   █ ▓█   ▀\n▓██░ ██▓▒▒██▒░██   █▌▓██ ░▄█ ▒▒██░  ██▒▓██  ▀█ ██▒▒███\n▒██▄█▓▒ ▒░██░░▓█▄   ▌▒██▀▀█▄  ▒██   ██░▓██▒  ▐▌██▒▒▓█  ▄\n▒██▒ ░  ░░██░░▒████▓ ░██▓ ▒██▒░ ████▓▒░▒██░   ▓██░░▒████▒\n▒▓▒░ ░  ░░▓   ▒▒▓  ▒ ░ ▒▓ ░▒▓░░ ▒░▒░▒░ ░ ▒░   ▒ ▒ ░░ ▒░ ░\n░▒ ░      ▒ ░ ░ ▒  ▒   ░▒ ░ ▒░  ░ ▒ ▒░ ░ ░░   ░ ▒░ ░ ░  ░\n░░        ▒ ░ ░ ░  ░   ░░   ░ ░ ░ ░ ▒     ░   ░ ░    ░\n░     ░       ░         ░ ░           ░    ░  ░\n░')
    GS_IP = '192.168.1.124'
    cap = VideoCapture(GS_IP)
    cap.start()
    video = Video(on_message_video, on_publish)
    video.start()
    drone = Drone(on_message_drone, on_publish)
    drone.start()
    droneBroker = droneDataBroker()
    droneBroker.start()
