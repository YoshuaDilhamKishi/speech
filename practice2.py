import pyaudio
import wave
from datetime import datetime
now = datetime.now()

RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "result.wav" + str(now)
iDeviceIndex = 0

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 2 ** 11
p = pyaudio.PyAudio()

stream = p.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    input_device_index=iDeviceIndex,
                    frames_per_buffer=CHUNK)


print("recording...")
speech = []
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    speech.append(data)
    speech.append(now)

print("finish recording")

stream.stop_stream()
stream.close()
p.terminate()

waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setsampwidth(p.get_sample_size(FORMAT))
waveFile.setnchannels(CHANNELS)
waveFile.setframerate(RATE)
waveFile.writeframes('/'.join(map(str,speech)))
waveFile.close()