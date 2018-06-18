import socket
import threading
import time
import ffmpy
import numpy
import picamera


class CameraBuffer:
    def __init__(self, sock, DEST):
        self.sock = sock
        self.DEST = DEST

    def write(self, buf):
        self.sock.sendto(buf, self.DEST)


class VideoCapture(threading.Thread):
    # Connect a client socket to my_server:8000 (change my_server to the
    # hostname of your server)
    def __init__(self, dest, group=None, target=None, name=None, verbose=None, port=1000, record=False):
        super().__init__(group=group, target=target, name=name)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.DEST = (dest, port)
        self.record = record
        self.camera = picamera.PiCamera()
        self.camera.resolution = (1280, 720)
        self.camera.framerate = 15
        self.outputStream = CameraBuffer(self.server_socket, self.DEST)

    def run(self):
        try:
            timestr = time.strftime("%Y%m%d-%H%M%S")
            if self.record:
                self.camera.start_recording('recording_' + timestr + '.h264', splitter_port=1, format='h264',
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

    def recordLaunch(self):
        self.camera.start_recording('launch.h264', splitter_port=3, format='h264',
                                    bitrate=3000000)

    def stopRecordLaunchAndTransmit(self):
        self.camera.stop_recording(splitter_port=3)
        ff = ffmpy.FFmpeg(global_options='-framerate 15 -y',
                          inputs={'launch.h264': None},
                          outputs={'launch.mp4': '-c:v copy -f mp4'})
        ff.run()
        self.sendFile('launch.mp4')

    def sendFile(self, name):
        s = socket.socket()
        s.bind(('0.0.0.0', 50000))
        s.listen(5)

        conn, addr = s.accept()  # Establish connection with client.
        f = open(name, 'rb')
        l = f.read(1024)
        while (l):
            conn.send(l)
            l = f.read(1024)
        f.close()
        conn.close()