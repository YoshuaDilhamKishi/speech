import os
import sys
import atexit
import json
import time
import tempfile
import wave
import traceback
import urllib3
from subprocess import check_output
from Queue import Queue, Empty
import pyaudio
import numpy as np

class Spectrum(object):

    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    FRAME_SIZE = 512
    RATE = 16000

    def frames(self, n):
        return int(n*self.RATE/self.FRAME_SIZE)

    def __init__(self):
        self.speak = Queue()
        self.pa = pyaudio.PyAudio()
        self.last_samples = None
        atexit.register(self.pa.terminate)
        self.begin = self.FRAME_SIZE*3/8
        self.end = self.FRAME_SIZE/2
        self.fque = np.zeros((self.frames(1.0), self.end-self.begin), np.float32)
        self.buff = np.zeros((self.frames(5.0), 512), np.float32)

    def fft(self, samples):
        win = np.hanning(len(samples))
        res = np.fft.fftshift(np.fft.fft(win*samples))
        return 20*np.log10(np.abs(res))

    def callback(self, in_data, frame_count, time_info, status):
        try:
            data = np.fromstring(in_data, np.float32)
            self.buff[0] = data
            self.buff = np.roll(self.buff, -1, axis=0)
            if self.status == 0:
                self.fque = np.roll(self.fque, 1, axis=0)
            self.fque[0] = self.fft(data)[self.begin:self.end]
            average = np.average(self.fque, axis=0)
            values = self.fque[0] - average
            volume = np.average(values)
            if self.status:
                self.count += 1
            else:
                self.count = 0
            if self.status < 5:
                if volume>5:
                    self.status += 1
                else:
                    self.status = 0
            elif self.status == 5:
                if volume<5:
                    self.status += 1
            elif self.status < 15:
                if volume<5:
                    self.status += 1
                else:
                    self.status -= 1
            else:
                self.status = 0
                self.speak.put(self.buff[-self.count-2:])
            if self.debug:
                pr = [min(9, max(0, int(v/10))) for v in values]
                print (''.join([str(i) for i in pr]), self.status)

            return (in_data, self.recording)
        except KeyboardInterrupt:
            self.recording = pyaudio.paAbort

    def start(self, debug=False):
        self.debug = debug
        self.status = 0
        self.count = 0
        self.recording = pyaudio.paContinue
        self.stream = self.pa.open(format = self.FORMAT,
                        channels = self.CHANNELS,
                        rate = self.RATE,
                        input = True,
                        output = False,
                        frames_per_buffer = self.FRAME_SIZE,
                        stream_callback = self.callback)
        self.stream.start_stream()

    def stop(self):
        self.recording = pyaudio.paAbort
        while self.stream.is_active():
            time.sleep(0.5)
        self.stream.start_stream()
        self.stream.close()


RECOGNIZE_URL = "https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang=ja-JP"
FLAC_TOOL = 'flac'

def recognize(fpath):
    flac = open(fpath,"rb").read()
    header = {'Content-Type' : 'audio/x-flac; rate=16000'}
    req = urllib2.Request(RECOGNIZE_URL, flac, header)
    data = urllib2.urlopen(req)
    params = json.loads(data.read())
    return params

def main(spe):
    while 1:
        try:
            buff = spe.speak.get(timeout=3)
            with tempfile.NamedTemporaryFile(suffix='.wav') as fp:
                f = wave.open(fp, 'w')
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(16000)
                f.writeframes(np.int16(buff*32768).tostring())
                f.close()
                check_output([FLAC_TOOL, '-sf', fp.name])
                output = os.path.splitext(fp.name)[0] + '.flac'
                res = recognize(output)
                for i in res.get('hypotheses', []):
                    print (i['confidence'], i['utterance'])
        except KeyboardInterrupt:
            raise SystemExit(0)
        except Empty:
            pass
        except:
            traceback.print_exc()
            time.sleep(5)

if __name__ == '__main__':
    spe = Spectrum()
    spe.start(False)
    try:
        main(spe)
    finally:
        spe.stop()