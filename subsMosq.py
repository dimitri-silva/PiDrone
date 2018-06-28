import json
import threading
from MSP import MSP
import MSP_Threadp
import paho.mqtt.client as paho
import memcache


def on_message(mosq, obj, msg):
    msp=MSP()
    print ("%s" % ( msg.payload))
    dict=json.loads(msg.payload)
    if dict["module_type"]=="moveBoat":
        t = threading.Thread(target=RPI.MSP_Thread.MSP_Thread.startFollowing, args=(msp, dict['id']))
        t.start()

    elif dict["module_type"]=="return":
        t = threading.Thread(target=RPI.MSP_Thread.MSP_Thread.stopFollowing, args=())
        t.start()

    elif dict["module_type"] == "moveBuoy":
        t = threading.Thread(target=RPI.MSP_Thread.MSP_Thread.go_to_buoy, args=(msp, dict['id']))
        t.start()

def on_publish(mosq, obj, mid):
    pass

if __name__ == '__main__':
    client = paho.Client()
    client.on_message = on_message
    client.on_publish = on_publish

    #client.tls_set('root.ca', certfile='c1.crt', keyfile='c1.key')
    client.connect("192.168.1.102", 1883, 60)

    client.subscribe("droneCommand", 0)

    while client.loop() == 0:
        pass
