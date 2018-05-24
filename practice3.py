import pyaudio
import wave
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

now = datetime.now()

RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "result.wav"
iDeviceIndex = 0
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 11025
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


def main():
    N = 256
    dt = 0.01
    f1, f2 = 10, 20
    t = np.arange(0, N * dt, dt)
    freq = np.linspace(0, 1.0 / dt, N)

    f = np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t) + 0.3 * np.random.randn(N)


    F = np.fft.fft(f)

    Amp = np.abs(F)

    plt.figure()
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 17
    plt.subplot(121)
    plt.plot(t, f, label='f(n)')
    plt.xlabel("Time", fontsize=20)
    plt.ylabel("Signal", fontsize=20)
    plt.grid()
    leg = plt.legend(loc=1, fontsize=25)
    leg.get_frame().set_alpha(1)
    plt.subplot(122)
    plt.plot(freq, Amp, label='|F(k)|')
    plt.xlabel('Frequency', fontsize=20)
    plt.ylabel('Amplitude', fontsize=20)
    plt.grid()
    leg = plt.legend(loc=1, fontsize=25)
    leg.get_frame().set_alpha(1)
    plt.savefig(str(now) + 'figure.png')
    plt.show()

if __name__ == "__main__":
    main()