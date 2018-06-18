import socket
import threading
import time

import numpy
import picamera


class CameraBuffer:
    def __init__(self, sock):
        self.sock = sock

    def write(self, buf):
        self.sock.sendto(buf, self.DEST)


class VideoCapture(threading.Thread):
    # Connect a client socket to my_server:8000 (change my_server to the
    # hostname of your server)
    def __init__(self, dest, group=None, target=None, name=None, verbose=None, port=1000, record=False):
        super().__init__(self, group=group, target=target, name=name,
                         verbose=verbose)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.DEST = (dest, port)
        self.record = record
        self.camera = picamera.PiCamera()
        self.camera.resolution = (1280, 720)
        self.camera.framerate = 15
        self.outputStream = CameraBuffer(self.server_socket)

    def run(self):
        try:
            timestr = time.strftime("%Y%m%d-%H%M%S")
            if self.record:
                self.camera.start_recording('Videos/recording_' + timestr + '.h264', splitter_port=1, format='h264',
                                            bitrate=3000000)
                print('Video Recording Started')
            self.camera.start_recording(self.outputStream, format='h264', splitter_port=2, resize=(854, 480),
                                        bitrate=500000)
            print('Video Stream Started')
            self.camera.wait_recording(100000, splitter_port=2)
        finally:
            if self.record:
                self.camera.stop_recording(splitter_port=1)
            self.camera.stop_recording(splitter_port=2)
            self.server_socket.close()

    def stop(self):
        if self.record:
            self.camera.stop_recording(splitter_port=1)
            print('Video Recording Stopped')
        self.camera.stop_recording(splitter_port=2)
        print('Video Stream Stopped')

    def readFrame(self):
        image = numpy.empty((720 * 1280 * 3,), dtype=numpy.uint8)
        self.camera.capture(image, 'rgb', splitter_port=0)
        return image
