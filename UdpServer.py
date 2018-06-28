import logging
import socket
from math import radians
import paho.mqtt.client as paho
import requests
from MSP_Thread import getDroneData
from flask import json
import converter
from MSP import MSP

ip = str(socket.gethostbyname(socket.gethostname()))

def publish_on_rest(dic):
    x = '{ "type": "FeatureCollection", "features":['
    for i, key in enumerate(dic.keys()):
        s = len(dic) - 1
        x += str(json.dumps(dic[key]))
        if i != s:
            x += ','
    x += ']}'
    try:
        r = requests.post('http://'+ip+':5000/produce', x)
    except requests.exceptions.RequestException as e:
        log.info("Rest API not Available. Reason: " + e)

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
    cont = 0
    dic={}
    dict = {}
    host = "192.168.1.102"
    port = 2000
    msp=MSP()
    # Specifying a client id here could lead to collisions if you have multiple
    # clients sending. Either generate a random id, or use:
    # client = mosquitto.Mosquitto()
    client = paho.Client()
    client.on_publish = on_publish
    ids={}
    count=0
    for data in udp_server():
        modules = {}
        values = data.decode("utf-8")
        d = json.loads(values)
        lst= []
        print('i got data')
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

        #s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #s.connect((host, port))
        print('before drone data')
        #data = getDroneData(msp)
        print('data',data)
        #data['Lat']=d['Lat']
        #data['Long']=d['Long']
        #if data["alt"]<=5:
        #    data["alt"]=15
        #result=converter.getCanvasPosition((data["Lat"],data["Long"]),(d["Lat"],d["Long"]),-data["degree"],data["alt"],[radians(data["angx"]),radians(data["angy"])])
        #print('result ', result)
        #idMap={"id":ids[d['deviceId']],"result":result}
        #idMap=(ids[d['deviceId']],result)
        print('before connect')
        client.connect("127.0.0.1")
        print('values :', values)
        print('data : ', data)
        client.publish("id", json.dumps(modules).encode(), 0)
        #s.send(json.dumps(data).encode())
        dic[d['deviceId']] = modules
        print('final',dic)
	#publish_on_rest(dic)
