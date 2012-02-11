# -*- coding: utf8 -*-
import pyaudio
import numpy
import math
import time
pyAudio = pyaudio.PyAudio()
chunk = 512
FORMAT = pyaudio.paFloat32
CHANNELS = 1
RATE = 44100
bufferSize = 512
stream = pyAudio.open(format = FORMAT,
                channels = CHANNELS,
                rate = RATE,
                output = True,
                frames_per_buffer = chunk)

frames = bufferSize
freq = 440.0
timer = 0
f = open("asd.txt", "w")
import wave
waveFile = wave.open("test.wav", "wb")
wf = waveFile
wf.setnchannels(1)
wf.setsampwidth(pyAudio.get_sample_size(pyaudio.paInt16))
wf.setframerate(44100)

for ii in range(2):
    sT = time.time()
    freqs = [440.0, 430.0, 420.0, 410.0, 400.0, 390.0]
    theta = 2.0 * math.pi * freq/44100.0
        # write data

    for i in range(int(44100.0/512.0)*1):
        iii = i/18
        sT = time.time()
        interleaved = numpy.zeros(bufferSize, dtype=numpy.float32)
        interleaved2 = numpy.zeros(bufferSize, dtype=numpy.int16)

        freq1 = freqs[i/18]/44100.0
        freq2 = freqs[(i/18)+1]/44100.0
        for j in range(512):
            theta = 2.0 * math.pi * (freq1+(freq2-freq1)*(float(j)/512.0))
            interleaved[j] = math.sin(theta*(j+i*512))*0.5
            timer += 1
            timer %= 512
       

        for j in range(512):
            interleaved2[j] = interleaved[j]*32767
        interleaved = interleaved.tostring()

        stream.write(interleaved, num_frames=frames)

        wf.writeframes(interleaved2.tostring())
        """
        done = False
        while not done:
            if time.time()-sT >= int(512.0/44100.0):
                break
        """


wf.close()
f.close()

"""
주파수가 서서히 줄어드는 현상을 구현하려면 스케일링을 해서 이전 주파수의 앵글값을 얻어서 같은 앵글에서 시작해야 한다.
"""
