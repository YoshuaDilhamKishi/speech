import pyaudio
import sys
import matplotlib.pyplot as plt
import numpy as np

chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 20
WAVE_OUTPUT_FILENAME = "result.wav"

p = pyaudio.PyAudio()

rec = p.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                input = True,
                frames_per_buffer = chunk)

print ("* recording")
all = []
for i in range(0, RATE / chunk * RECORD_SECONDS):
    data = rec.read(chunk)
    all.append(data)
print ("* done recording")

rec.close()
p.terminate()

# write data to WAVE file
data = ''.join(all)
result = np.frombuffer(data,dtype="int16") / float(2**15)

plt.plot(result)
plt.ylim([-1,1])
plt.show()