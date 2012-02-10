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
    freq = 440.0*(ii+1)
    theta = 2.0 * math.pi * freq/44100.0
        # write data
    for i in range(int(44100.0/512.0)*1):
        sT = time.time()
        interleaved = numpy.zeros(bufferSize, dtype=numpy.float32)
        interleaved2 = numpy.zeros(bufferSize, dtype=numpy.int16)
        for j in range(512):
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
할일
사인웨이브
사인웨이브를 하는데 512프레임에 채우려니 이게 잘 안된다. 또한 사운드가 좀 튀는 것 같기도 하다.
둘 중 하난데 뭔지 모름 헤헤

둘 단데 암튼 전자는 512만 하지 말고 그 뒤에 좀 더 채워보면 암
"""
