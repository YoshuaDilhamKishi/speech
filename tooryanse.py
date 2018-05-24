# coding: shift-jis
import wave
import pyaudio


def printWaveInfo(wf):
    """WAVE�t�@�C���̏����擾"""
    print
    ("�`�����l����:", wf.getnchannels())
    print
    ("�T���v����:", wf.getsampwidth())
    print
    ("�T���v�����O���g��:", wf.getframerate())
    print
    ("�t���[����:", wf.getnframes())
    print
    ("�p�����[�^:", wf.getparams())
    print
    ("�����i�b�j:", float(wf.getnframes()) / wf.getframerate())


if __name__ == '__main__':
    wf = wave.open("ex0.wav", "wb")

    printWaveInfo(wf)

    # �X�g���[�����J��
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # �`�����N�P�ʂŃX�g���[���ɏo�͂��������Đ�
    chunk = 1024
    data = wf.readframes(chunk)
    while data != '':
        stream.write(data)
        data = wf.readframes(chunk)
    stream.close()
    p.terminate()