import paho.mqtt.client as paho
import time
from MSP import MSP
import json
from MSP_Thread import getDroneData
import requests
import threading
import time


class droneDataBroker(threading.Thread):

    def on_publish(mosq, userdata, mid):
        # Disconnect after our message has been sent.
        pass

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        client = paho.Client()
        client.connect("127.0.0.1")
        msp = MSP()
        info = {}
        i=74
        while True:
            data = getDroneData(msp)
            info["module_type"]='droneInfo'
            info["type"]="drone"
            info["btl"]=str(i)
            info["status"]="in_flight"
            info["lat"]=data["Lat"]
            info["log"]=data["Long"]
            info["ort"]=data["degree"]
            info["alt"]=data["alt"]
            info["angx"]=data["angx"]
            info["angy"]=data["angy"]
            info["coords"]=(data["Lat"],data["Long"])
            client.publish("droneInfo", json.dumps(info).encode(), 0,retain=True)
            ip="192.168.1.103"
            time.sleep(1)
