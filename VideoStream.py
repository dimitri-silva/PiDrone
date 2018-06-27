import socket
import threading
import time
import ffmpy
import numpy
import picamera
from click import File
import os


class CameraBuffer:
    def __init__(self, sock, DEST):
        self.sock = sock
        self.DEST = DEST

    def write(self, buf):
        self.sock.sendto(buf, self.DEST)


class VideoCapture(threading.Thread):
    # Connect a client socket to my_server:8000 (change my_server to the
    # hostname of your server)
    def __init__(self, dest, group=None, target=None, name=None, verbose=None, port=1000):
        super().__init__(group=group, target=target, name=name)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.DEST = (dest, port)
        self.recording = False
        self.recordingLaunch = False
        self.launchName = None
        self.camera = picamera.PiCamera()
        self.camera.resolution = (1280, 720)
        self.camera.framerate = 15
        self.outputStream = CameraBuffer(self.server_socket, self.DEST)

    def run(self):
        try:
            self.camera.start_recording(self.outputStream, format='h264', splitter_port=2, resize=(854, 480),
                                        bitrate=500000)
            print('Video Stream Started')
            self.camera.wait_recording(1000000, splitter_port=2)
        finally:
            if self.recording:
                self.camera.stop_recording(splitter_port=1)
            if self.recordingLaunch:
                self.camera.stop_recording(splitter_port=3)
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

    def record(self, name):
        if not self.recording:
            self.camera.start_recording("Videos/" + name + '.h264', splitter_port=1, format='h264',
                                        bitrate=3000000)
            self.recording = True
            return True
        return False

    def stopRecord(self):
        if self.recording:
            self.camera.stop_recording(splitter_port=1)
            self.recording = False
            return True
        return False

    def recordLaunch(self, name):
        if not self.recordingLaunch:
            self.camera.start_recording(name + '.h264', splitter_port=3, format='h264',
                                        bitrate=5000000)
            self.launchName = name
            self.recordingLaunch = True
            return True
        return False

    def stopRecordLaunch(self):
        if self.recordingLaunch:
            self.camera.stop_recording(splitter_port=3)
            self.processVideo(self.launchName)
            name = self.launchName
            self.launchName = None
            self.recordingLaunch = False
            return name
        return None

    def sendFile(self, name):
        t = threading.Thread(target=self.sendFileAssist, args=(name,))
        t.start()

    def sendFileAssist(self, name):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 30000))
        s.listen(0)
        conn, addr = s.accept()  # Establish connection with client.
        print('conn')
        f = open(name, 'rb')
        l = f.read(1024)
        while (l):
            conn.send(l)
            l = f.read(1024)
        f.close()
        conn.close()
        s.shutdown(2)
        s.close()
        print('done')

    def listVideos(self):
        list_videos = []
        path_videos = 'Videos/'
        videos = os.listdir(path_videos)
        for video_file in videos[:]:
            if not (video_file.endswith(".h264")):
                videos.remove(video_file)
            else:
                list_videos.append(
                    File("NAME", path_videos + video_file,
                         time.ctime(os.path.getctime(path_videos + video_file))))
        json_videos = '['
        for i, file in enumerate(list_videos):
            s = len(list_videos) - 1
            json_videos += '{"name": "' + file.name + '"}'
            if i != s:
                json_videos += ','
        json_videos += ']'
        return json_videos

    def processVideo(self, name):
        ff = ffmpy.FFmpeg(global_options='-framerate 15 -y',
                          inputs={name + '.h264': None},
                          outputs={name + '.mp4': '-c:v copy -f mp4'})
        ff.run()
