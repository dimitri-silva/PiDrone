import logging
import socket
from math import radians
import paho.mqtt.client as paho
import requests
from MSP_Thread import getDroneData
from flask import json
import converter
import memcache
from MSP import MSP

ip = str(socket.gethostbyname(socket.gethostname()))


log = logging.getLogger('udp_server')


def udp_server(host='192.168.1.102', port=8182):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    log.info("Listening on udp %s:%s" % (host, port))
    s.bind((host, port))
    while True:
        (data, addr) = s.recvfrom(128*1024)
        yield data


FORMAT_CONS = '%(asctime)s %(name)-12s %(levelname)8s\t%(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT_CONS)


def on_publish(mosq, userdata, mid):
    # Disconnect after our message has been sent.
    mosq.disconnect()


def runServer():
    dic={}
    client = paho.Client()
    client.on_publish = on_publish
    ids={}
    mc = memcache.Client(['127.0.0.1:11211'], debug=0)
    data={}
    count=0
    for data in udp_server():
        modules = {}
        values = data.decode("utf-8")
        d = json.loads(values)
        lst= []
        if d['deviceId'] not in ids:
            count+=1
            ids[d['deviceId']]=count

        modules['id'] = ids[d['deviceId']]
        modules['deviceId'] = d['deviceId']
        modules['type'] = d['type']
        modules['degree'] = 10
        lst.append(d['Long'])
        lst.append(d['Lat'])
        modules['coords'] = lst
        client.connect("127.0.0.1")
        client.publish("id", json.dumps(modules).encode(), 0)
        if d['type']=='boat':
            dic[ids[d['deviceId']]] = (d['Lat'],d['Long'])
        mc.set("data",dic)
