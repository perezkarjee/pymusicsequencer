# -*- coding: utf8 -*-
# License: GPLv3
# Author: yubgipenguin@gmail.com
"""
For God so loved the world, that he gave his only Son(Jesus), that whoever believes in him should not perish but have eternal life.
- John 3:16, Holy Bible
Be saved first and then make some music!
"""
# dependencies:
# pyPortmidi
# pyAudio
# numpy
# pyqt4
# included in source package:
# pyvst, midiutil
# when installing pyPortmidi you must copy portmidi.dll to the pyPortmidi folder.
# see license files for more details on licenses I have included all the license files in the source package.
from midiutil.MidiFile import MIDIFile
import pypm
import array
import time
import threading
import pyvst
from ctypes import *
import numpy
import time
import pyaudio
import pickle
import math
import sip
import sys, os
sip.setapi('QVariant', 2)

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
import PyQt4

imagesPath = "./MusicTheory/images" # FIXME: fix this
imagesPath2 = "/MusicTheory/images" # FIXME: fix this
import math
SettingsSingleton = None
CurProjectSingleton = None
TempoSingleton = None
VSTThreadSingleton = None
ParentFrameSingleton = None
PianoRollSingleton = None
StatusBarSingleton = None
ApplicationSingleton = None
MixerPanelsSingleton = None
OpenedWindowSingleton = None
PatternManagerSingleton = None
g_WindowClosed = False
LMB = 1
RMB = 2
def ShiftOn():
    if ApplicationSingleton.keyboardModifiers() & Qt.ShiftModifier:
        return True
    else:
        return False
def AltOn():
    if ApplicationSingleton.keyboardModifiers() & Qt.AltModifier:
        return True
    else:
        return False


def GetFrequency(d):
    return 440*(2**((d-69)/12))
def DoPopup(parent, menu, ev):
    if ev.button() == RMB:
        menu.exec_( parent.mapToGlobal(ev.pos()) ) 

def GetTempos(key, beatDividedBy=12, min=60, max=180):
    secondsPerCycle = 1.0/float(GetFrequency(key))
    cyclesPerMinute =  60.0 / secondsPerCycle # max tempo == cyclesPerMinute
    maxDivisor = cyclesPerMinute
    tempos = []
    # tempo / 60 = beatsPerSecond
    # tempo = beatsPerSecond*60
    for i in range(int(maxDivisor)):
        i += 1
        tempo = cyclesPerMinute/i # i는 비트당 몇개의 사이클이 들어가느냐 하는 의미이다.
        if (i % beatDividedBy) == 0:
            if min <= tempo <= max:
                tempos += [tempo]
        if tempo < min:
            break

    return tempos

def GetLCM(c, d):
    def gcd(a, b):
        if a == 0:
            return b;
        while b:
            if a > b:
                a = a-b
            else:
                b = b-a
        return a
    g = gcd(c,d)
    return (c*d)/g

from threading import Thread

def SetFixed(wgt):
    sizePolicy = wgt.sizePolicy()
    sizePolicy.setHorizontalPolicy(QtGui.QSizePolicy.Fixed) 
    wgt.setSizePolicy(sizePolicy)

def SetBitmapButton(button, fileName):
    path = os.getcwd() 
    sheet = "background-image: url(" + path + imagesPath2 + "/" + fileName + ");"
    sheet = sheet.replace("\\", "/")
    button.setStyleSheet(sheet) 

def BitmapButton(imgName, size=QtCore.QSize(23, 23), parent=None):
    btn = QtGui.QPushButton("", parent, size=size)
    SetBitmapButton(btn, imgName)
    return btn

class RenderNotesWorker(Thread):
    quit = False
    def __init__(self, vstThd, notes):
        RenderNotesWorker.quit = False
        Thread.__init__(self)
        self.vstThd = vstThd
        self.notes = notes
    def run(self):
        def Go(mutexObj):
            self.vstThd.locked = True
            notes = self.notes
            notesByTime = {}
            for note in notes.itervalues():
                if note[2] not in notesByTime.keys():
                    notesByTime[note[2]] = []
                pos = 1.0/float(note[1])*float(note[2])
                len_ = 1.0/float(note[1])*float(note[3]+note[2])
                pos = (60000.0/float(TempoSingleton.GetTempo()/4.0)) * pos
                len_ = (60000.0/float(TempoSingleton.GetTempo()/4.0)) * len_
                notesByTime[note[2]] += [[note[0], pos, len_]]

            def compare(x, y):
                return int(math.ceil(x[0] - y[0]))

            def BuildMsgs(notesByTime_):
                msgs = []
                keys = notesByTime_.keys()
                keys.sort()
                volumes = []
                for key in keys:
                    for note in notesByTime_[key]:
                        key, pos, len_ = note
                        msgs += [[pos, key, 100]]
                        msgs += [[len_, key, 0]]

                msgs = sorted(msgs, cmp=compare)
                return msgs

            frame = 512.0
            samplingRate = 44100.0
            secondsPerBlock = frame / (samplingRate)
                        
            msgs = BuildMsgs(notesByTime)

            bufferSize = int(frame*8)
            output1 = numpy.zeros((self.vstThd.vstEff.number_of_outputs, bufferSize), dtype=numpy.float32)
            output2 = numpy.zeros((self.vstThd.vstEff.number_of_outputs, bufferSize), dtype=numpy.float32)

            nextPlayTime = 0
            curNotPlayingBuffer = output1
            curBufferIdx = 1
            idxidx = 0
            def StopAllNotes(playingNotes):
                if playingNotes:
                    kVstMidiType = 1
                    kVstMidiEventIsRealTime = 1
                    vstMidiEvents = pyvst.VstMidiEvents()
                    vstMidiEvents.numEvents = len(playingNotes)
                    vstMidiEvents.reserved = 0
                    for msgIdx in range(len(playingNotes)):
                        playingNote = playingNotes[msgIdx]
                        midiEvent1 = pyvst.VstMidiEvent()
                        midiEvent1.type = kVstMidiType
                        midiEvent1.byteSize = 24
                        midiEvent1.deltaFrames = 0
                        midiEvent1.flags = kVstMidiEventIsRealTime
                        midiEvent1.noteLength = 0
                        midiEvent1.noteOffset = 0
                        midiEvent1.midiData1 = (0x90)
                        midiEvent1.midiData2 = (playingNote)
                        midiEvent1.midiData3 = (0x00)
                        midiEvent1.midiData4 = (0x00)
                        midiEvent1.detune = 0
                        midiEvent1.noteOffVelocity = 0
                        midiEvent1.reserved1 = 0
                        midiEvent1.reserved2 = 0
                        vstMidiEvents.events[msgIdx] = POINTER(pyvst.VstMidiEvent)(midiEvent1)

                    self.vstThd.vstEff.ProcessMidi(vstMidiEvents)
                    self.vstThd.vstEff.process_replacing_output(curNotPlayingBuffer[:, i*512:(i+1)*512], 512)

            import wave
            waveFile = wave.open("test.wav", "wb")
            wf = waveFile
            wf.setnchannels(2)
            wf.setsampwidth(self.vstThd.pyAudio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)

            playingNotes = []
            while msgs and not RenderNotesWorker.quit: # 이걸로 하면 안되고 지정해준 음악의 길이로 해야 함.
                for i in range(bufferSize/512):
                    curMsgs = []
                    lastIdx = 0
                    for msgIdx in range(len(msgs)):
                        lastIdx = msgIdx+1
                        msg = msgs[msgIdx]
                        deltaFrames = int((msg[0]-((idxidx*bufferSize/512+i)*secondsPerBlock*1000)) * (samplingRate/1000.0))
                        if deltaFrames < 512:
                            curMsgs += [(deltaFrames, msg[1], msg[2])]
                        else:
                            lastIdx = msgIdx
                            break

                    msgs = msgs[lastIdx:]

                    if curMsgs:
                        kVstMidiType = 1
                        kVstMidiEventIsRealTime = 1
                        vstMidiEvents = pyvst.VstMidiEvents()
                        vstMidiEvents.numEvents = len(curMsgs)
                        vstMidiEvents.reserved = 0
                        for msgIdx in range(len(curMsgs)):
                            msg = curMsgs[msgIdx]
                            if msg[2] >= 0.05:
                                playingNotes += [msg[1]]
                            elif msg[2] < 0.05:
                                try:
                                    del playingNotes[playingNotes.index(msg[1])]
                                except:
                                    pass

                            midiEvent1 = pyvst.VstMidiEvent()
                            midiEvent1.type = kVstMidiType
                            midiEvent1.byteSize = 24
                            midiEvent1.deltaFrames = msg[0]
                            midiEvent1.flags = kVstMidiEventIsRealTime
                            midiEvent1.noteLength = 0
                            midiEvent1.noteOffset = 0
                            midiEvent1.midiData1 = (0x90)
                            midiEvent1.midiData2 = (msg[1])
                            midiEvent1.midiData3 = (msg[2])
                            midiEvent1.midiData4 = (0x00)
                            midiEvent1.detune = 0
                            midiEvent1.noteOffVelocity = 0
                            midiEvent1.reserved1 = 0
                            midiEvent1.reserved2 = 0
                            vstMidiEvents.events[msgIdx] = POINTER(pyvst.VstMidiEvent)(midiEvent1)

                        self.vstThd.vstEff.ProcessMidi(vstMidiEvents)
                    self.vstThd.vstEff.process_replacing_output(curNotPlayingBuffer[:, i*512:(i+1)*512], 512)

                interleaved = numpy.zeros(bufferSize*2, dtype=numpy.int16)
                for i in range(bufferSize):
                    interleaved[i*2] = int(curNotPlayingBuffer[0][i]*32767.0)
                    interleaved[i*2+1] = int(curNotPlayingBuffer[1][i]*32767.0)
                interleaved = interleaved.tostring()
                frames = bufferSize
                wf.writeframes(interleaved)
                #self.vstThd.stream.write(interleaved, num_frames=frames)
                # 여기서 wave에다가 쓰면 됨.
                # 근데 포멧이 이래서 변형을 해야하나? 음..float32의 포멧의 wave가 있나?
                #nextPlayTime = pypm.Time() + (bufferSize/512)*secondsPerBlock*1000
                if curBufferIdx == 1:
                    curBufferIdx = 2
                    curNotPlayingBuffer = output2
                elif curBufferIdx == 2:
                    curBufferIdx = 1
                    curNotPlayingBuffer = output1

                idxidx += 1
            wf.close()
            StopAllNotes(playingNotes)
            self.vstThd.locked = False
            self.vstThd.mutexObj.unlock()

        self.vstThd.mutexObj.lock(Go, self.vstThd.mutexObj)

class PlayNotesWorker(Thread): # 한 패턴만 연주하거나 플레이리스트를 연주한다. 한 패턴 안에는 여러 악기가 있을 수 있고
    #한 플레이리스트 안에는 여러 패턴이 있다.
    # 제대로 이거 만들고 렌더링도 되게 하면 거의 완성이다.
    # 모든 악기의 각각 idle하는 상황에서도 읽어와서 합쳐야 한다. 꼬리라던가 리버브 등등...
    # 그러면 데이터는 그냥
    # 악기당 notes를 악기와 이펙트와 함께 묶어서 주고 그냥 한 process 턴마다 한번씩 돌리고 다 합쳐서 플레이하면 된다.
    # 거기서 버퍼를 wave로 쓰기만 하면 렌더링임!
    quit = False
    #def __init__(self, vstThd, notes, panel, pattern, playlist=None):
    def __init__(self, vstThd, pattern, playlist=None):
        # notes = (vst, fxs, notes)
        # pattern = [notes, notes, ...]
        # playlist = [(posintime, pattern), (posintime, pattern), ...]
        PlayNotesWorker.quit = False
        Thread.__init__(self)
        self.vstThd = vstThd
        self.pattern = pattern
        self.playlist = playlist
        # 기존의 방법처럼 한 개의 노트 리스트로 만들어서
        # 늘어놓고
        # "시간"과 "노트 목록" 두개를 기준으로 진행해야 한다.
        # 일단 시간이 앞에 공백시간이 있을 것이다. 그만큼 기다린다.
        # 그 다음 첫번째 노트가 플레이 되기 시작한다.
        # 한 턴(512만큼의 버퍼만큼)만큼의 노트 메시지들을 알맞는 VST들에 보낸 후
        # 모든 VST를 그 턴만큼 읽고
        # 모든 버퍼를 더해서 출력하고
        # 그 버퍼의 지속시간의 1/2시간만큼 기다린 후 다시 반복한다.
        # 쓰레드를 쓰면서도 PyQt의 repaint에러를 안나오게 하려면 pyqt의 메인루프에 관여해서 값을 넣고 메인루프에서 값이 셋되어있으면
        # repaint를 하는 방법으로 플레잉 바를 그려야할텐데.... <---- 아 PyQt의 타이머를 쓰면 그런 걱정이 없는 듯 하다.
    def run(self):
        def Go2(mutexObj):
            self.vstThd.locked = True
            playingNotesDict = {}
            pattern = self.pattern
            notesByTime = {}
            for notes in pattern:
                for note in notes.itervalues():
                    if note[2] not in notesByTime.keys():
                        notesByTime[note[2]] = []
                    pos = 1.0/float(note[1])*float(note[2])
                    len_ = 1.0/float(note[1])*float(note[3]+note[2])
                    pos = (60000.0/float(TempoSingleton.GetTempo()/4.0)) * pos
                    len_ = (60000.0/float(TempoSingleton.GetTempo()/4.0)) * len_
                    notesByTime[note[2]] += [[note[0], pos, len_, note[4]]] # note[4] is vsti

            def compare(x, y):
                return int(math.ceil(x[0] - y[0]))

            def BuildMsgs(notesByTime_):
                msgs = []
                keys = notesByTime_.keys()
                keys.sort()
                volumes = []
                for key in keys:
                    for note in notesByTime_[key]:
                        midikey, pos, endpos, vsti = note
                        msgs += [[pos, midikey, 100, vsti]]
                        msgs += [[endpos, midikey, 0, vsti]]

                #msgs = sorted(msgs+volumes, cmp=compare)
                msgs = sorted(msgs, cmp=compare)
                return msgs

            """
            메시지가 다 만들어 졌다면
            루프를 돈다. 쓰레드를 하나 더 할 필요는 없고 걍 뮤텍스 락을 걸고 한다.?
            아니다. 쓰레드를 하나 더 만들어서 해야 한다. 대신, 뮤텍스 락은 똑같은 걸 쓴다.

            기다린다. 음....... 일단 버퍼를 한 4096 길이로 해서 8번씩 루프를 돌면서 버퍼를 채우고
            4096이면 몇초지?
            4096짜리 버퍼를 2개 만들어서
            seconds / 2 만큼의 시간이 지나면 다른 버퍼를 채우고 이런다? 아니다.
            하나 채우고 플레이 하면서 그 도중에 또 채우고 기다렸다가 플레이된 게 끝나면 바로 또 그 버퍼에 채우고 이런다.
            frame = seconds * (samplingRate / 1000)


            플레이를 중단하면 현재 On된 노트를 모두 추적해서 off해줘야 한다.


            한개의 악기와 한개의 노트리스트에 대한 건 있으니
            이걸 한 번 루프 돌 때 여러 악기와 여러 노트리스트에 대해 돌면 된다.
            노트리스트를 시간을 기준으로 하나로 합치고 각 노트에 vst에 대한 링크를 둔다.
            """
            frame = 512.0
            samplingRate = 44100.0
            secondsPerBlock = frame / (samplingRate)
                        
            msgs = BuildMsgs(notesByTime)
            """
            음 set으로 각각의 vsti를 구해서 각각 인풋아웃풋 넘버에 따라 버퍼를 할당한다.
            bufferSize를 그냥 512로 한다.
            12
            """
            vstis = [msg[3] for msg in msgs]
            vstis = list(set(vstis))

            bufferSize = int(frame*8)
            outputs1 = [numpy.zeros((vstis[i].vstEff.number_of_outputs, bufferSize), dtype=numpy.float32) for i in range(len(vstis))]
            outputs2 = [numpy.zeros((vstis[i].vstEff.number_of_outputs, bufferSize), dtype=numpy.float32) for i in range(len(vstis))]


            nextPlayTime = 0
            curNotPlayingBuffers = outputs1
            curBufferIdx = 1
            idxidx = 0
            def StopAllNotes(playingNotesDict):
                if playingNotesDict:
                    for vsti in playingNotesDict.iterkeys():
                        kVstMidiType = 1
                        kVstMidiEventIsRealTime = 1
                        vstMidiEvents = pyvst.VstMidiEvents()
                        vstMidiEvents.numEvents = len(playingNotesDict[vsti])
                        vstMidiEvents.reserved = 0
                        for msgIdx in range(len(playingNotesDict[vsti])):
                            playingNote = playingNotesDict[vsti][msgIdx]
                            midiEvent1 = pyvst.VstMidiEvent()
                            midiEvent1.type = kVstMidiType
                            midiEvent1.byteSize = 24
                            midiEvent1.deltaFrames = 0
                            midiEvent1.flags = kVstMidiEventIsRealTime
                            midiEvent1.noteLength = 0
                            midiEvent1.noteOffset = 0
                            midiEvent1.midiData1 = (0x90)
                            midiEvent1.midiData2 = (playingNote)
                            midiEvent1.midiData3 = (0x00)
                            midiEvent1.midiData4 = (0x00)
                            midiEvent1.detune = 0
                            midiEvent1.noteOffVelocity = 0
                            midiEvent1.reserved1 = 0
                            midiEvent1.reserved2 = 0
                            vstMidiEvents.events[msgIdx] = POINTER(pyvst.VstMidiEvent)(midiEvent1)

                        tempBuffer = numpy.zeros((vsti.vstEff.number_of_outputs, bufferSize), dtype=numpy.float32)
                        vsti.vstEff.ProcessMidi(vstMidiEvents)
                        vsti.vstEff.process_replacing_output(tempBuffer[:, i*512:(i+1)*512], 512)


            while msgs and not PlayNotesWorker.quit:
                for i in range(bufferSize/512):
                    curMsgs = []
                    lastIdx = 0
                    for msgIdx in range(len(msgs)):
                        lastIdx = msgIdx+1
                        msg = msgs[msgIdx]
                        deltaFrames = int((msg[0]-((idxidx*bufferSize/512+i)*secondsPerBlock*1000)) * (samplingRate/1000.0))
                        if deltaFrames < 512:
                            curMsgs += [(deltaFrames, msg[1], msg[2], msg[3])]
                        else:
                            lastIdx = msgIdx
                            break

                    msgs = msgs[lastIdx:]

                    if curMsgs:
                        """
                        vstis를 이용해서
                        메시지중에 vst가 같은 것들만 현재 버퍼에 넣고 보내고 이런다.
                        """
                        for vsti in vstis:
                            kVstMidiType = 1
                            kVstMidiEventIsRealTime = 1
                            vstMidiEvents = pyvst.VstMidiEvents()
                            curVSTMsgs = [msg for msg in curMsgs if msg[3] == vsti]
                            vstMidiEvents.numEvents = len(curVSTMsgs)
                            vstMidiEvents.reserved = 0
                            for msgIdx in range(len(curVSTMsgs)):
                                msg = curVSTMsgs[msgIdx]
                                if msg[2] >= 0.05: # volume
                                    if vsti not in playingNotesDict:
                                        playingNotesDict[vsti] = []
                                    playingNotesDict[vsti] += [msg[1]]
                                elif msg[2] < 0.05:
                                    try:
                                        del playingNotesDict[vsti][playingNotesDict[vsti].index(msg[1])]
                                    except:
                                        pass

                                midiEvent1 = pyvst.VstMidiEvent()
                                midiEvent1.type = kVstMidiType
                                midiEvent1.byteSize = 24
                                midiEvent1.deltaFrames = msg[0]
                                midiEvent1.flags = kVstMidiEventIsRealTime
                                midiEvent1.noteLength = 0
                                midiEvent1.noteOffset = 0
                                midiEvent1.midiData1 = (0x90)
                                midiEvent1.midiData2 = (msg[1])
                                midiEvent1.midiData3 = (msg[2])
                                midiEvent1.midiData4 = (0x00)
                                midiEvent1.detune = 0
                                midiEvent1.noteOffVelocity = 0
                                midiEvent1.reserved1 = 0
                                midiEvent1.reserved2 = 0
                                vstMidiEvents.events[msgIdx] = POINTER(pyvst.VstMidiEvent)(midiEvent1)

                            if len(curVSTMsgs):
                                vsti.vstEff.ProcessMidi(vstMidiEvents)

                    for vstiIdx in range(len(vstis)):
                        vsti = vstis[vstiIdx]
                        vsti.vstEff.process_replacing_output(curNotPlayingBuffers[vstiIdx][:, i*512:(i+1)*512], 512)
                        #inputMono[0:1, i*512:(i+1)*512] = curNotPlayingBuffer[0:1, i*512:(i+1)*512]/2.0 + curNotPlayingBuffer[1:2, i*512:(i+1)*512]/2.0
                       # self.panel.vstFX.vstEff.process_replacing(inputMono[:, i*512:(i+1)*512], outputMono[:, i*512:(i+1)*512])
                      #  curNotPlayingBuffer[0:1, i*512:(i+1)*512] = outputMono[0][i*512:(i+1)*512]
                     #   curNotPlayingBuffer[1:2, i*512:(i+1)*512] = outputMono[0][i*512:(i+1)*512]
                    # number of output등을 잘 살펴서 모노인지 스테레오인지 구별해서 해야함.
                # 일단 아웃풋이 1개인 것과 2개인 것에 대해서만 한다.
                if len(curNotPlayingBuffers[0]) == 2:
                    outputBuffer = curNotPlayingBuffers[0]
                elif len(curNotPlayingBuffers[0]) == 1:
                    outputBuffer = curNotPlayingBuffers[0], curNotPlayingBuffers[0]
                for buffer in curNotPlayingBuffers[1:]:
                    if len(buffer) == 2:
                        outputBuffer[0] = outputBuffer[0] + buffer[0]
                        outputBuffer[1] = outputBuffer[1] + buffer[1]
                    elif len(buffer) == 1:
                        outputBuffer[0] = outputBuffer[0] + buffer[0]
                        outputBuffer[1] = outputBuffer[1] + buffer[0]

                frames = bufferSize
                output = self.GetInterleaved(output, frames)
                while nextPlayTime > pypm.Time():
                    if PlayNotesWorker.quit:
                        StopAllNotes(playingNotesDict)
                        self.panel.playing= False
                        self.vstThd.mutexObj.unlock()
                        return
                self.SoundOut(output, frames)
                nextPlayTime = pypm.Time() + (bufferSize/512)*secondsPerBlock*1000
                if curBufferIdx == 1:
                    curBufferIdx = 2
                    curNotPlayingBuffers = outputs2
                elif curBufferIdx == 2:
                    curBufferIdx = 1
                    curNotPlayingBuffers = outputs1

                idxidx += 1
            
            StopAllNotes(playingNotesDict)

            self.panel.playing = False
            self.vstThd.locked = False
            self.vstThd.mutexObj.unlock()

        def Go(mutexObj):
            self.vstThd.locked = True
            playingNotes = []
            notes = self.notes
            notesByTime = {}
            for note in notes.itervalues():
                if note[2] not in notesByTime.keys():
                    notesByTime[note[2]] = []
                pos = 1.0/float(note[1])*float(note[2])
                len_ = 1.0/float(note[1])*float(note[3]+note[2])
                pos = (60000.0/float(TempoSingleton.GetTempo()/4.0)) * pos
                len_ = (60000.0/float(TempoSingleton.GetTempo()/4.0)) * len_
                notesByTime[note[2]] += [[note[0], pos, len_]]

            def compare(x, y):
                return int(math.ceil(x[0] - y[0]))

            def BuildMsgs(notesByTime_):
                msgs = []
                keys = notesByTime_.keys()
                keys.sort()
                volumes = []
                for key in keys:
                    for note in notesByTime_[key]:
                        key, pos, len_ = note
                        msgs += [[pos, key, 100]]
                        msgs += [[len_, key, 0]]
                        counter = 0
                        count = 100
                        time = 0
                        vol = 1
                        volumeDef = [[0,20], [30,40], [50, 60], [70, 80], [90, 100], [110, 127]]
                        volCouter = 0
                        while counter < count:
                            volumes += [[pos+time-1, min(127, int(vol/float(count)*100.0))]]
                            time += ((len_-pos)/float(count)) / 5.0
                            for i in range(len(volumeDef)):
                                if counter < count*i/float(len(volumeDef)):
                                    idx = i
                            vol = volumeDef[idx][0] + (volumeDef[idx][1] - volumeDef[idx][0]) / float(100-volCouter)
                            counter += 1
                        counter = 0
                        volCouter += len(volumeDef)
                        if volCouter >= 99:
                            volCouter = 0
                        time = len_-pos
                        vol = 127
                        """
                        while counter < count:
                            volumes += [[pos+time, max(0, int(vol/float(count)*100.0))]]
                            time -= ((len-pos)/float(count)) / 3.0
                            vol -= counter*0.5
                            counter += 1
                        """

                #msgs = sorted(msgs+volumes, cmp=compare)
                msgs = sorted(msgs, cmp=compare)
                return msgs

            """
            메시지가 다 만들어 졌다면
            루프를 돈다. 쓰레드를 하나 더 할 필요는 없고 걍 뮤텍스 락을 걸고 한다.?
            아니다. 쓰레드를 하나 더 만들어서 해야 한다. 대신, 뮤텍스 락은 똑같은 걸 쓴다.

            기다린다. 음....... 일단 버퍼를 한 4096 길이로 해서 8번씩 루프를 돌면서 버퍼를 채우고
            4096이면 몇초지?
            4096짜리 버퍼를 2개 만들어서
            seconds / 2 만큼의 시간이 지나면 다른 버퍼를 채우고 이런다? 아니다.
            하나 채우고 플레이 하면서 그 도중에 또 채우고 기다렸다가 플레이된 게 끝나면 바로 또 그 버퍼에 채우고 이런다.
            frame = seconds * (samplingRate / 1000)


            플레이를 중단하면 현재 On된 노트를 모두 추적해서 off해줘야 한다.


            한개의 악기와 한개의 노트리스트에 대한 건 있으니
            이걸 한 번 루프 돌 때 여러 악기와 여러 노트리스트에 대해 돌면 된다.
            노트리스트를 시간을 기준으로 하나로 합치고 각 노트에 vst에 대한 링크를 둔다.
            """
            frame = 512.0
            samplingRate = 44100.0
            secondsPerBlock = frame / (samplingRate)
                        
            msgs = BuildMsgs(notesByTime)

            bufferSize = int(frame*8)
            output1 = numpy.zeros((self.vstThd.vstEff.number_of_outputs, bufferSize), dtype=numpy.float32)
            inputMono = numpy.zeros((self.panel.vstFX.vstEff.number_of_inputs, bufferSize), dtype=numpy.float32)
            outputMono = numpy.zeros((self.panel.vstFX.vstEff.number_of_outputs, bufferSize), dtype=numpy.float32)
            output2 = numpy.zeros((self.vstThd.vstEff.number_of_outputs, bufferSize), dtype=numpy.float32)

            nextPlayTime = 0
            curNotPlayingBuffer = output1
            curBufferIdx = 1
            idxidx = 0
            def StopAllNotes(playingNotes):
                if playingNotes:
                    kVstMidiType = 1
                    kVstMidiEventIsRealTime = 1
                    vstMidiEvents = pyvst.VstMidiEvents()
                    vstMidiEvents.numEvents = len(playingNotes)
                    vstMidiEvents.reserved = 0
                    for msgIdx in range(len(playingNotes)):
                        playingNote = playingNotes[msgIdx]
                        midiEvent1 = pyvst.VstMidiEvent()
                        midiEvent1.type = kVstMidiType
                        midiEvent1.byteSize = 24
                        midiEvent1.deltaFrames = 0
                        midiEvent1.flags = kVstMidiEventIsRealTime
                        midiEvent1.noteLength = 0
                        midiEvent1.noteOffset = 0
                        midiEvent1.midiData1 = (0x90)
                        midiEvent1.midiData2 = (playingNote)
                        midiEvent1.midiData3 = (0x00)
                        midiEvent1.midiData4 = (0x00)
                        midiEvent1.detune = 0
                        midiEvent1.noteOffVelocity = 0
                        midiEvent1.reserved1 = 0
                        midiEvent1.reserved2 = 0
                        vstMidiEvents.events[msgIdx] = POINTER(pyvst.VstMidiEvent)(midiEvent1)

                    self.vstThd.vstEff.ProcessMidi(vstMidiEvents)
                    self.vstThd.vstEff.process_replacing_output(curNotPlayingBuffer[:, i*512:(i+1)*512], 512)


            while msgs and not PlayNotesWorker.quit:
                for i in range(bufferSize/512):
                    curMsgs = []
                    lastIdx = 0
                    for msgIdx in range(len(msgs)):
                        lastIdx = msgIdx+1
                        msg = msgs[msgIdx]
                        deltaFrames = int((msg[0]-((idxidx*bufferSize/512+i)*secondsPerBlock*1000)) * (samplingRate/1000.0))
                        if deltaFrames < 512:
                            curMsgs += [(deltaFrames, msg[1], msg[2])]
                        else:
                            lastIdx = msgIdx
                            break

                    msgs = msgs[lastIdx:]

                    if curMsgs:
                        kVstMidiType = 1
                        kVstMidiEventIsRealTime = 1
                        vstMidiEvents = pyvst.VstMidiEvents()
                        vstMidiEvents.numEvents = len(curMsgs)
                        vstMidiEvents.reserved = 0
                        for msgIdx in range(len(curMsgs)):
                            msg = curMsgs[msgIdx]
                            if msg[2] >= 0.05:
                                playingNotes += [msg[1]]
                            elif msg[2] < 0.05:
                                try:
                                    del playingNotes[playingNotes.index(msg[1])]
                                except:
                                    pass

                            midiEvent1 = pyvst.VstMidiEvent()
                            midiEvent1.type = kVstMidiType
                            midiEvent1.byteSize = 24
                            midiEvent1.deltaFrames = msg[0]
                            midiEvent1.flags = kVstMidiEventIsRealTime
                            midiEvent1.noteLength = 0
                            midiEvent1.noteOffset = 0
                            midiEvent1.midiData1 = (0x90)
                            midiEvent1.midiData2 = (msg[1])
                            midiEvent1.midiData3 = (msg[2])
                            midiEvent1.midiData4 = (0x00)
                            midiEvent1.detune = 0
                            midiEvent1.noteOffVelocity = 0
                            midiEvent1.reserved1 = 0
                            midiEvent1.reserved2 = 0
                            vstMidiEvents.events[msgIdx] = POINTER(pyvst.VstMidiEvent)(midiEvent1)

                        self.vstThd.vstEff.ProcessMidi(vstMidiEvents)
                    self.vstThd.vstEff.process_replacing_output(curNotPlayingBuffer[:, i*512:(i+1)*512], 512)
                    inputMono[0:1, i*512:(i+1)*512] = curNotPlayingBuffer[0:1, i*512:(i+1)*512]/2.0 + curNotPlayingBuffer[1:2, i*512:(i+1)*512]/2.0
                    self.panel.vstFX.vstEff.process_replacing(inputMono[:, i*512:(i+1)*512], outputMono[:, i*512:(i+1)*512])
                    curNotPlayingBuffer[0:1, i*512:(i+1)*512] = outputMono[0][i*512:(i+1)*512]
                    curNotPlayingBuffer[1:2, i*512:(i+1)*512] = outputMono[0][i*512:(i+1)*512]
                    # number of output등을 잘 살펴서 모노인지 스테레오인지 구별해서 해야함.

                interleaved = numpy.zeros(bufferSize*2, dtype=numpy.float32)
                for i in range(2):
                    interleaved[i::2] = curNotPlayingBuffer[i]
                interleaved = interleaved.tostring()
                while nextPlayTime > pypm.Time():
                    if PlayNotesWorker.quit:
                        StopAllNotes(playingNotes)
                        self.panel.playing= False
                        self.vstThd.mutexObj.unlock()
                        return
                frames = bufferSize
                self.vstThd.stream.write(interleaved, num_frames=frames)
                nextPlayTime = pypm.Time() + (bufferSize/512)*secondsPerBlock*1000
                if curBufferIdx == 1:
                    curBufferIdx = 2
                    curNotPlayingBuffer = output2 = numpy.zeros((self.vstThd.vstEff.number_of_outputs, bufferSize), dtype=numpy.float32)
                elif curBufferIdx == 2:
                    curBufferIdx = 1
                    curNotPlayingBuffer = output1 = numpy.zeros((self.vstThd.vstEff.number_of_outputs, bufferSize), dtype=numpy.float32)

                idxidx += 1
            
            StopAllNotes(playingNotes)

            self.panel.playing = False
            self.vstThd.locked = False
            self.vstThd.mutexObj.unlock()
        self.vstThd.mutexObj.lock(Go2, self.vstThd.mutexObj)
        # 사운드 워커보다 이게 더 프라이오리티가 높아야 하므로...
        # 뭔가 해서 음..



class VSTSoundWorker(Thread):
    quit = False
    def __init__(self, parent):
        Thread.__init__(self)
        self.vstEff = None
        self.fxs = []
        self.parent = parent
        self.inited = False
        self.pyAudio = pyaudio.PyAudio()
        chunk = 512
        FORMAT = pyaudio.paFloat32
        CHANNELS = 2
        RATE = 44100
        self.stream = self.pyAudio.open(format = FORMAT,
                        channels = CHANNELS,
                        rate = RATE,
                        output = True,
                        frames_per_buffer = chunk)

        self.playingNote = []
        self.locked = False
        self.stopped = True
        """
        아 알았다. 무조건 한 쓰레드에서 해야한다. 쓰레드를 하나 더 띄우면 process_replacing이 뭐 진행중인데 한 번 더 불러서 에러나고 이러는 거 같다.
        플레이고 뭐고 run쓰레드에서 해야한다.
        """
        self.playNote = None
        self.stopNote = False
        self.paramCallbacks = []
        self.setParams = []
        self.msgSent = False
        self.switchInstrument = False
        self.prevPlayNoteTime = 0
        self.playNotesMode = False

    def SetParam(self, index, param):
        self.setParams += [(index, param)]
    def GetParamCallBack(self, func):
        self.paramCallbacks += [func]
    def PlayNotes(self, panel, notes, pattern):
        PlayNotesWorker.quit = True
        self.notes = notes
        self.panel = panel
        self.pattern = pattern
        self.playNotesMode = True
    def RenderNotes(self, notes):
        self.renderThd = RenderNotesWorker(self, notes)
        self.renderThd.start()
    def StopNotes(self):
        self.playNotesMode = False

    def StopNote(self):
        # 음....... PlayNote를 리스트에 넣고
        # 마우스를 떼면 모든 PlayNote리스트에 있는 걸 다 스톱해야 한다.
            # 이야 이거 제대로 안 되는데? (......)
        self.stopNote = True
        self.playNote = None

    def StopNoteCmd(self):
        self.stopped = True
        if self.playingNote:
            kVstMidiType = 1
            kVstMidiEventIsRealTime = 1
            vstMidiEvents = pyvst.VstMidiEvents()
            vstMidiEvents.numEvents = len(self.playingNote)
            vstMidiEvents.reserved = 0
            for i in range(len(self.playingNote)):
                key = self.playingNote[i]
                midiEvent1 = pyvst.VstMidiEvent()
                midiEvent1.type = kVstMidiType
                midiEvent1.byteSize = 24
                midiEvent1.deltaFrames = 0
                midiEvent1.flags = kVstMidiEventIsRealTime
                midiEvent1.noteLength = 0
                midiEvent1.noteOffset = 0
                midiEvent1.midiData1 = (0x90)
                midiEvent1.midiData2 = (key)
                midiEvent1.midiData3 = (0x00)
                midiEvent1.midiData4 = (0x00)
                midiEvent1.detune = 0
                midiEvent1.noteOffVelocity = 0
                midiEvent1.reserved1 = 0
                midiEvent1.reserved2 = 0
                vstMidiEvents.events[i] = POINTER(pyvst.VstMidiEvent)(midiEvent1)
            self.vstEff.ProcessMidi(vstMidiEvents)
            self.playingNote = []
            output = self.ReadVSTi()
            output = self.ApplyEffect512(output)
            frames = 512
            interleaved = numpy.zeros(frames*2, dtype=numpy.float32)
            for i in range(2):
                interleaved[i::2] = output[i]
            self.stream.write(interleaved.tostring(), num_frames=frames)

        self.stopNote = False

    def PlayNoteCmd(self, key):
        self.stopped = False
        kVstMidiType = 1
        kVstMidiEventIsRealTime = 1
        vstMidiEvents = pyvst.VstMidiEvents()
        vstMidiEvents.numEvents = 1
        vstMidiEvents.reserved = 0

        midiEvent1 = pyvst.VstMidiEvent()
        midiEvent1.type = kVstMidiType
        midiEvent1.byteSize = 24
        midiEvent1.deltaFrames = 0
        midiEvent1.flags = kVstMidiEventIsRealTime
        midiEvent1.noteLength = 0
        midiEvent1.noteOffset = 0
        midiEvent1.midiData1 = (0x90)
        midiEvent1.midiData2 = (key)
        midiEvent1.midiData3 = (100) # TODO:볼륨을 읽어온다. 음.... 한 악기의 볼륨이 큰 건 무조건 안 좋구나?
        midiEvent1.midiData4 = (0x00)
        midiEvent1.detune = 0
        midiEvent1.noteOffVelocity = 0
        midiEvent1.reserved1 = 0
        midiEvent1.reserved2 = 0
        vstMidiEvents.events[0] = POINTER(pyvst.VstMidiEvent)(midiEvent1)
        self.vstEff.ProcessMidi(vstMidiEvents)
        self.playingNote = [key]

        output = self.ReadVSTi()
        output = self.ApplyEffect512(output)
        frames = 512
        interleaved = numpy.zeros(frames*2, dtype=numpy.float32)
        for i in range(2):
            interleaved[i::2] = output[i]
        self.stream.write(interleaved.tostring(), num_frames=frames)

    def PlayNotesCmd(self):
        playingNotesDict = {}
        pattern = self.pattern
        notesByTime = {}
        for notes in pattern:
            for note in notes.itervalues():
                if note[2] not in notesByTime.keys():
                    notesByTime[note[2]] = []
                pos = 1.0/float(note[1])*float(note[2])
                len_ = 1.0/float(note[1])*float(note[3]+note[2])
                pos = (60000.0/float(TempoSingleton.GetTempo()/4.0)) * pos
                len_ = (60000.0/float(TempoSingleton.GetTempo()/4.0)) * len_
                notesByTime[note[2]] += [[note[0], pos, len_, note[4]]] # note[4] is vsti

        def compare(x, y):
            return int(math.ceil(x[0] - y[0]))

        def BuildMsgs(notesByTime_):
            msgs = []
            keys = notesByTime_.keys()
            keys.sort()
            volumes = []
            for key in keys:
                for note in notesByTime_[key]:
                    midikey, pos, endpos, vsti = note
                    msgs += [[pos, midikey, 100, vsti]]
                    msgs += [[endpos, midikey, 0, vsti]]

            #msgs = sorted(msgs+volumes, cmp=compare)
            msgs = sorted(msgs, cmp=compare)
            return msgs

        """
        메시지가 다 만들어 졌다면
        루프를 돈다. 쓰레드를 하나 더 할 필요는 없고 걍 뮤텍스 락을 걸고 한다.?
        아니다. 쓰레드를 하나 더 만들어서 해야 한다. 대신, 뮤텍스 락은 똑같은 걸 쓴다.

        기다린다. 음....... 일단 버퍼를 한 4096 길이로 해서 8번씩 루프를 돌면서 버퍼를 채우고
        4096이면 몇초지?
        4096짜리 버퍼를 2개 만들어서
        seconds / 2 만큼의 시간이 지나면 다른 버퍼를 채우고 이런다? 아니다.
        하나 채우고 플레이 하면서 그 도중에 또 채우고 기다렸다가 플레이된 게 끝나면 바로 또 그 버퍼에 채우고 이런다.
        frame = seconds * (samplingRate / 1000)


        플레이를 중단하면 현재 On된 노트를 모두 추적해서 off해줘야 한다.


        한개의 악기와 한개의 노트리스트에 대한 건 있으니
        이걸 한 번 루프 돌 때 여러 악기와 여러 노트리스트에 대해 돌면 된다.
        노트리스트를 시간을 기준으로 하나로 합치고 각 노트에 vst에 대한 링크를 둔다.
        """
        frame = 512.0
        samplingRate = 44100.0
        secondsPerBlock = frame / (samplingRate)
                    
        msgs = BuildMsgs(notesByTime)
        """
        음 set으로 각각의 vsti를 구해서 각각 인풋아웃풋 넘버에 따라 버퍼를 할당한다.
        bufferSize를 그냥 512로 한다.
        12
        """
        vstis = [msg[3] for msg in msgs]
        vstis = list(set(vstis))

        bufferSize = int(frame*8)
        outputs1 = [numpy.zeros((vstis[i].vstEff.number_of_outputs, bufferSize), dtype=numpy.float32) for i in range(len(vstis))]
        outputs2 = [numpy.zeros((vstis[i].vstEff.number_of_outputs, bufferSize), dtype=numpy.float32) for i in range(len(vstis))]


        nextPlayTime = 0
        curNotPlayingBuffers = outputs1
        curBufferIdx = 1
        idxidx = 0
        def StopAllNotes(playingNotesDict):
            if playingNotesDict:
                for vsti in playingNotesDict.iterkeys():
                    kVstMidiType = 1
                    kVstMidiEventIsRealTime = 1
                    vstMidiEvents = pyvst.VstMidiEvents()
                    vstMidiEvents.numEvents = len(playingNotesDict[vsti])
                    vstMidiEvents.reserved = 0
                    for msgIdx in range(len(playingNotesDict[vsti])):
                        playingNote = playingNotesDict[vsti][msgIdx]
                        midiEvent1 = pyvst.VstMidiEvent()
                        midiEvent1.type = kVstMidiType
                        midiEvent1.byteSize = 24
                        midiEvent1.deltaFrames = 0
                        midiEvent1.flags = kVstMidiEventIsRealTime
                        midiEvent1.noteLength = 0
                        midiEvent1.noteOffset = 0
                        midiEvent1.midiData1 = (0x90)
                        midiEvent1.midiData2 = (playingNote)
                        midiEvent1.midiData3 = (0x00)
                        midiEvent1.midiData4 = (0x00)
                        midiEvent1.detune = 0
                        midiEvent1.noteOffVelocity = 0
                        midiEvent1.reserved1 = 0
                        midiEvent1.reserved2 = 0
                        vstMidiEvents.events[msgIdx] = POINTER(pyvst.VstMidiEvent)(midiEvent1)

                    tempBuffer = numpy.zeros((vsti.vstEff.number_of_outputs, bufferSize), dtype=numpy.float32)
                    vsti.vstEff.ProcessMidi(vstMidiEvents)
                    vsti.vstEff.process_replacing_output(tempBuffer[:, i*512:(i+1)*512], 512)


        while msgs and self.playNotesMode:
            for i in range(bufferSize/512):
                curMsgs = []
                lastIdx = 0
                for msgIdx in range(len(msgs)):
                    lastIdx = msgIdx+1
                    msg = msgs[msgIdx]
                    deltaFrames = int((msg[0]-((idxidx*bufferSize/512+i)*secondsPerBlock*1000)) * (samplingRate/1000.0))
                    if deltaFrames < 512:
                        curMsgs += [(deltaFrames, msg[1], msg[2], msg[3])]
                    else:
                        lastIdx = msgIdx
                        break

                msgs = msgs[lastIdx:]

                if curMsgs:
                    """
                    vstis를 이용해서
                    메시지중에 vst가 같은 것들만 현재 버퍼에 넣고 보내고 이런다.
                    """
                    for vsti in vstis:
                        kVstMidiType = 1
                        kVstMidiEventIsRealTime = 1
                        vstMidiEvents = pyvst.VstMidiEvents()
                        curVSTMsgs = [msg for msg in curMsgs if msg[3] == vsti]
                        vstMidiEvents.numEvents = len(curVSTMsgs)
                        vstMidiEvents.reserved = 0
                        for msgIdx in range(len(curVSTMsgs)):
                            msg = curVSTMsgs[msgIdx]
                            if msg[2] >= 0.05: # volume
                                if vsti not in playingNotesDict:
                                    playingNotesDict[vsti] = []
                                playingNotesDict[vsti] += [msg[1]]
                            elif msg[2] < 0.05:
                                try:
                                    del playingNotesDict[vsti][playingNotesDict[vsti].index(msg[1])]
                                except:
                                    pass

                            midiEvent1 = pyvst.VstMidiEvent()
                            midiEvent1.type = kVstMidiType
                            midiEvent1.byteSize = 24
                            midiEvent1.deltaFrames = msg[0]
                            midiEvent1.flags = kVstMidiEventIsRealTime
                            midiEvent1.noteLength = 0
                            midiEvent1.noteOffset = 0
                            midiEvent1.midiData1 = (0x90)
                            midiEvent1.midiData2 = (msg[1])
                            midiEvent1.midiData3 = (msg[2])
                            midiEvent1.midiData4 = (0x00)
                            midiEvent1.detune = 0
                            midiEvent1.noteOffVelocity = 0
                            midiEvent1.reserved1 = 0
                            midiEvent1.reserved2 = 0
                            vstMidiEvents.events[msgIdx] = POINTER(pyvst.VstMidiEvent)(midiEvent1)

                        if len(curVSTMsgs):
                            vsti.vstEff.ProcessMidi(vstMidiEvents)

                for vstiIdx in range(len(vstis)):
                    vsti = vstis[vstiIdx]
                    vsti.vstEff.process_replacing_output(curNotPlayingBuffers[vstiIdx][:, i*512:(i+1)*512], 512)
                    curNotPlayingBuffers[vstiIdx][:, i*512:(i+1)*512] = self.ApplyEffect512(curNotPlayingBuffers[vstiIdx][:, i*512:(i+1)*512])
                    # TODO: 여기서 [:, 1:3] 이렇게 하면 길이 1짜리랑 2짜리랑 섞여서 미스매치 에러뜸.
                    # 
                    # TODO:vstis를 이용해서 이펙트들을 가져와서 그걸 써야함!
                    # TODO:만약 2 개 이상의 vsti가 1개의 fx를 공유하면 그 2개의 vsti웨이브 파형을 합쳐서 1개로 보내야 함... 리버브 등등.
                    #
                    #
                    #inputMono[0:1, i*512:(i+1)*512] = curNotPlayingBuffer[0:1, i*512:(i+1)*512]/2.0 + curNotPlayingBuffer[1:2, i*512:(i+1)*512]/2.0
                    # self.panel.vstFX.vstEff.process_replacing(inputMono[:, i*512:(i+1)*512], outputMono[:, i*512:(i+1)*512])
                    #  curNotPlayingBuffer[0:1, i*512:(i+1)*512] = outputMono[0][i*512:(i+1)*512]
                    #   curNotPlayingBuffer[1:2, i*512:(i+1)*512] = outputMono[0][i*512:(i+1)*512]
                # number of output등을 잘 살펴서 모노인지 스테레오인지 구별해서 해야함.
            # 일단 아웃풋이 1개인 것과 2개인 것에 대해서만 한다.
            if len(curNotPlayingBuffers[0]) >= 2:
                outputBuffer = curNotPlayingBuffers[0]
            elif len(curNotPlayingBuffers[0]) == 1:
                outputBuffer = curNotPlayingBuffers[0], curNotPlayingBuffers[0]
            for buffer in curNotPlayingBuffers[1:]:
                if len(buffer) >= 2:
                    outputBuffer[0] = outputBuffer[0] + buffer[0]
                    outputBuffer[1] = outputBuffer[1] + buffer[1]
                elif len(buffer) == 1:
                    outputBuffer[0] = outputBuffer[0] + buffer[0]
                    outputBuffer[1] = outputBuffer[1] + buffer[0]

            frames = bufferSize
            outputBuffer = self.GetInterleaved(outputBuffer, frames)
            while nextPlayTime > pypm.Time():
                if not self.playNotesMode:
                    StopAllNotes(playingNotesDict)
                    self.panel.playing = False
                    return
            self.SoundOut(outputBuffer, frames)
            nextPlayTime = pypm.Time() + (bufferSize/512)*secondsPerBlock*1000
            if curBufferIdx == 1:
                curBufferIdx = 2
                curNotPlayingBuffers = outputs2
            elif curBufferIdx == 2:
                curBufferIdx = 1
                curNotPlayingBuffers = outputs1

            idxidx += 1
        
        StopAllNotes(playingNotesDict)
        self.panel.playing = False
        self.playNotesMode = False

    def SwitchInstrumentCmd(self):
        self.setParams = []
        self.paramCallbacks = []
        self.prevProgram = 0
        self.programNumber = 0
        if self.vstEff:
            output = numpy.zeros((self.vstEff.number_of_outputs, 512), dtype=numpy.float32)

            ni = self.vstEff.number_of_inputs
            i = 0
            bufferSize = 512
            if ni:
                input = numpy.zeros((ni, bufferSize), dtype=numpy.float32)
            for j in range(int(512.0*10/44100.0)):
                if ni:
                    self.vstEff.process_replacing(input[:, i*512:(i+1)*512], output[:, i*512:(i+1)*512])
                else:
                    self.vstEff.process_replacing_output(output[:, i*512:(i+1)*512], 512)

        for fx in self.fxs:
            no = fx.number_of_outputs
            ni = fx.number_of_inputs
            o = numpy.zeros((no, 512), dtype=numpy.float32)
            i = numpy.zeros((ni, 512), dtype=numpy.float32)
            if ni == 1 and no == 1:
                for i in range(int(512.0*10/44100.0)):
                    fx.process_replacing(i[0:1, i*512:(i+1)*512], o[0:1, i*512:(i+1)*512])

        self.vstEff = self.newVST
        self.fxs = self.newFX
        self.newVST = None
        self.newFX = None
        self.switchInstrument = False

    def SwitchInstrument(self, vstEff, fxchain):
        #여기서 10초 정도 읽어와 버리고 바꾼다.
        # 아니 그냥 버퍼를 리셋해버리는 건 없나?

        self.switchInstrument = True
        self.newVST = vstEff
        self.newFX = fxchain

    def PlayNote(self, key):
        self.playNote = key

    def ApplyEffects(self, output, bufferSize):
        assert self.IsMultipleOf512(bufferSize), "Buffer size must be multiple of 512(%d)" % bufferSize
        assert bufferSize >= 512, "Buffer size must be greater than or equal to 512(%d)" % bufferSize
        outputTemp = numpy.zeros((self.vstEff.number_of_outputs, bufferSize), dtype=numpy.float32)
        outputTemp2 = numpy.zeros((2, bufferSize), dtype=numpy.float32)
        outputStereo = numpy.zeros((2, bufferSize), dtype=numpy.float32)
        vstini = self.vstEff.number_of_outputs

        for i in range(bufferSize/512):
            if vstini == 1:
                outputStereo[0:1, i*512:(i+1)*512] = output[0:1, i*512:(i+1)*512]
                outputStereo[1:2, i*512:(i+1)*512] = output[0:1, i*512:(i+1)*512]
            else:
                outputStereo = output # can be more than stereo but only two channels will be used
            for fx in self.fxs:
                no = fx.number_of_outputs
                ni = fx.number_of_inputs
                if ni == 1 and no == 1:
                    inputTemp = numpy.zeros((1, 512), dtype=numpy.float32)
                    inputTemp[0:1, i*512:(i+1)*512] = (outputStereo[0:1, i*512:(i+1)*512]/2.0) + (outputStereo[1:2, i*512:(i+1)*512]/2.0)
                    fx.process_replacing(inputTemp[0:1, i*512:(i+1)*512], outputTemp2[:, i*512:(i+1)*512])
                    outputStereo[0:1, i*512:(i+1)*512] = outputTemp2[0:1, i*512:(i+1)*512]
                    outputStereo[1:2, i*512:(i+1)*512] = outputTemp2[0:1, i*512:(i+1)*512]
                    outputTemp2 = numpy.zeros((2, bufferSize), dtype=numpy.float32)
                elif ni == 2 and no == 2:
                    fx.process_replacing(outputStereo[:, i*512:(i+1)*512], outputTemp2[:, i*512:(i+1)*512])
                    outputStereo = outputTemp2
                    outputTemp2 = numpy.zeros((2, bufferSize), dtype=numpy.float32)
                elif ni == 1 and no == 2:
                    inputTemp = numpy.zeros((1, 512), dtype=numpy.float32)
                    inputTemp[0:1, i*512:(i+1)*512] = outputStereo[0:1, i*512:(i+1)*512]/2.0 + outputStereo[1:2, i*512:(i+1)*512]/2.0
                    fx.process_replacing(inputTemp[0:1, i*512:(i+1)*512], outputStereo[:, i*512:(i+1)*512])
                elif ni == 4 and no == 2: # density mk ii, etc
                    inputTemp = numpy.zeros((4, 512), dtype=numpy.float32)
                    inputTemp[0:1, i*512:(i+1)*512] = outputStereo[0:1, i*512:(i+1)*512]
                    inputTemp[1:2, i*512:(i+1)*512] = outputStereo[1:2, i*512:(i+1)*512]
                    inputTemp[2:3, i*512:(i+1)*512] = outputStereo[0:1, i*512:(i+1)*512]
                    inputTemp[3:4, i*512:(i+1)*512] = outputStereo[1:2, i*512:(i+1)*512]
                    fx.process_replacing(inputTemp[0:4, i*512:(i+1)*512], outputStereo[:, i*512:(i+1)*512])
                    # how do I do it???????????????????????
                    # just duplicate it into two stereos(four channels)?
                    # Is it surround sound? maybe ill just copy it and be done with it...
                else:
                    assert False, "function not implemented for this vst fx(number of input: %d, number of output: %d)" % (ni, no)

        return outputStereo

    def ApplyEffect512(self, output):
        return self.ApplyEffects(output, 512)

    def IsMultipleOf512(self, number):
        number = float(number) / 512.0
        if (number - math.floor(number)) < 0.0001:
            return True
        else:
            return False

    def ReadVSTi(self, bufferSize=512):
        assert self.IsMultipleOf512(bufferSize), "Buffer size must be multiple of 512(%d)" % bufferSize
        assert bufferSize >= 512, "Buffer size must be greater than or equal to 512(%d)" % bufferSize
        output = numpy.zeros((self.vstEff.number_of_outputs, bufferSize), dtype=numpy.float32)
        ni = self.vstEff.number_of_inputs
        if ni:
            input2 = numpy.zeros((ni, bufferSize), dtype=numpy.float32)
        else:
            input2 = None
        numiter = bufferSize/512
        for i in range(numiter):
            if ni:
                #self.vstEff.process_replacing(input2[:, i*512:(i+1)*512], output[:, i*512:(i+1)*512])
                self.vstEff.process(input2[:, i*512:(i+1)*512], output[:, i*512:(i+1)*512])
            else:
                self.vstEff.process_replacing_output(output[:, i*512:(i+1)*512], 512)
        return output

    def GetInterleaved(self, output, frames):
        interleaved = numpy.zeros(frames*2, dtype=numpy.float32)
        for i in range(2):
            interleaved[i::2] = output[i]
        return interleaved
    def SoundOut(self, interleaved, frames):
        self.stream.write(interleaved.tostring(), num_frames=frames)

    def run(self): 
        self.prevTime = pypm.Time()
        frame = 512.0
        samplingRate = 44100.0
        secondsPerBlock = frame / (samplingRate)
        self.prevTime = pypm.Time()
        self.prevTime2 = pypm.Time()

        while not VSTSoundWorker.quit:
            if self.switchInstrument:
                self.playNote = None
                self.stopNote = False
                if self.vstEff:
                    self.StopNoteCmd()
                    self.ReadVSTi()
                self.SwitchInstrumentCmd()

            if self.vstEff:
                if self.playNotesMode:
                    self.PlayNotesCmd()
                def Out():
                    output = self.ReadVSTi()
                    output = self.ApplyEffect512(output)
                    frames = 512
                    interleaved = numpy.zeros(frames*2, dtype=numpy.float32)
                    for i in range(2):
                        interleaved[i::2] = output[i]
                    self.stream.write(interleaved.tostring(), num_frames=frames)



                progN = self.programNumber
                if progN != self.prevProgram:
                    self.prevProgram = progN
                    self.vstEff.set_program(progN)
                    output = self.ReadVSTi()
                    output = self.ApplyEffect512(output)
                    frames = 512
                    interleaved = numpy.zeros(frames*2, dtype=numpy.float32)
                    for i in range(2):
                        interleaved[i::2] = output[i]
                    self.stream.write(interleaved.tostring(), num_frames=frames)

                for func in self.paramCallbacks:
                    func()
                self.paramCallbacks = []

                for pair in self.setParams:
                    self.vstEff.set_parameter(*pair)

                if self.stopNote:
                    self.playNote = None
                    self.StopNoteCmd()
                    Out()
                elif self.playNote:
                    self.StopNoteCmd()
                    #Out()
                    if self.prevPlayNoteTime + 50 < pypm.Time():
                        self.prevPlayNoteTime = pypm.Time()
                        key = self.playNote
                        self.playNote = None
                        self.PlayNoteCmd(key)
                    # 아....뭐지. 한 쓰레드에서 펑션을 부른다고 "연속적"인 게 아닌가보다.
                    # 파이썬이 어떻게 돌아가서 이러는지는 몰라도 PlayNoteCmd에서 사운드 아웃을 해주면 에러가 안나고
                    # PlayNoteCmd따로, 여기서 Out따로 하면 에러난다. ㅡㅡ;;;; 뭥미.......
                    # 음.....파이썬을 애초에 이용한다는 게 에러를 부르는 것 같다. 콜링 컨벤션이라던가 이런게 다르던지 뭔가 문제가 있어서
                    # 뭔가를 따로따로 하면 DLL을 콜링하는 거에서 뭔가 문제가 생겨서 에러가 나나놉다.
                    # 흠..... 같이 부르니까 뭔가 에러가 안 난다.

                if self.prevTime + 110 < pypm.Time() and self.stopped:
                    self.vstEff.idle()
                    self.prevTime = pypm.Time()

                Out()

                while self.prevTime2 + secondsPerBlock*500 > pypm.Time():
                    pass
                self.prevTime2 = pypm.Time()

        self.vstEff.close()
        self.stream.close()
        self.pyAudio.terminate()
        

"""
class VSTSoundWorker(Thread):
    quit = False
    def __init__(self):
        Thread.__init__(self)
    

    def PlayNotes(self, panel, notes, pattern):
        pass
    def RenderNotes(self, notes):
        pass
    def StopNotes(self):
        pass

    def StopNote(self):
        pass

    def PlayNote(self, key):
        pass


"""

def DumpVSTData(fileName):
    vstEff = pyvst.VSTPlugin(fileName)
    data = vstEff.IsSynth(), vstEff.get_name()
    del vstEff
    return data

        

class Mixer(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        self.setWindowTitle("Mixer")
        self.fx = VSTFXPanel(self)
        self.panels = MixerScrollArea(self)
        extensionLayout = QtGui.QGridLayout()
        extensionLayout.setMargin(5)
        extensionLayout.addWidget(self.panels, 0, 0)
        extensionLayout.addWidget(self.fx, 0, 1)
        extensionLayout.setColumnStretch(0, 1)
        self.setLayout(extensionLayout)

    def minimumSizeHint(self):
        return QtCore.QSize(400, 400)

    def sizeHint(self):
        return QtCore.QSize(400, 400)
    def closeEvent(self, ev):
        if not g_WindowClosed:
            ev.ignore()

class MixerScrollArea(QtGui.QScrollArea):
    def __init__(self, parent):
        QtGui.QScrollArea.__init__(self, parent)
        self.parent_ = parent
        self.mixerPanels = mixerPanels = MixerPanels(self)
        self.setWidget(mixerPanels)


class OpenedWindow:
    def __init__(self):
        self.wnd = []

    def AddWnd(self, wnd):
        self.wnd += [wnd]
    def Del(self, wnd):
        try:
            del self.wnd[self.wnd.index(wnd)]
        except:
            pass
    def CloseAll(self):
        for wnd in self.wnd:
            wnd.close()
        self.wnd = []
class MixerPanels(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        global MixerPanelsSingleton 
        MixerPanelsSingleton = self
        self.panels = [MixerPanel(self, "Master VST FX")] + [MixerPanel(self, "VST FX %d" % (i)) for i in range(100)]
        self.fx = parent.parent_.fx
        buttonsL = QtGui.QHBoxLayout()
        buttonsL.setMargin(0)
        buttonsL.setSpacing(0)
        for panel in self.panels:
            buttonsL.addWidget(panel)
        self.setLayout(buttonsL)

        self.selectedPanel = self.panels[0]
        self.panels[0].selected = True

    def GetFXs(self, fxNum):
        masterWnds = self.panels[0].effects
        if fxNum != -1:
            pan = self.panels[fxNum+1]
            effWnds = pan.effects
            fxs = [wnd.vstEff for wnd in effWnds+masterWnds]
        else:
            fxs = [wnd.vstEff for wnd in masterWnds]
        """
        모든 윈도우 닫으면 다시 열 수 있는 방법을 만든다.
        패턴매니져나 인스트루먼트 패널, 믹서 등은 파괴될 때 안에 내용물을 따로 저장해서 파괴 안되게 하고
        생성시에 실질적인 악기는 생성하지 않게 하고 이미 생성된 악기를 전달해주기만 하게 바꾼다.
        또는......... 아예 윈도우가 닫히지 않게 만들면 되겠네? (....)
        """
        return fxs

    def minimumSizeHint(self):
        return QtCore.QSize(25*101, 360)

    def sizeHint(self):
        return QtCore.QSize(25*101, 360)


class FXQListWidget(QtGui.QListWidget):
    def __init__(self, parent):
        QtGui.QListWidget.__init__(self)
        self.parent_ = parent
        self.popMenu = QtGui.QMenu( self ) 
        self.popMenu.addAction("Show GUI", self.OnShow) 
        self.popMenu.addAction("Insert Here", self.OnInsert) 
        self.popMenu.addAction("Remove", self.OnRemove) 
        self.popMenu.addAction("Move Up", self.OnMoveUp) 
        self.popMenu.addAction("Move Down", self.OnMoveDown) 
    def mousePressEvent(self, ev):
        QtGui.QListWidget.mousePressEvent(self, ev)
        if ev.button() == RMB:
            if self.parent_.selectedItem:
                print self.parent_.view.indexFromItem(self.parent_.selectedItem).row()
                txt = str(self.parent_.selectedItem.text())
                print txt
                self.popMenu.exec_( self.mapToGlobal(ev.pos()) ) 

    def OnShow(self):
        pass
    def OnInsert(self):
        pass
    def OnRemove(self):
        pass
    def OnMoveUp(self):
        pass
    def OnMoveDown(self):
        pass

class VSTFXPanel(QtGui.QWidget):
    def __init__(self, parent):
        self.parent = parent
        QtGui.QWidget.__init__(self, parent)
        self.parent_ = parent
        extensionLayout = QtGui.QGridLayout()
        extensionLayout.setMargin(0)


        self.view = view = FXQListWidget(self)
        QtCore.QObject.connect(view, QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.OnItemSelect)
        QtCore.QObject.connect(view, QtCore.SIGNAL("itemActivated(QListWidgetItem *)"), self.OnItemDoubleClick)
        
        """
        lst = ["test.dll", "test2", "test3"]
        for item in lst:
            view.addItem(QtCore.QString(item))
        """
        btn1 = QtGui.QPushButton("Add")
        self.connect(btn1, QtCore.SIGNAL("clicked()"),
                     self.OnAdd)

        extensionLayout.addWidget(view, 0, 0)
        extensionLayout.addWidget(btn1, 1, 0)
        extensionLayout.setRowStretch(0, 1)
        self.setLayout(extensionLayout)


        """
        btn = wx.Button(self, wx.NewId(), "Add", pos=(0, 300))
        self.Bind(wx.EVT_BUTTON, self.OnAdd, btn)
        """

        #self.lb1.SetSelection(3)
       # self.lb1.Append("with data", "This one has data");
        #Insert(self, item, pos, clientData=None) 
       # self.lb1.SetClientData(2, "This one has data");
        #o 더블클릭하면 GUI를 보여주고 선택하고 오른쪽버튼 누르면 컨텍스트 메뉴에서 여기에 추가 삭제 이동위아래를 넣는다.
        """
HitTest(self, pt) 
Test where the given (in client coords) point lies

Parameters:
pt 
           (type=Point) 
        
        오른족 버튼으로 힛테스트를 해서 아템을 가져옴.
        팝업메뉴에 현재 선택된 아이템의 파일이름을 보여준다. 메뉴아이템을disable하면 되는데...
        """
        self.selectedItem = None
    def OnItemSelect(self, item):
        self.selectedItem = item
    def OnItemDoubleClick(self, item):
        self.selectedItem = item
    def minimumSizeHint(self):
        return QtCore.QSize(100, 400)

    def sizeHint(self):
        return QtCore.QSize(100, 400)
    def OnItemChange(self, item):
        pass
    def OnAdd(self):
        vsti = SettingsSingleton.GetData("VSTEffects")
        vsti.sort()
        dlg = SingleChoiceDialogManager("Select VST Effect", "Select VST Effect", vsti)
        result = dlg.DoModal()
        if result:
            fileName = result[1]
            fileName = SettingsSingleton.GetData("VSTPath") + "/" + fileName
            
            pan = self.parent_.panels.mixerPanels.selectedPanel
            if pan:
                pan.effects += [VSTWindow(fileName, pan, False)]
                name = pan.effects[-1].vstEff.get_name()
                if not name:
                    name = result[1][:-4]
                self.view.addItem(name)
                instpan = PianoRollSingleton.GetCurInstrument()
                if instpan:
                    fxs = MixerPanelsSingleton.GetFXs(instpan.vst.fxNum)
                    VSTThreadSingleton.SwitchInstrument(instpan.vst.vstEff, fxs)
                    

    def EvtListBox(self, evt):
        pass
    def EvtListBoxDClick(self, evt):
        pass

    def EvtRightButton(self, evt):
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
            self.popupID3 = wx.NewId()
            self.popupID4 = wx.NewId()
            self.popupID5 = wx.NewId()
            self.popupID6 = wx.NewId()
            self.popupID7 = wx.NewId()
            self.popupID8 = wx.NewId()
            self.popupID9 = wx.NewId()

            self.Bind(wx.EVT_MENU, lambda evt: None, id=self.popupID1)
            self.Bind(wx.EVT_MENU, self.OnShow, id=self.popupID2)
            self.Bind(wx.EVT_MENU, self.OnAdd, id=self.popupID3)
            self.Bind(wx.EVT_MENU, self.OnRemove, id=self.popupID4)
            self.Bind(wx.EVT_MENU, self.OnMoveUp, id=self.popupID5)
            self.Bind(wx.EVT_MENU, self.OnMoveDown, id=self.popupID6)
            """

            self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
            self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
            self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
            self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)
            self.Bind(wx.EVT_MENU, self.OnPopupSix, id=self.popupID6)
            self.Bind(wx.EVT_MENU, self.OnPopupSeven, id=self.popupID7)
            self.Bind(wx.EVT_MENU, self.OnPopupEight, id=self.popupID8)
            self.Bind(wx.EVT_MENU, self.OnPopupNine, id=self.popupID9)
            """

        pos = evt.GetPosition()
        selection = self.lb1.HitTest(pos)
        if selection != -1:
            self.lb1.SetSelection(selection)
            selections = self.lb1.GetSelections()
            fileName = self.lb1.GetString(selections[0])
            # make a menu
            menu = wx.Menu()
            # Show how to put an icon in the menu
            item = wx.MenuItem(menu, self.popupID1,fileName)
            item.Enable(False)
            menu.AppendItem(item)
            menu.AppendSeparator()
            menu.AppendItem(wx.MenuItem(menu, self.popupID2,"Show GUI"))
            menu.AppendItem(wx.MenuItem(menu, self.popupID3,"Insert Here"))
            menu.AppendItem(wx.MenuItem(menu, self.popupID4,"Remove"))
            menu.AppendItem(wx.MenuItem(menu, self.popupID5,"Move Up"))
            menu.AppendItem(wx.MenuItem(menu, self.popupID6,"Move Down"))
            # add some other items
            """
            menu.Append(self.popupID2, "Two")
            menu.Append(self.popupID3, "Three")
            menu.Append(self.popupID4, "Four")
            menu.Append(self.popupID5, "Five")
            menu.Append(self.popupID6, "Six")
            # make a submenu
            sm = wx.Menu()
            sm.Append(self.popupID8, "sub item 1")
            sm.Append(self.popupID9, "sub item 1")
            menu.AppendMenu(self.popupID7, "Test Submenu", sm)
            """


            # Popup the menu.  If an item is selected then its handler
            # will be called before PopupMenu returns.
            self.PopupMenu(menu)
            menu.Destroy()


"""
VSTFX를 추가하고
연결을...

오른쪽클릭으로 추가,이동,삭제
뭐 콤보박스 이런거 쓰지 말고 Label그린다.
추가는 vSTi추가랑 똑같은 다이알로그
아...리스트박스에 추가해야겠다.
scrolledpanel로 믹서패널을 넣고 오른쪽에다가 vstfx 리스트박스를 넣자.

Mixer
    VSTFX(scrolledpanel)
        listBox for fx
    MixerPanels
        mixer panel
            knobs
            meters
"""
class MixerPanel(QtGui.QWidget):
    def __init__(self, parent, title):
        QtGui.QWidget.__init__(self, parent)
        self.ldragging = False
        self.knob = Knob(self)
        self.knob.move(0, 80)
        self.effects = []
        self.parent_ = parent
        self.selected = False
        self.titleTxt = title

    def minimumSizeHint(self):
        return QtCore.QSize(25, 350)

    def sizeHint(self):
        return QtCore.QSize(25, 350)


    def mousePressEvent(self, ev):
        if ev.button() == LMB:
            if self.parent_.selectedPanel:
                self.parent_.selectedPanel.selected = False
                self.parent_.selectedPanel.repaint()
            self.parent_.selectedPanel = self

            self.parent_.fx.view.clear()
            for effWnd in self.effects:
                self.parent_.fx.view.addItem(effWnd.vstEff.get_name())
            self.selected = True
            self.repaint()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self.Draw(painter)
    def Draw(self, painter):
        # help text라는 컨트롤이 있으면 그걸 쓴다. knob의 값을 거기서 보여준다.
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        color = self.palette().background().color()
        color = color.red(), color.blue(), color.green()
        size = self.size()
        w = size.width()-1
        h = size.height()-1

        if self.selected:
            col = QtGui.QColor(color[0]-10, color[1]-10, color[2]-10)
            painter.setPen(QtGui.QPen(col))
            painter.setBrush(QtGui.QBrush(col))
            rect = QtCore.QRect(0, 0, w, h)
            painter.drawRect(rect)

        col = QtGui.QColor(255, 255, 255)
        painter.setPen(QtGui.QPen(col))
        painter.setBrush(QtGui.QBrush(col))
        painter.drawLine(0, 0, w, 0)
        col = QtGui.QColor(color[0]-30, color[1]-30, color[2]-30)#"#a5b84c"
        painter.setPen(QtGui.QPen(col))
        painter.setBrush(QtGui.QBrush(col))
        painter.drawLine(0, h, w, h)
        col = QtGui.QColor(255, 255, 255)
        painter.setPen(QtGui.QPen(col))
        painter.setBrush(QtGui.QBrush(col))
        painter.drawLine(0, 0, 0, h)
        col = QtGui.QColor(color[0]-30, color[1]-30, color[2]-30)#"#a5b84c"
        painter.setPen(QtGui.QPen(col))
        painter.setBrush(QtGui.QBrush(col))
        painter.drawLine(w, 0, w, h)

        col = QtGui.QColor(0, 0, 0)#"#a5b84c"
        painter.setPen(QtGui.QPen(col))
        painter.setBrush(QtGui.QBrush(col))
        painter.save()
        painter.translate(w/3, 3)
        painter.rotate(90)
        painter.drawText(0, 0, self.titleTxt)
        painter.restore()



class VSTSettingsWindow(QtGui.QWidget):
    def __init__(self, parent, vstEff, vsti=True):
        super(VSTSettingsWindow, self).__init__(ParentFrameSingleton, size=QtCore.QSize(PatternManagerWidth, 400))
        self.parent_ = parent
        self.setWindowTitle(vstEff.get_name() + " Settings")

        self.mdi = ParentFrameSingleton.AddSubWindow(self)
        #win = ParentFrameSingleton.NewVSTGUIChild(vstEff.get_name() + " Settings")
        self.vstEff = vstEff
        self.isVSTi = vsti

        """
        fgs = wx.BoxSizer(wx.VERTICAL)
        cc = self.MakeLCCombo()
        cc.SetPopupMaxHeight(250)
        fgs.Add(cc, 0, wx.ALL, 10)
        self.SetAutoLayout(True)
        self.SetSizer(fgs)
        self.Layout()
        """
        extensionLayout = QtGui.QGridLayout()
        extensionLayout.setMargin(5)




        self.combo1=QtGui.QComboBox(parent=self, size=QtCore.QSize(150, 30))
        for program_index in range(self.vstEff.number_of_programs):
            self.vstEff.set_program(program_index)
            program_name = self.vstEff.get_program_name()
            self.combo1.addItem(program_name)
        self.vstEff.set_program(0)
        self.connect(self.combo1, QtCore.SIGNAL('activated(int)'), self.OnItemChange)
        self.combo1.setCurrentIndex(self.parent_.pNum)

        if vsti:
            self.combo2=QtGui.QComboBox(parent=self, size=QtCore.QSize(150, 30))
            self.combo2.addItem(QtCore.QString("None"))
            for i in range(100):
                self.combo2.addItem(`i`)
            self.connect(self.combo2, QtCore.SIGNAL('activated(int)'), self.OnFXItemChange)
        self.combo2.setCurrentIndex(self.parent_.fxNum+1)


        label = QtGui.QLabel("Preset:")
        extensionLayout.addWidget(label, 0, 0)
        extensionLayout.addWidget(self.combo1, 1, 0)

        label = QtGui.QLabel("")
        if vsti:
            label = QtGui.QLabel("VST FX number which this is connected to:")
            extensionLayout.addWidget(label, 2, 0)
            extensionLayout.addWidget(self.combo2, 3, 0)

            extensionLayout.addWidget(label, 4, 0)
            extensionLayout.setRowStretch(4, 1)
        else:
            extensionLayout.addWidget(label, 2, 0)
            extensionLayout.setRowStretch(2, 1)

        self.setLayout(extensionLayout)

    def closeEvent(self, ev):
        OpenedWindowSingleton.Del(self)
        self.mdi.close()
        self.mdi = None
        self.parent_.vstSettings = None
    def minimumSizeHint(self):
        return QtCore.QSize(300, 400)

    def sizeHint(self):
        return QtCore.QSize(300, 400)

    def OnFXItemChange(self, listItem):
        self.parent_.fxNum = self.combo2.currentIndex()-1
    def OnItemChange(self, listItem):
        self.parent_.pNum = self.combo1.currentIndex()
        self.OnValueSelect(self.combo1.currentIndex())
    def OnValueSelect(self, value):
        if self.vstEff == VSTThreadSingleton.vstEff:
            VSTThreadSingleton.programNumber = value
        else:
            self.vstEff.set_program(value)
        #TODO FX같은 거나 나중에 VSTThread에 모든 VST를 다 넣을 때엔 그 때에 맞게 처리한다. 지금은 테스트중...

       

class VSTKnob(QtGui.QWidget):
    # knob을 그대로 카피했다. 음...카피앤 페이스트는 참 안좋은데 귀찮으니 어쩔 수 없다.
    # 여기에 뭐랄까 "제목" 하고 값을 글씨로 표시하는 거랑 뭐 변경을 VST에 적용시키는 거
    # 아니면 그냥 기존의 Knob을 그대로 써도 되겠군?
    # 근데 하나하나 갖다대기 불편하니까 새로 만들자 제목이랑 값 표시해서.
    def __init__(self, vstEff, paramIndex, parent):
        QtGui.QWidget.__init__(self, parent)
        self.vstEff = vstEff
        self.value = 0
        self.pi = paramIndex
        self.param_display = ""
        self.param_label = ""
        self.pvalue = 0.0
        self.parent = parent
        self.paramName = self.vstEff.get_parameter_name(self.pi)
        self.SetMinMax(0.0, 1.0)
        self.ldragging = False
        self.startValue = self.value
        self.accuracy = 0.5/100.0
        self.fractionLen = 3
        self.ttstr = ''
        self.SetToolTipString(self.paramName)
        param_index = self.pi
        self.param_display = self.vstEff.get_parameter_display(param_index)
        self.param_label = self.vstEff.get_parameter_label(param_index)
        self.pvalue = self.vstEff.get_parameter(param_index)
        self.SetValue(self.pvalue)
        
    def minimumSizeHint(self):
        return QtCore.QSize(100, 50)

    def sizeHint(self):
        return QtCore.QSize(100, 50)

    def GetParam(self):
        def Go():
            param_index = self.pi
            self.param_display = self.vstEff.get_parameter_display(param_index)
            self.param_label = self.vstEff.get_parameter_label(param_index)
            self.pvalue = self.vstEff.get_parameter(param_index)

        if self.vstEff == VSTThreadSingleton.vstEff:
            VSTThreadSingleton.GetParamCallBack(Go)
        else:
            param_index = self.pi
            self.param_display = self.vstEff.get_parameter_display(param_index)
            self.param_label = self.vstEff.get_parameter_label(param_index)
            self.pvalue = self.vstEff.get_parameter(param_index)

        return self.param_display, self.param_label, self.pvalue

    def SetParam(self, value):
        if self.vstEff == VSTThreadSingleton.vstEff:
            VSTThreadSingleton.SetParam(self.pi, value)
        else:
            self.vstEff.set_parameter(self.pi, value)

    def SetToolTipString(self, ttstr):
        self.ttstr = ttstr
    def event(self, event):
        if event.type() == QtCore.QEvent.ToolTip:
            QtGui.QToolTip.hideText()
            QtGui.QToolTip.showText(event.globalPos(), self.ttstr)
            return True
        else:
            QtGui.QToolTip.hideText()

        return super(self.__class__, self).event(event)

    def SetStatVal(self):
        valText = `self.value`
        decPnt = valText.find(".")
        if decPnt != -1:
            valText = valText[:decPnt+self.fractionLen+1]
        StatusBarSingleton.showMessage(valText)
    def enterEvent(self, ev):
        self.SetStatVal()
    def leaveEvent(self, event):
        StatusBarSingleton.showMessage('')

    def BindRDown(self, func): # func(knob)
        self.binds += [func]

    def mouseMoveEvent(self, ev):
        curPos = ev.pos().y()
        offset = (curPos-self.startPos)
        offset = float(offset)*((self.GetMaxValue()-self.GetMinValue())*self.accuracy)
        value = self.startValue-offset
        if value > self.GetMaxValue():
            value = self.GetMaxValue()
        if value < self.GetMinValue():
            value = self.GetMinValue()
        self.SetValue(value)
        self.SetStatVal()
    def mousePressEvent(self, ev):
        if ev.button() == LMB:
            self.startPos = ev.pos().y()
            self.startValue = self.value
        elif ev.button() == RMB:
            for func in self.binds:
                func(ev, self)
        """
        pos = event.GetPosition().Get()

        if pos[0] < 23 and pos[1] < 23:
            #set value to status
            SetStatVal()
        else:
            pass
            #clear status? no. it will conflict with others
            # but if you use queueing system it will be very good. clearing stat msgs while not in the rect..
        if event.LeftDown():
            self.SetFocus()
            self.CaptureMouse()
            #self.drawing = True
            self.startPos = event.GetPosition().Get()[1]
            self.startValue = self.value
            self.ldragging = True

        elif event.Dragging():
            if self.ldragging:
                pass

        elif event.LeftUp():
            TopWindowSingleton.SetStatusText('', 0)
            self.ldragging = False
            try:
                self.ReleaseMouse()
            except:
                pass
        """

    def GetValue(self):
        return self.value
    def SetValue(self, val):
        self.value = val
        self.repaint()
        self.SetParam(val)
    def SetMinMax(self, min, max):
        self.minmax = (min, max)
    def GetMinValue(self):
        return self.minmax[0]
    def GetMaxValue(self):
        return self.minmax[1]
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self.Draw(painter)

    def Draw(self, painter):
        painter.drawText(QtCore.QRect(28, 0, 100-28, 15), QtCore.Qt.AlignLeft, self.paramName)
        disp, label, value = self.GetParam()
        painter.drawText(QtCore.QRect(28, 15, 100-28, 15), QtCore.Qt.AlignLeft, disp)
        painter.drawText(QtCore.QRect(28, 30, 100-28, 15), QtCore.Qt.AlignLeft, label)


        bmp = LoadBitmap('knob.png')
        painter.drawPixmap(1,1,bmp)
        value = self.GetValue()
        min = self.GetMinValue()
        max = self.GetMaxValue()
        normalizedMax = max - min
        value -= min
        value = float(value) / float(normalizedMax)
        maxTheta = (math.pi/4)*6
        theta = maxTheta*value
        #theta *= -1
        theta += 3*math.pi/4
        #minTheta = (math.pi/4)*5
        #maxTheta = (math.pi/4)*7
        # 일단 theta값을 뒤집고(-1곱합?) +3*math.pi/4 해주면 된다.
        x1 = 11+1
        y1 = 11+1
        x2 = int(math.cos(theta)*9)+x1
        y2 = int(math.sin(theta)*9)+y1
        col = QtGui.QColor(0, 0, 0)
        painter.setPen(QtGui.QPen(col))
        painter.setBrush(QtGui.QBrush(col))
        painter.drawLine(x1, y1, x2, y2)

        color = self.palette().background().color()
        color = color.red(), color.blue(), color.green()
        w, h = 100-1, 50-1
        col = QtGui.QColor(255, 255, 255)
        painter.setPen(QtGui.QPen(col))
        painter.setBrush(QtGui.QBrush(col))
        painter.drawLine(0, 0, w, 0)
        col = QtGui.QColor(color[0]-30, color[1]-30, color[2]-30)#"#a5b84c"
        painter.setPen(QtGui.QPen(col))
        painter.setBrush(QtGui.QBrush(col))
        painter.drawLine(0, h, w, h)
        col = QtGui.QColor(255, 255, 255)
        painter.setPen(QtGui.QPen(col))
        painter.setBrush(QtGui.QBrush(col))
        painter.drawLine(0, 0, 0, h)
        col = QtGui.QColor(color[0]-30, color[1]-30, color[2]-30)#"#a5b84c"
        painter.setPen(QtGui.QPen(col))
        painter.setBrush(QtGui.QBrush(col))
        painter.drawLine(w, 0, w, h)



class VSTGUILessWindow(QtGui.QWidget):
    def __init__(self, parent, vstEff):
        QtGui.QWidget.__init__(self, parent)
        self.vstEff = vstEff
        gridL = QtGui.QGridLayout()
        gridL.setMargin(0)

        self.setWindowTitle(vstEff.get_name())
        parent.gui = self
        knobs = self.knobs = [VSTKnob(vstEff, i, self) for i in range(vstEff.get_number_of_parameters())]
        numKnobs = len(knobs)
        numCols = 4
        numRows = int(math.ceil(numKnobs/float(numCols)))
        self.size_ = (numCols*(100+5), numRows*(50+6))
        """
        ################## -> ####
                              ####
                              ####
        """
        row = 1
        col = 1
        for i in range(numKnobs):
            gridL.addWidget(knobs[i], row, col)
            col += 1
            if col > numCols:
                col = 1
                row += 1

        self.setLayout(gridL)


    def minimumSizeHint(self):
        return QtCore.QSize(*self.size_)

    def sizeHint(self):
        return QtCore.QSize(*self.size_)

class VSTScrollArea(QtGui.QScrollArea):
    def __init__(self, parent):
        QtGui.QScrollArea.__init__(self)
        self.parent = parent
        self.closed = False
    def minimumSizeHint(self):
        return QtCore.QSize(440, 300)

    def sizeHint(self):
        return QtCore.QSize(440, 300)
    def closeEvent(self, ev):
        if not self.closed:
            self.closed = True
            OpenedWindowSingleton.Del(self)
            OpenedWindowSingleton.Del(self.parent.gui)
            OpenedWindowSingleton.Del(self.parent.guimdi)
            self.parent.gui = None
            self.parent.guimdi.close()
            self.parent.guimdi = None

class VSTGUIWindow(QtGui.QWidget):
    def __init__(self, vstWindow):
        QtGui.QWidget.__init__(self)
        self.vstWindow = vstWindow
        self.closed = False
    def closeEvent(self, ev):
        if not self.closed:
            self.closed = True
            OpenedWindowSingleton.Del(self)
            OpenedWindowSingleton.Del(self.vstWindow.gui)
            OpenedWindowSingleton.Del(self.vstWindow.guimdi)
            self.vstWindow.gui = None
            self.vstWindow.guimdi.close()
            self.vstWindow.guimdi = None
            self.vstWindow.vstEff.close_edit()
class VSTWindow:
    idx = 0
    def __init__(self, fileName, parent, mustbeSynth):
        self.fileName = fileName.replace("\\","/")
        self.parent = parent
        vstEff = pyvst.VSTPlugin(fileName,self.Callback)
        if not ((vstEff.IsSynth() and mustbeSynth) or (not vstEff.IsSynth() and not mustbeSynth)):
            QtGui.QMessageBox.information(self.parent,
                                    'Error',
                                    'Trying to add an effect to an instrument panel or vice versa')
            return

        self.vstEff = vstEff
        vstEff.open()
        self.sampleRate = 44100.0
        self.blockSize = 512
        self.fxNum = -1
        self.pNum = 0
        self.vstSettings = None
        #self.window = wx.Frame(None, pos=(0, 0), size=wx.DefaultSize)
        #self.window.Show(True)
        vstEff.set_sample_rate(self.sampleRate)
        #vstEff.set_block_size(11025)
        #vstEff.resume()
        #vstEff.suspend()
        vstEff.set_block_size(self.blockSize)
        vstEff.resume()
        #self.NoteEvent(0x64, 0xFF)

        print "Programs", vstEff.get_number_of_programs()
        print "Params", vstEff.get_number_of_parameters()
        print "Inputs", vstEff.get_number_of_inputs()
        print "Outputs", vstEff.get_number_of_outputs()
        print "Version", vstEff.get_vst_version()
        print "Plugin name:", vstEff.get_name()
        print "Vendor name:", vstEff.get_vendor()
        print "Product name:", vstEff.get_product()

        self.wantMidi = vstEff.CanDo("receiveVstMidiEvent") == True # False: Effect, True: VSTi
        self.isVSTi = vstEff.IsSynth()
        #print vstEff.CanDo("receiveVstEvents")
       # print vstEff.CanDo("midiProgramNames")
        if self.isVSTi:
            print "VSTInstrument"
        else:
            print "VSTEffect"

        #print GetTempos(69, 4)
       # print GetTempos(69+4, 3)
      #  print GetTempos(69+4, 4)
        
        self.windowInited = False
        self.OpenGUI()



        # 타이머를 타이머로 하지 말고 뭐랄까... 메인루프를 가져온다.
        self.notClosed = True
        self.vstLoaded = False
        self.vstLoadInited = False
        #self.parent.Bind (wx.EVT_IDLE, self.OnTime)
        
    def OpenGUI(self):
        OpenedWindowSingleton.CloseAll()
        self.vstSettings = VSTSettingsWindow(self, self.vstEff)
        OpenedWindowSingleton.AddWnd(self.vstSettings)

        self.eRect = eRect = self.vstEff.get_erect()
        VSTWindow.idx += 1
        if eRect:
            self.gui = guiWindow = VSTGUIWindow(self)
            self.guimdi = sub = ParentFrameSingleton.AddSubWindow(guiWindow)
            self.gui.show()
            
            OpenedWindowSingleton.AddWnd(self.gui)
            OpenedWindowSingleton.AddWnd(self.guimdi)
            guiWindow.setWindowTitle(self.vstEff.get_name())

            self.vstEff.open_edit(int(guiWindow.winId()))

            self.eRect = eRect = self.vstEff.get_erect()
            width = eRect.right - eRect.left;
            height = eRect.bottom - eRect.top;
            if (width < 100):
                width = 100
            if (height < 100):
                height = 100

            width += 10
            height += 35
            sub.resize(width, height)

        else:
            self.gui = myscr = VSTScrollArea(self)
            guiWindow = VSTGUILessWindow(ParentFrameSingleton, self.vstEff)
            self.guimdi = ParentFrameSingleton.AddSubWindow(myscr)
            OpenedWindowSingleton.AddWnd(self.gui)
            OpenedWindowSingleton.AddWnd(self.guimdi)
            myscr.setWindowTitle(self.vstEff.get_name())
            myscr.setWidget(guiWindow)
            myscr.show()
        self.gui.lower() # 내렸다 올려줘야 pyqt부분은 raise_되어있고 vsthwnd부분은 lower되어있는게 해결된다.
        self.guimdi.lower()
        self.gui.raise_()
        self.guimdi.raise_()


    def NoteEvent(self, key, volume):
        kVstMidiType = 1
        kVstMidiEventIsRealTime = 1
        vstMidiEvents = pyvst.VstMidiEvents(numEvents=4, reserved=0)
        vstMidiEvents.numEvents = 4
        vstMidiEvents.reserved = 0
        midiEvent1 = pyvst.VstMidiEvent()
        midiEvent1.type = kVstMidiType
        midiEvent1.byteSize = 24#sizeof(pyvst.VstMidiEvent)
        midiEvent1.deltaFrames = 0 # note start position!
        midiEvent1.flags = kVstMidiEventIsRealTime
        midiEvent1.noteLength = 0#self.sampleRate/1000*30
        midiEvent1.noteOffset = 0 # ??? end position?
        midiEvent1.midiData1 = (0x90) # play note midi msg
        midiEvent1.midiData2 = (key) # note key
        midiEvent1.midiData3 = (0xFF) # volume
        midiEvent1.midiData4 = (0x00)
        midiEvent1.detune = 0
        midiEvent1.noteOffVelocity = 0
        midiEvent1.reserved1 = 0
        midiEvent1.reserved2 = 0
        vstMidiEvents.events[0] = POINTER(pyvst.VstMidiEvent)(midiEvent1)
        midiEvent2 = pyvst.VstMidiEvent()
        midiEvent2.type = kVstMidiType
        midiEvent2.byteSize = 24#sizeof(pyvst.VstMidiEvent)
        midiEvent2.deltaFrames = 128 # note start position!
        midiEvent2.flags = kVstMidiEventIsRealTime
        midiEvent2.noteLength = 0#self.sampleRate/1000*30
        midiEvent2.noteOffset = 0 # ??? end position?
        midiEvent2.midiData1 = (0x90) # play note midi msg
        midiEvent2.midiData2 = (key) # note key
        midiEvent2.midiData3 = (0x00) # volume
        midiEvent2.midiData4 = (0x00)
        midiEvent2.detune = 0
        midiEvent2.noteOffVelocity = 0
        midiEvent2.reserved1 = 0
        midiEvent2.reserved2 = 0
        vstMidiEvents.events[1] = POINTER(pyvst.VstMidiEvent)(midiEvent2)
        midiEvent3 = pyvst.VstMidiEvent()
        midiEvent3.type = kVstMidiType
        midiEvent3.byteSize = 24#sizeof(pyvst.VstMidiEvent)
        midiEvent3.deltaFrames = 256 # note start position!
        midiEvent3.flags = kVstMidiEventIsRealTime
        midiEvent3.noteLength = 0#self.sampleRate/1000*30
        midiEvent3.noteOffset = 0 # ??? end position?
        midiEvent3.midiData1 = (0x90) # play note midi msg
        midiEvent3.midiData2 = (key) # note key
        midiEvent3.midiData3 = (0xFF) # volume
        midiEvent3.midiData4 = (0x00)
        midiEvent3.detune = 0
        midiEvent3.noteOffVelocity = 0
        midiEvent3.reserved1 = 0
        midiEvent3.reserved2 = 0
        vstMidiEvents.events[2] = POINTER(pyvst.VstMidiEvent)(midiEvent3)
        midiEvent4 = pyvst.VstMidiEvent()
        midiEvent4.type = kVstMidiType
        midiEvent4.byteSize = 24#sizeof(pyvst.VstMidiEvent)
        midiEvent4.deltaFrames = 384 # note start position!
        midiEvent4.flags = kVstMidiEventIsRealTime
        midiEvent4.noteLength = 0#self.sampleRate/1000*30
        midiEvent4.noteOffset = 0 # ??? end position?
        midiEvent4.midiData1 = (0x90) # play note midi msg
        midiEvent4.midiData2 = (key) # note key
        midiEvent4.midiData3 = (0x00) # volume
        midiEvent4.midiData4 = (0x00)
        midiEvent4.detune = 0
        midiEvent4.noteOffVelocity = 0
        midiEvent4.reserved1 = 0
        midiEvent4.reserved2 = 0
        vstMidiEvents.events[3] = POINTER(pyvst.VstMidiEvent)(midiEvent4)
        self.vstEff.ProcessMidi(vstMidiEvents)
        output = numpy.zeros((self.vstEff.number_of_outputs, 512), dtype=numpy.float32)
        self.vstEff.process_replacing_output(output[:, 0:512], 512)
        """
        for o in output[1]:
            if o != 0.0:
                print o
        """
        """
        f = open("text.wav", "wb")
        f.write(output[1][0:512])
        f.write(output[0][0:512])
        f.close()
        """

    def OnTime(self, evt):
        """
        idle은 말 그대로 idle일때만 작동... 매번 되는 건 없나...
        if self.parent and self.notClosed:
            try:
                #self.vstEff.idle()
                self.vstLoaded = True
                if not self.vstLoadInited:
                    self.vstLoadInited = True
                    self.OnVSTLoad()
            except:
                self.vstLoaded = False
        """
    def OnVSTLoad(self):
        pass
    def OnWM_CLOSE(self, hwnd, msg, wp, lp):
        self.CloseWindow(hwnd)
    def Close(self, hwnd):
        self.CloseWindow(hwnd)
        VSTSoundWorker.quit = True
    def CloseWindow(self, hwnd):
        if self.notClosed:
            self.notClosed = False
            self.vstEff.close_edit()
            win32gui.DestroyWindow(hwnd)
    def Callback(self, effect, opcode, index, value, ptr, opt):
        #print opcode, index, value, c_char_p(ptr).value, opt, pyvst.AudioMasterOpcodes.audioMasterWantMidi
        """
        1,42,6,6
        Basic callback
        """
        #print opcode
        kVstVersion = 2400
        if opcode == pyvst.AudioMasterOpcodes.audioMasterCanDo:
            canDos = ["sendVstEvents",
                "sendVstMidiEvent",
                "receiveVstEvents",
                "receiveVstMidiEvent",
                "sizeWindow",
                "sendVstMidiEventFlagIsRealtime",
                "openFileSelector",
                "closeFileSelector",
                "shellCategory",
                "supplyIdle"]
            
            if c_char_p(ptr).value in canDos:
                return 1
        if opcode == pyvst.AudioMasterOpcodes.audioMasterVersion:
            return kVstVersion

        if opcode == pyvst.AudioMasterOpcodes.audioMasterWantMidi:
            return 1

        return 0


class SettingsFile:
    def __init__(self, fileName):
        self.fileName = fileName
        try:
            self.settings = pickle.load(open(fileName, "rb"))
        except:
            self.settings = {}

    def SetData(self, name, value):
        self.settings[name] = value
        pickle.dump(self.settings, open(self.fileName, "wb"))
    def GetData(self, name):
        try:
            return self.settings[name]
        except:
            return None
"""
VST Option페이지에 플러그인 디렉토리
스캔 플러그인
플러그인 리스트도 보여주고
Set Instruments
Set Effects버튼을 넣어서 멀티쵸이스로 보여준다.
"""
class VSTPanel(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self, parent)
        extensionLayout = QtGui.QVBoxLayout()
        pathL = QtGui.QLabel("VST Plugins Path:")
        path = SettingsSingleton.GetData("VSTPath")
        self.path = QtGui.QLabel(path)

        setpath = QtGui.QPushButton("Select Path")
        self.connect(setpath, QtCore.SIGNAL("clicked()"),
                     self.OnVSTPath)

        scanb = QtGui.QPushButton("Scan VST Plugins")
        self.connect(scanb, QtCore.SIGNAL("clicked()"),
                     self.OnDumpVST)
        setvsti = QtGui.QPushButton("Set VST Instruments")
        self.connect(setvsti, QtCore.SIGNAL("clicked()"),
                     self.OnSetVSTI)
        setvste = QtGui.QPushButton("Set VST Effects")
        self.connect(setvste, QtCore.SIGNAL("clicked()"),
                     self.OnSetVSTE)
        extensionLayout.addWidget(pathL)
        extensionLayout.addWidget(self.path)
        extensionLayout.addWidget(setpath)
        extensionLayout.addWidget(scanb)
        extensionLayout.addWidget(setvsti)
        extensionLayout.addWidget(setvste)
        label = QtGui.QLabel("")
        extensionLayout.addWidget(label)
        extensionLayout.setStretch(6, 1)
        self.setLayout(extensionLayout)

    def OnVSTPath(self):
        path = SettingsSingleton.GetData("VSTPath") 
        if not path:
            path = QtCore.QDir.currentPath()
        directory = QtGui.QFileDialog.getExistingDirectory(self, "Set VST Plugins Folder",
                path)

        if directory:
            directory = str(directory)
            SettingsSingleton.SetData("VSTPath", directory)
            self.path.setText(directory)

    def OnSetVSTI(self):
        dllList = SettingsSingleton.GetData("VSTDllDump")
        dllList = [dll[1] for dll in dllList]
        dllList.sort()
        print dllList
        selectedList = SettingsSingleton.GetData("VSTInstruments")
        selectedIdx = []
        for selected in selectedList:
            if selected in dllList:
                selectedIdx += [dllList.index(selected)]

        mgr = MultiChoiceDialogManager("VST Instruments", "Select VST Instruments", dllList, selectedIdx)
        result = mgr.DoModal()

        if result:
            selections = result
            strings = [dllList[x] for x in selections]
            SettingsSingleton.SetData("VSTInstruments", strings)

    def OnSetVSTE(self):
        dllList = SettingsSingleton.GetData("VSTDllDump")
        dllList = [dll[1] for dll in dllList]
        dllList.sort()
        selectedList = SettingsSingleton.GetData("VSTEffects")
        selectedIdx = []
        for selected in selectedList:
            if selected in dllList:
                selectedIdx += [dllList.index(selected)]


        mgr = MultiChoiceDialogManager("VST Effects", "Select VST Instruments", dllList, selectedIdx)
        result = mgr.DoModal()

        if result:
            selections = result
            strings = [dllList[x] for x in selections]
            SettingsSingleton.SetData("VSTEffects", strings)

    def OnDumpVST(self):
        import os
        vstPath = SettingsSingleton.GetData("VSTPath")

        def RecurseDirs(path):
            paths = []
            dirs = os.listdir(path)
            for dir in dirs:
                if os.path.isdir(path + "/" + dir):
                    paths += [path+"/"+dir]
                    paths += RecurseDirs(path+"/"+dir)
            return paths
        dirs = [vstPath] + RecurseDirs(vstPath)
        dllfiles = []
        for dir in dirs:
            files = os.listdir(dir)
            for fileName in files:
                if fileName[-3:].lower() == "dll":
                    dllfiles += [(dir+"/"+fileName, fileName)]
        vsti = []
        vstEffect = []
        dlldump = []
        oldDlls = SettingsSingleton.GetData("VSTDllDump")
        oldFileNames = [dll[1] for dll in oldDlls]
        for dll in dllfiles:
            if dll[1] in oldFileNames:
                dlldump += [dll]
            else:
                __lib = CDLL(dll[0])
                print "Scanning...", dll[1]
                try:
                    __lib.VSTPluginMain
                    print "VSTPlugin", dll[1]
                    dlldump += [dll]
                except AttributeError:
                    try:
                        __lib.main
                        print "Might be a VSTPlugin!", dll[1]
                        dlldump += [dll]
                    except:
                        print "Not a VST Plugin!", dll[1]

            #data = DumpVSTData(dll)

        SettingsSingleton.SetData("VSTDllDump", dlldump)
        print "Scaning All Done"
        QtGui.QMessageBox.information(self,
                                'Scanning Complete',
                                'Scanning complete. Please select VST Instruments and VST Effects.')

        """
        dlg = wx.MessageDialog(self, 
                               
                                ,
                               wx.OK | wx.ICON_INFORMATION
                               #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        dlg.ShowModal()
        dlg.Destroy()
        """



class Options(QtGui.QDialog):
    def __init__(self):
        super(Options, self).__init__(None, Qt.WindowTitleHint | Qt.WindowSystemMenuHint)
        self.setWindowTitle("Options")

        self.nb = QtGui.QTabWidget(self)
        self.nb.addTab(VSTPanel(self.nb), "VST")
        btn1 = QtGui.QPushButton("Save")
        self.connect(btn1, QtCore.SIGNAL("clicked()"),
                     self.OnOK)
        btn2 = QtGui.QPushButton("Don't Save")
        self.connect(btn2, QtCore.SIGNAL("clicked()"),
                     self.OnCancel)

        extensionLayout = QtGui.QVBoxLayout()
        buttonsL = QtGui.QHBoxLayout()
        buttonsL.addWidget(btn1)
        buttonsL.addWidget(btn2)
        extensionLayout.setMargin(0)
        extensionLayout.setSpacing(5)
        extensionLayout.addWidget(self.nb)
        extensionLayout.setStretch(0, 1)
        extensionLayout.addLayout(buttonsL)


        self.setLayout(extensionLayout)
    def OnOK(self):
        self.accept()
    def OnCancel(self):
        self.reject()

class MyParentFrame:
    def __init__(self, app):
        global TopWindowSingleton, TempoSingleton, ParentFrameSingleton
        ParentFrameSingleton = self
        self.app = app
        wx.MDIParentFrame.__init__(self, None, -1, "Py Music Sequencer", size=(1000,600))
        ID_New  = wx.NewId()
        ID_Open  = wx.NewId()
        ID_SelectVST  = wx.NewId()
        ID_Options  = wx.NewId()
        ID_DumpVST  = wx.NewId()
        ID_Exit = wx.NewId()
        self.winCount = 0
        self.settings = SettingsFile("./MusicTheory/settings.pkl")
        self.projectFile = SettingsFile("./MusicTheory/myProj.pys")
        global SettingsSingleton, CurProjectSingleton
        SettingsSingleton = self.settings
        CurProjectSingleton = self.projectFile
        
        menubar = wx.MenuBar()
        menu = wx.Menu()
        menu.Append(ID_Open, "OpenTest")
        menu.AppendSeparator()
        menu.Append(ID_Exit, "E&xit")
        menubar.Append(menu, "&File")

        menu = wx.Menu()
        menu.Append(ID_New, "&Piano Roll")
        menu.AppendSeparator()
        menu.Append(ID_Options, "&Options")
        menubar.Append(menu, "&Edit")

        self.SetMenuBar(menubar)

        self.CreateStatusBar()
        TopWindowSingleton = self

        #self.Bind(wx.EVT_MENU, self.OnNewWindow, id=ID_New)
        #self.Bind(wx.EVT_MENU, self.OnSelectVST, id=ID_SelectVST)
        #self.Bind(wx.EVT_MENU, self.OnDumpVST, id=ID_DumpVST)
        self.Bind(wx.EVT_MENU, self.OnOpen, id=ID_Open)
        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_Exit)
        self.Bind(wx.EVT_MENU, self.OnOptions, id=ID_Options)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        #self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.regHotKey()

        self.patternManagerShown = False
        self.OnNewWindow(None)
        self.OnPatternManager(None)
        self.mixer = Mixer()
        
        """
        if SHOW_BACKGROUND:
            self.bg_bmp = images.getGridBGBitmap()
            self.GetClientWindow().Bind(
                wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground
                )
        """
        TBFLAGS = ( wx.TB_HORIZONTAL
                    | wx.NO_BORDER
                    | wx.TB_FLAT
                    #| wx.TB_TEXT
                    #| wx.TB_HORZ_LAYOUT
                    )


        tb = self.CreateToolBar( TBFLAGS )
        # 툴바가 뭐 이렇냐...
        # 줄만 좀 어떻게 되면 되는데 다음줄에 아템추가가 안되니 뭐..
        # 걍 패널 하나 띄우고 그걸 툴바로 쓴다. 이 툴바에는 아주 필요한 것 몇개만 넣는다.
        # 일단 플레이버튼 정지버튼, 템포, 패턴, 패턴매니져, 믹서, 플레이리스트
        # 나머지는 뭐 패널에 넣음
        #
        # 템포, 패턴은 그려서 만든다.
        # 패턴매니져 믹서 플레이리스트 아이콘은...
        tsize = (15,15)
        tb.SetToolBitmapSize(tsize)
        
        #tb.AddSimpleTool(10, new_bmp, "New", "Long help for 'New'")
        id = wx.NewId()
        tb.AddLabelTool(id, "Save Project", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE), shortHelp="Save Project", longHelp="Save Project")
        self.Bind(wx.EVT_TOOL, self.OnSaveProject, id=id)

        tb.AddSeparator()
        tb.AddControl(Display(tb))
        tb.AddLabelTool(wx.NewId(), "Play From Start", LoadBitmap("play2.png"), shortHelp="Play From Start", longHelp="Play From Start")
        tb.AddLabelTool(wx.NewId(), "Play", LoadBitmap("play.png"), shortHelp="Play", longHelp="Play")
        tb.AddLabelTool(wx.NewId(), "Pause", LoadBitmap("pause.png"), shortHelp="Pause", longHelp="Pause")
        tb.AddLabelTool(wx.NewId(), "Stop", LoadBitmap("stop.png"), shortHelp="Stop", longHelp="Stop")
        tb.AddSeparator()
        tb.AddLabelTool(wx.NewId(), "Pattern Manager", LoadBitmap("pm.png"), shortHelp="Pattern Manager", longHelp="Open Pattern Manager")
        tb.AddLabelTool(wx.NewId(), "Play List", LoadBitmap("pl.png"), shortHelp="Play List", longHelp="Open Play List")
        tb.AddLabelTool(wx.NewId(), "Mixer", LoadBitmap("mix.png"), shortHelp="Mixer", longHelp="Open Mixer/FX Manager")
        tb.AddSeparator()
        TempoSingleton = Tempo(tb)
        tb.AddControl(TempoSingleton)
        tb.AddControl(Pattern(tb))

        #for i in range(100):
        """
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=10)
        self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=10)

        #tb.AddSimpleTool(20, open_bmp, "Open", "Long help for 'Open'")
        """
        #tb.AddLabelTool(20, "Open", open_bmp, shortHelp="Open", longHelp="Long help for 'Open'")
        """
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=20)
        self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=20)

        """
        #tb.AddSimpleTool(30, copy_bmp, "Copy", "Long help for 'Copy'")
        """
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=30)
        self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=30)
        """

        #tb.AddSimpleTool(40, paste_bmp, "Paste", "Long help for 'Paste'")
        """
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=40)
        self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=40)
        """


        """
        #tool = tb.AddCheckTool(50, images.getTog1Bitmap(), shortHelp="Toggle this")
        tool = tb.AddCheckLabelTool(50, "Checkable", images.getTog1Bitmap(),
                                    shortHelp="Toggle this")
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=50)

        self.Bind(wx.EVT_TOOL_ENTER, self.OnToolEnter)
        self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick) # Match all
        self.Bind(wx.EVT_TIMER, self.OnClearSB)

        tb.AddSeparator()
        cbID = wx.NewId()

        tb.AddControl(
            wx.ComboBox(
                tb, cbID, "", choices=["", "This", "is a", "wx.ComboBox"],
                size=(150,-1), style=wx.CB_DROPDOWN
                ))
        self.Bind(wx.EVT_COMBOBOX, self.OnCombo, id=cbID)

        tb.AddSeparator()
        search = TestSearchCtrl(tb, size=(150,-1), doSearch=self.DoSearch)
        tb.AddControl(search)

        # Final thing to do for a toolbar is call the Realize() method. This
        # causes it to render (more or less, that is).
        """
        tb.Realize()

    def OnOpen(self, evt):
        self.patternManager.Load()
    def OnSaveProject(self, evt):
        insts = []
        for panel in self.patternManager.insPanels:
            inst = {}
            inst["fileName"] = panel.vst.fileName
            inst["pianoRoll"] = panel.notes
            insts += [inst]
                
        insts = CurProjectSingleton.SetData("instruments", insts)

    def regHotKey(self):
        """
        This function registers the hotkey Alt+F1 with id=100
        """
        playID = wx.NewId()
        self.Bind(wx.EVT_MENU, self.handleHotKey, id=playID)
        aTable = wx.AcceleratorTable([
                                    (wx.ACCEL_NORMAL, wx.WXK_SPACE, playID)
                                    ])
        self.SetAcceleratorTable(aTable)

    def handleHotKey(self, evt):
        self.patternManager.OnPlay()

    def OnExit(self, evt):
        self.Close(True)

    def OnOptions(self, evt):
        dlg = Options(self, -1, "Options", size=(450, 500),
                         style=wx.DEFAULT_DIALOG_STYLE,
                         )
        dlg.CenterOnScreen()

        val = dlg.ShowModal()
    
        if val == wx.ID_OK:
            print "Save"
        else:
            print "Cancel"

        dlg.Destroy()


    def OnSelectVST(self, evt):
        dialog = wx.DirDialog(None, "Choose VSTPlugins directory:",style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            self.settings.SetData("VSTPath", dialog.GetPath())
        dialog.Destroy()


    def OnNewWindow(self, evt):
        win = wx.MDIChildFrame(self, -1, "Piano Roll")
        self.pianoRoll = PianoRollWindow(win)
        win.Show(True)

    def NewVSTGUIChild(self, title, size=(500, 400)):
        win = wx.MDIChildFrame(self, -1, title, size=size)
        win.Show(True)
        return win

    def OnPatternManager(self, evt):
        if self.patternManagerShown:
            pass
        else:
            self.patternManagerShown = True
            win = wx.MDIChildFrame(self, -1, "Instruments/Pattern Manager", size=(PatternManagerWidth, 400))
            self.patternManager = PatternManager(win)
            win.Show(True)



    def OnClose(self, evt):
        """
        dlg = wx.MessageDialog(self, 
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()
        """
        try:
            self.pianoRoll.vst.Close(self.pianoRoll.vst.hwnd)
            self.pianoRoll.Close()
        except:
            pass
        self.Destroy()
        self.app.Exit()
        VSTSoundWorker.quit = True
        import sys
        def Go(m):
            VSTThreadSingleton.mutexObj.unlock()
            sys.exit()
        VSTThreadSingleton.mutexObj.lock(Go, None)
        sys.exit()

    def OnEraseBackground(self, evt):
        painter = evt.GetDC()

        if not painter:
            painter = wx.ClientDC(self.GetClientWindow())

        # tile the background bitmap
        sz = self.GetClientSize()
        w = self.bg_bmp.GetWidth()
        h = self.bg_bmp.GetHeight()
        x = 0
        
        while x < sz.width:
            y = 0

            while y < sz.height:
                painter.DrawBitmap(self.bg_bmp, x, y)
                y = y + h

            x = x + w

def LoadBitmap(fileName):
    imgPath = imagesPath + '/' + fileName
    pix = QtGui.QPixmap(imgPath)
    return pix



PatternManagerWidth = 500
class BeatEditor(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self,parent,size=QtCore.QSize(280,30))
        self.parent = parent
        """
        "Set Key" 버튼이 있어서 그 키에 맞게 비트의 음을 설정하도록 한다.
        으 비트 하나하나의 음을 설정하는게 FL Studio엔 있다. 그것도 구현한다?
        그런 패널을 통째로 띄우는 게 이쓴ㄴ지 모르겠다.
        apply(pop.PopupControl.__init__,(self,) + _args,_kwargs)

        self.win = wx.Window(self,-1,pos = (0,0),style = 0)
        self.cal = cal.CalendarCtrl(self.win,-1,pos = (0,0))

        bz = self.cal.GetBestSize()
        self.win.SetSize(bz)

        # This method is needed to set the contents that will be displayed
        # in the popup
        self.SetPopupContent(self.win)
있다.
        """
        self.beats = [False for i in range(16)]
        self.SetBeat(0, True)
        self.SetBeat(4, True)
        self.SetBeat(8, True)
        self.enteredBeat = -1
        self.ldragging = False
        self.setMouseTracking(True)


    def mousePressEvent(self, ev):
        pos = ev.pos().x(), ev.pos().y()
        beatpos = self.GenBeatPositions()

        if ev.button() == LMB:
            self.ldragging = True
            idx = 0
            for bpos in beatpos:
                if InRect(*(bpos+(pos[0],pos[1]))):
                    if self.enteredBeat != idx:
                        self.enteredBeat = idx
                    if self.IsBeatOn(idx):
                        self.SetBeat(idx, False)
                    else:
                        self.SetBeat(idx, True)
                idx += 1
    def mouseMoveEvent(self, ev):
        pos = ev.pos().x(), ev.pos().y()
        beatpos = self.GenBeatPositions()
        cnum = QtGui.QCursor(QtCore.Qt.ArrowCursor)
        for bpos in beatpos:
            if InRect(*(bpos+(pos[0],pos[1]))):
                cnum = QtGui.QCursor(QtCore.Qt.PointingHandCursor)
        self.setCursor(cnum)

        if self.ldragging:
            idx = 0

            for bpos in beatpos:
                if InRect(*(bpos+(pos[0],pos[1]))):
                    if self.enteredBeat != idx:
                        self.enteredBeat = idx
                        if self.IsBeatOn(idx):
                            self.SetBeat(idx, False)
                        else:
                            self.SetBeat(idx, True)
                idx += 1
    def mouseReleaseEvent(self, ev):
        self.ldragging = False

    def OnPianoRoll(self):
        fxs = MixerPanelsSingleton.GetFXs(self.parent.vst.fxNum)
        VSTThreadSingleton.SwitchInstrument(self.parent.vst.vstEff, fxs)
        PianoRollSingleton.SetInstrumentPattern(self.parent, 0)
    def OnContextMenu(self, event):
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
            self.popupID3 = wx.NewId()
            self.popupID4 = wx.NewId()
            self.popupID5 = wx.NewId()
            self.popupID6 = wx.NewId()
            self.popupID7 = wx.NewId()
            self.popupID8 = wx.NewId()
            self.popupID9 = wx.NewId()

            self.Bind(wx.EVT_MENU, self.OnPianoRoll, id=self.popupID1)
            """

            self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
            self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
            self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
            self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)
            self.Bind(wx.EVT_MENU, self.OnPopupSix, id=self.popupID6)
            self.Bind(wx.EVT_MENU, self.OnPopupSeven, id=self.popupID7)
            self.Bind(wx.EVT_MENU, self.OnPopupEight, id=self.popupID8)
            self.Bind(wx.EVT_MENU, self.OnPopupNine, id=self.popupID9)
            """

        # make a menu
        menu = wx.Menu()
        # Show how to put an icon in the menu
        item = wx.MenuItem(menu, self.popupID1,"PianoRoll")
        menu.AppendItem(item)
        # add some other items
        """
        menu.Append(self.popupID2, "Two")
        menu.Append(self.popupID3, "Three")
        menu.Append(self.popupID4, "Four")
        menu.Append(self.popupID5, "Five")
        menu.Append(self.popupID6, "Six")
        # make a submenu
        sm = wx.Menu()
        sm.Append(self.popupID8, "sub item 1")
        sm.Append(self.popupID9, "sub item 1")
        menu.AppendMenu(self.popupID7, "Test Submenu", sm)
        """


        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu)
        menu.Destroy()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self.Draw(painter)

    def GenBeatPositions(self):
        pos = []
        totalOffset = 0
        for i in range(16):
            offset = i%4 == 0
            offset *= 4
            totalOffset += offset
            l = 2+i*16+totalOffset
            w = 15
            t = 5
            h = 19
            pos += [(l,t,w,h)]
        return pos

    def IsBeatOn(self, idx):
        return self.beats[idx]
    def SetBeat(self, idx, onOff):
        self.beats[idx] = onOff
        self.repaint()
    def minimumSizeHint(self):
        return QtCore.QSize(280, 30)

    def sizeHint(self):
        return QtCore.QSize(280, 30)

    def Draw(self, painter):
        color = self.parent.palette().background().color()
        color = color.red(), color.blue(), color.green()
        w, h = self.size().width(), self.size().height()
        w -= 1
        h -= 1
        col = QtGui.QColor(255, 255, 255)
        painter.setPen(QtGui.QPen(col))
        painter.setBrush(QtGui.QBrush(col))
        painter.drawLine(0, 0, w, 0)
        col = QtGui.QColor(color[0]-30, color[1]-30, color[2]-30)#"#a5b84c"
        painter.setPen(QtGui.QPen(col))
        painter.setBrush(QtGui.QBrush(col))
        painter.drawLine(0, h, w, h)
        col = QtGui.QColor(255, 255, 255)
        painter.setPen(QtGui.QPen(col))
        painter.setBrush(QtGui.QBrush(col))
        painter.drawLine(0, 0, 0, h)
        col = QtGui.QColor(color[0]-30, color[1]-30, color[2]-30)#"#a5b84c"
        painter.setPen(QtGui.QPen(col))
        painter.setBrush(QtGui.QBrush(col))
        painter.drawLine(w, 0, w, h)



        on = LoadBitmap('beat.png')
        off = LoadBitmap('beatoff.png')
        #painter.DrawBitmap(bmp, 2,5, True)
        totalOffset = 0
        for i in range(16):
            if self.IsBeatOn(i):
                bmp = on
            else:
                bmp = off
            offset = i%4 == 0
            offset *= 4
            totalOffset += offset
            painter.drawPixmap(2+i*16+totalOffset,5,bmp)


class Pattern(QtGui.QFrame):#wx.Panel, 
    def __init__(self, parent):
        QtGui.QFrame.__init__(self,parent,size=QtCore.QSize(31,15))
        #wx.Panel.__init__(self, parent, size=(49,23))
        self.binds = []
        self.value = 0
        self.SetMinMax(0, 9999)
        self.SetValue(0)
        self.ldragging = False
        self.startValue = self.value
        # 음.... 1픽셀당 1퍼센트 움직이게 하자.
        self.accuracy = 0.2/9999.0
        self.fractionLen = 3
        self.SetToolTipString("Pattern Number")

        self.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        self.setLineWidth(1)
    def minimumSizeHint(self):
        return QtCore.QSize(31, 15)

    def sizeHint(self):
        return QtCore.QSize(31, 15)
    def SetToolTipString(self, ttstr):
        self.ttstr = ttstr
    def event(self, event):
        if event.type() == QtCore.QEvent.ToolTip:
            QtGui.QToolTip.hideText()
            QtGui.QToolTip.showText(event.globalPos(), self.ttstr)
            return True
        else:
            QtGui.QToolTip.hideText()

        return super(self.__class__, self).event(event)

    def OnSetValue(self, evt):
        dlg = wx.TextEntryDialog(
                self, 'Set Pattern Number(0~9999)',
                'Select Pattern', 'Select Pattern')

        dlg.SetValue(`self.GetPatternNumber()`)

        if dlg.ShowModal() == wx.ID_OK:
            try:
                num = int(dlg.GetValue())
                if num > 9999:
                    num = 9999
                if num < 0:
                    num = 0
                self.SetValue(num)
            except:
                pass

        dlg.Destroy()

    def OnContextMenu(self, evt):
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.Bind(wx.EVT_MENU, self.OnSetValue, id=self.popupID1)
        menu = wx.Menu()
        item = wx.MenuItem(menu, self.popupID1,"Set Value")
        menu.AppendItem(item)
        self.PopupMenu(menu)
        menu.Destroy()

    def GetPatternNumber(self):
        return self.value

    def BindOnPatternChange(self, func):
        self.binds += [func]
    def _OnPatternChange(self, pat):
        for bind in self.binds:
            bind(pat)

    def OnButtonEvent(self, event):
        pos = event.GetPosition().Get()
        if event.LeftDown():
            self.SetFocus()
            self.CaptureMouse()
            self.startPos = event.GetPosition().Get()[1]
            self.startPosX = event.GetPosition().Get()[0]
            if InRect(0,0,self.size[0],self.size[1], pos[0], pos[1]):
                self.startValue = self.value
                self.ldragging = True

        elif event.Dragging():
            if self.ldragging:
                curPos = event.GetPosition().Get()[1]
                offset = (curPos-self.startPos)
                offset = float(offset)*((self.GetMaxValue()-self.GetMinValue())*self.accuracy)
                self.SetValue(int(self.startValue-offset))
                if self.value > self.GetMaxValue():
                    self.SetValue(self.GetMaxValue())
                if self.value < self.GetMinValue():
                    self.SetValue(self.GetMinValue())

        elif event.LeftUp():
            self.ldragging = False
            try:
                self.ReleaseMouse()
            except:
                pass

    def GetValue(self):
        return self.value
    def SetValue(self, val):
        self.value = val
        self._OnPatternChange(self.GetPatternNumber())
        self.repaint()
    def SetMinMax(self, min, max):
        self.minmax = (min, max)
    def GetMinValue(self):
        return self.minmax[0]
    def GetMaxValue(self):
        return self.minmax[1]
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self.Draw(painter)
        QtGui.QFrame.paintEvent(self, event)

    def Draw(self, painter):
        bmp = LoadBitmap('patternbg.png')
        painter.drawPixmap(0,0, bmp)
        valueStr = `self.value`
        while len(valueStr) < 4:
            valueStr = "0" + valueStr


        imgs = [(`i`, LoadBitmap(`i`+".png")) for i in range(10)]
        imgsD = {}
        for img in imgs:
            imgsD[img[0]] = img[1]
        i = 0
        nonZeroFound = False
        for num in valueStr:
            if num == "0" and not nonZeroFound and i < 3:
                i += 1
                continue
            else:
                nonZeroFound = True
            painter.drawPixmap(2+i*7,2, imgsD[num])
            i += 1




class Display(QtGui.QFrame):#wx.Panel, 
    def __init__(self, parent):
        QtGui.QFrame.__init__(self,parent,size=QtCore.QSize(72,15))
        #wx.Panel.__init__(self, parent, size=(49,23))
        self.binds = []
        self.value = 0
        self.value2 = 0
        self.value3 = 0
        self.SetMinMax(0, 9999)
        self.SetValue(9999)
        self.SetMinMax2(0, 99)
        self.SetValue2(45)
        self.SetMinMax3(0, 999)
        self.SetValue3(41)
        self.SetToolTipString("Step - Step / Beat / Minute Display")
        self.states = ["Step", "Beat", "Minute"]
        self.msgs = ["Step (Click to change to Beat View, Right click to show menu)",
                "Beat (Click to change to Minute View, Right click to show menu)",
                "Minute (Click to change to Step View, Right click to show menu)"]
        self.state = self.states.index("Step")
        self.SetToolTipString(self.msgs[self.state])
        self.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        self.setLineWidth(1)

    def minimumSizeHint(self):
        return QtCore.QSize(72, 15)

    def sizeHint(self):
        return QtCore.QSize(72, 15)
    def SetToolTipString(self, ttstr):
        self.ttstr = ttstr
    def event(self, event):
        if event.type() == QtCore.QEvent.ToolTip:
            QtGui.QToolTip.hideText()
            QtGui.QToolTip.showText(event.globalPos(), self.ttstr)
            return True
        else:
            QtGui.QToolTip.hideText()

        return super(self.__class__, self).event(event)

    def OnLeave(self, event):
        TopWindowSingleton.SetStatusText('', 0)
    def BindFunc(self, func):
        self.binds += [func]
    def _OnStageChange(self):
        for bind in self.binds:
            bind(self.GetCurStage())
    def SetStep(self, evt):
        self.state = self.states.index("Step")
        self.repaint()
        self._OnStageChange()
        self.SetToolTipString(self.msgs[self.state])
    def SetBeat(self, evt):
        self.state = self.states.index("Beat")
        self.repaint()
        self._OnStageChange()
        self.SetToolTipString(self.msgs[self.state])
    def SetMinute(self, evt):
        self.state = self.states.index("Minute")
        self.repaint()
        self._OnStageChange()
        self.SetToolTipString(self.msgs[self.state])
    def OnContextMenu(self, evt):
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
            self.popupID3 = wx.NewId()
            self.Bind(wx.EVT_MENU, self.SetStep, id=self.popupID1)
            self.Bind(wx.EVT_MENU, self.SetBeat, id=self.popupID2)
            self.Bind(wx.EVT_MENU, self.SetMinute, id=self.popupID3)
        menu = wx.Menu()
        item = wx.MenuItem(menu, self.popupID1,"Step View")
        menu.AppendItem(item)
        item = wx.MenuItem(menu, self.popupID2,"Beat View")
        menu.AppendItem(item)
        item = wx.MenuItem(menu, self.popupID3,"Minute View")
        menu.AppendItem(item)
        self.PopupMenu(menu)
        menu.Destroy()

    def OnLeave(self, event):
        TopWindowSingleton.SetStatusText('', 0)
    def BindFunc(self, func):
        self.binds += [func]
    def _OnStageChange(self):
        for bind in self.binds:
            bind(self.GetCurStage())
    def GetCurStage(self):
        return self.states[self.state]
    def SetNextStage(self, evt=None):
        self.state += 1
        if self.state >= len(self.states):
            self.state = 0
        self._OnStageChange()
        TopWindowSingleton.SetStatusText(self.GetCurStage(), 0)
        self.SetToolTipString(self.msgs[self.state])
        self.repaint()

    def OnButtonEvent(self, event):
        pos = event.GetPosition().Get()
        if InRect(0, 0, 13, 13, pos[0], pos[1]):
            TopWindowSingleton.SetStatusText(self.GetCurStage(), 0)

        if event.LeftDown() or event.LeftDClick():
            self.SetFocus()
            self.CaptureMouse()
            self.startPos = event.GetPosition().Get()[1]
            self.startPosX = event.GetPosition().Get()[0]
            if InRect(0, 0, self.size[0], self.size[1], pos[0], pos[1]):
                self.SetNextStage()

        elif event.LeftUp():
            self.ldragging = False
            try:
                self.ReleaseMouse()
            except:
                pass

    def GetValue3(self):
        return self.value3
    def SetValue3(self, val):
        self.value3 = val
        self.repaint()
    def SetMinMax3(self, min, max):
        self.minmax3 = (min, max)
    def GetMinValue3(self):
        return self.minmax3[0]
    def GetMaxValue3(self):
        return self.minmax3[1]
    def GetValue3(self):
        return self.value2
    def SetValue2(self, val):
        self.value2 = val
        self.repaint()
    def SetMinMax2(self, min, max):
        self.minmax2 = (min, max)
    def GetMinValue2(self):
        return self.minmax2[0]
    def GetMaxValue2(self):
        return self.minmax2[1]
    def GetValue(self):
        return self.value
    def SetValue(self, val):
        self.value = val
        self.repaint()
    def SetMinMax(self, min, max):
        self.minmax = (min, max)
    def GetMinValue(self):
        return self.minmax[0]
    def GetMaxValue(self):
        return self.minmax[1]
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self.Draw(painter)
        QtGui.QFrame.paintEvent(self, event)

    def Draw(self, painter):
        bmp = LoadBitmap('playingpos.png')
        painter.drawPixmap(0,0, bmp)
        valueStr = `self.value`
        while len(valueStr) < 4:
            valueStr = "0" + valueStr

        value2Str = `self.value2`
        while len(value2Str) < 2:
            value2Str = "0" + value2Str

        value3Str = `self.value3`
        while len(value3Str) < 3:
            value3Str = "0" + value3Str

        imgs = [(`i`, LoadBitmap(`i`+".png")) for i in range(10)]
        imgsD = {}
        for img in imgs:
            imgsD[img[0]] = img[1]
        i = 0
        for num in valueStr:
            painter.drawPixmap(2+i*7,2, imgsD[num])
            i += 1

        i = 0
        for num in value2Str:
            painter.drawPixmap(2+4*7+3+i*7,2, imgsD[num])
            i += 1

        i = 0
        for num in value3Str:
            painter.drawPixmap(2+4*7+3+2*7+3+i*7,2, imgsD[num])
            i += 1


class Tempo_(QtGui.QFrame):
    def __init__(self, parent):
        QtGui.QFrame.__init__(self,parent,size=QtCore.QSize(48,15))
        self.binds = []
        self.value = 0
        self.value2 = 0
        self.value3 = 0
        self.SetMinMax(1, 9999)
        self.SetMinMax2(0, 99)

        try:
            self.SetTempo(pickle.load(open("testtempo.pkl", "r")))
        except:
            self.SetTempo(120.00)
        self.key = 69
        self.beatdivisor = 12
        self.tempos = GetTempos(self.key, self.beatdivisor, 40, 300)

        self.SetToolTipString("Tempo (Press down shift key+drag to snap tempo to set frequency, right click to show menu)")
        self.ldragging = False
        self.startValue = self.value
        # 음.... 1픽셀당 1퍼센트 움직이게 하자.
        self.accuracy = 0.2/9999.0
        self.accuracy2 = 0.2/99.0
        self.fractionLen = 3
        self.setFrameStyle(QtGui.QFrame.Panel | QtGui.QFrame.Sunken)
        self.setLineWidth(1)
        """
        마우스 이벤트랑 컨텍스트 메뉴 고치면 됨.
        """

        self.menu = QtGui.QMenu( self ) 
        self.menu.addAction("Set Tempo", self.OnSetValue) 
        self.menu.addAction("Set Key", self.OnSetKey) 
        self.menu.addAction("Set Beat Divisor", self.OnSetBeatDivisor) 

    def minimumSizeHint(self):
        return QtCore.QSize(48, 15)

    def sizeHint(self):
        return QtCore.QSize(48, 15)

    def SetToolTipString(self, ttstr):
        self.ttstr = ttstr
    def event(self, event):
        if event.type() == QtCore.QEvent.ToolTip:
            QtGui.QToolTip.hideText()
            QtGui.QToolTip.showText(event.globalPos(), self.ttstr)
            return True
        else:
            QtGui.QToolTip.hideText()

        return super(self.__class__, self).event(event)

    def GetTempo(self):
        return float(`self.value` + '.' + `self.value3`.split("L")[0])
    def SetTempo(self, tempo):
        st = str(tempo)
        st = st.split(".")
        self.value = int(st[0])
        self.value2 = int(st[1][:2])
        self.value3 = int(st[1])
        self.repaint()
        f2 = open("testtempo.pkl", "wb")
        pickle.dump(self.GetTempo(), f2)
        f2.close()


    def OnSetBeatDivisor(self):
        dlg = TextEntryDialogManager('Set Beat Divisor', 'Set Beat Divisor(Tempos only can be divided by beat divisor will be used when shift dragging)', `self.beatdivisor`)
        result = dlg.DoModal()
        if result:
            try:
                self.beatdivisor = int(result)
            except:
                pass

            self.tempos = GetTempos(self.key, self.beatdivisor, 40, 300)

    def OnSetKey(self):
        labels = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        keyToLabel = [labels[i%12]+`(i/12)-2` for i in range(9*12)]
        dlg = TextEntryDialogManager('Set Key', 'Set Key(ex: c3, C3, C#3, G3, A4, 69; Range: C-2 ~ B7)', keyToLabel[self.key])
        result = dlg.DoModal()
        if result:
            val = result
            try:
                key = int(val)
            except:
                try:
                    key = val.upper()
                    key = keyToLabel.index(key)
                except:
                    key = 69
            self.key = key
            self.tempos = GetTempos(self.key, self.beatdivisor, 40, 300)

    def OnSetValue(self):
        dlg = TextEntryDialogManager('Set Tempo', 'Set Tempo(0.00000000000000~9999.99999999999999)', `self.value`+"."+`self.value3`)
        result = dlg.DoModal()

        if result:
            try:
                num = float(result)
                num1 = int(num)
                num2 = int(math.ceil((num-int(num))*100))
                num3 = num2
                s = str(num)
                f = s.find(".")
                if f != -1:
                    num3 = int(s[f+1:])
                if num1 > 9999:
                    num1 = 9999
                if num1 < 0:
                    num1 = 0
                if num2 > 99:
                    num2 = 99
                if num2 < 0:
                    num2 = 0
                self.SetValue(num1)
                self.SetValue2(num2)
                self.value3 = num3
            except:
                pass

    def BindOnTempoChange(self, func):
        self.binds += [func]
    def _OnTempoChange(self, tempo):
        f2 = open("testtempo.pkl", "wb")
        pickle.dump(self.GetTempo(), f2)
        f2.close()

        #for bind in self.binds:
        #    bind(tempo)
        #    not really used

    def mousePressEvent(self, event):
        if event.button() == LMB:
            pos = event.pos().x(), event.pos().y()

            x, w = 2, 4*7
            y = 0
            h = 15
            x2, w2 = 2+4*7+3, 2*7
            tempos = self.tempos
            tempos = [str(tempo) for tempo in tempos]
            tempos.reverse()
            self.startPos = pos[1]
            self.startPosX = pos[0]
            def GetNearestTempo(srcTempo):
                nearest = 999999.0
                nearestStr = `nearest`
                for tem in tempos:
                    if abs(nearest-srcTempo) > abs(float(tem)-srcTempo):
                        nearest = float(tem)
                        nearestStr = tem
                return nearestStr

            if ShiftOn():
                self.startTempo = GetNearestTempo(self.GetTempo())
            else:
                self.startTempo = None
            if InRect(x,y,w,h, pos[0], pos[1]):
                self.startValue = self.value
                self.ldragging = True
            elif InRect(x2,y,w2,h, pos[0], pos[1]):
                self.startValue = self.value2
                self.ldragging = True

        elif event.button() == RMB:
            self.menu.exec_( self.mapToGlobal(event.pos()) ) 


    def mouseMoveEvent(self, ev):
        x, w = 2, 4*7
        y = 0
        h = 15
        x2, w2 = 2+4*7+3, 2*7

        tempos = self.tempos
        tempos = [str(tempo) for tempo in tempos]
        tempos.reverse()
        if self.ldragging:
            if ShiftOn() and self.startTempo:
                curPos = ev.pos().y()
                offset = (curPos-self.startPos)
                offset = float(offset)*0.25
                newIdx = tempos.index(self.startTempo) - int(offset)
                if newIdx > len(tempos)-1:
                    newIdx = len(tempos)-1
                if newIdx < 0:
                    newIdx = 0
                newStrTempo = tempos[newIdx]
                self.value = int(newStrTempo.split(".")[0])
                self.value2 = int(newStrTempo.split(".")[1][:2])
                self.value3 = int(newStrTempo.split(".")[1])
                self._OnTempoChange(self.GetTempo())
                self.repaint()
            else:
                if x <= self.startPosX < x+w:
                    curPos = ev.pos().y()
                    offset = (curPos-self.startPos)
                    offset = float(offset)*((self.GetMaxValue()-self.GetMinValue())*self.accuracy)
                    value = int(self.startValue-offset)
                    if value > self.GetMaxValue():
                        value = self.GetMaxValue()
                    if value < self.GetMinValue():
                        value = (self.GetMinValue())
                    self.SetValue(value)
                elif x2 <= self.startPosX < x2+w2:
                    curPos = ev.pos().y()
                    offset = (curPos-self.startPos)
                    offset = float(offset)*((self.GetMaxValue2()-self.GetMinValue2())*self.accuracy2)
                    value = int(self.startValue-offset)
                    if value > self.GetMaxValue2():
                        value = self.GetMaxValue2()
                    if value < self.GetMinValue2():
                        value = self.GetMinValue2()
                    self.value3 = value
                    self.SetValue2(value)


    def mouseReleaseEvent(self, ev):
        self.ldragging = False

    def GetValue2(self):
        return self.value2
    def SetValue2(self, val):
        self.value2 = val
        self._OnTempoChange(self.GetTempo())
        self.repaint()
    def SetMinMax2(self, min, max):
        self.minmax2 = (min, max)
    def GetMinValue2(self):
        return self.minmax2[0]
    def GetMaxValue2(self):
        return self.minmax2[1]
    def GetValue(self):
        return self.value
    def SetValue(self, val):
        self.value = val
        self._OnTempoChange(self.GetTempo())
        self.repaint()
    def SetMinMax(self, min, max):
        self.minmax = (min, max)
    def GetMinValue(self):
        return self.minmax[0]
    def GetMaxValue(self):
        return self.minmax[1]
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self.Draw(painter)
        QtGui.QFrame.paintEvent(self, event)
    def Draw(self, painter):
        bmp = LoadBitmap('tempo.png')
        painter.drawPixmap(0,0, bmp)
        valueStr = `self.value`
        while len(valueStr) < 4:
            valueStr = "0" + valueStr

        value2Str = `self.value2`
        while len(value2Str) < 2:
            value2Str = "0" + value2Str

        imgs = [(`i`, LoadBitmap(`i`+".png")) for i in range(10)]
        imgsD = {}
        for img in imgs:
            imgsD[img[0]] = img[1]
        i = 0
        nonZeroFound = False
        for num in valueStr:
            if num == "0" and not nonZeroFound:
                i += 1
                continue
            else:
                nonZeroFound = True
            painter.drawPixmap(2+i*7,2, imgsD[num])
            i += 1

        i = 0
        for num in value2Str:
            painter.drawPixmap(2+4*7+3+i*7,2,  imgsD[num])
            i += 1


class MultiStateButton(QtGui.QWidget):
    def __init__(self, parent):
        QtGui.QWidget.__init__(self,parent,size=QtCore.QSize(13,13))
        self.states = ["On", "Solo", "Mute"]
        self.msgs = ["On (Click to change to Solo, Right click to show menu)",
                "Solo (Click to change to Mute, Right click to show menu)",
                "Mute (Click to change to On, Right click to show menu)"]
        self.state = self.states.index("On")
        self.ttstr = ''
        self.SetToolTipString(self.msgs[self.state])
        self.binds = []

        self.menu = QtGui.QMenu(self) 
        self.menu.addAction("On", self.SetOn) 
        self.menu.addAction("Solo", self.SetSolo) 
        self.menu.addAction("Mute", self.SetMute) 
    def SetToolTipString(self, ttstr):
        self.ttstr = ttstr
    def event(self, event):
        if event.type() == QtCore.QEvent.ToolTip:
            QtGui.QToolTip.hideText()
            QtGui.QToolTip.showText(event.globalPos(), self.ttstr)
            return True
        else:
            QtGui.QToolTip.hideText()

        return super(self.__class__, self).event(event)

    def SetOn(self):
        self.state = self.states.index("On")
        self.repaint()
        self._OnStageChange()
        self.SetToolTipString(self.msgs[self.state])
    def SetSolo(self):
        self.state = self.states.index("Solo")
        self.repaint()
        self._OnStageChange()
        self.SetToolTipString(self.msgs[self.state])
    def SetMute(self):
        self.state = self.states.index("Mute")
        self.repaint()
        self._OnStageChange()
        self.SetToolTipString(self.msgs[self.state])

    def leaveEvent(self, ev):
        StatusBarSingleton.showMessage('')
    def BindFunc(self, func):
        self.binds += [func]
    def _OnStageChange(self):
        for bind in self.binds:
            bind(self.GetCurStage())
    def GetCurStage(self):
        return self.states[self.state]
    def SetNextStage(self, evt=None):
        self.state += 1
        if self.state >= len(self.states):
            self.state = 0
        self._OnStageChange()
        StatusBarSingleton.showMessage(self.GetCurStage())
        self.SetToolTipString(self.msgs[self.state])
        self.repaint()
    def mousePressEvent(self, ev):
        pos = ev.pos().x(), ev.pos().y()

        if ev.button() == LMB:
            if InRect(0, 0, 13, 13, pos[0], pos[1]):
                StatusBarSingleton.showMessage(self.GetCurStage())
            if InRect(0, 0, 13, 13, pos[0], pos[1]):
                self.SetNextStage()
        elif ev.button() == RMB:
            self.menu.exec_( self.mapToGlobal(ev.pos()) ) 

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self.Draw(painter)
    def Draw(self, painter):
        bmps = ["on.png", "solo.png", "mute.png"]
        bmp = LoadBitmap(bmps[self.state])
        painter.drawPixmap(0,0, bmp)


TopWindowSingleton = None
class Knob(QtGui.QWidget):
    def __init__(self, parent):
        apply(QtGui.QWidget.__init__, (self,parent))
        self.resize(23,23)
        self.SetMinMax(0, 1)
        self.SetValue(0)
        self.ldragging = False
        self.startValue = self.value
        # 음.... 1픽셀당 1퍼센트 움직이게 하자.
        self.accuracy = 0.5/100.0
        self.fractionLen = 3
        self.binds = []

        self.ttstr = ''
    def SetToolTipString(self, ttstr):
        self.ttstr = ttstr
    def event(self, event):
        if event.type() == QtCore.QEvent.ToolTip:
            QtGui.QToolTip.hideText()
            QtGui.QToolTip.showText(event.globalPos(), self.ttstr)
            return True
        else:
            QtGui.QToolTip.hideText()

        return super(self.__class__, self).event(event)

    def minimumSizeHint(self):
        return QtCore.QSize(23, 23)

    def sizeHint(self):
        return QtCore.QSize(23, 23)

    def SetStatVal(self):
        valText = `self.value`
        decPnt = valText.find(".")
        if decPnt != -1:
            valText = valText[:decPnt+self.fractionLen+1]
        StatusBarSingleton.showMessage(valText)
    def enterEvent(self, ev):
        self.SetStatVal()
    def leaveEvent(self, event):
        StatusBarSingleton.showMessage('')

    def BindRDown(self, func): # func(knob)
        self.binds += [func]

    def mouseMoveEvent(self, ev):
        curPos = ev.pos().y()
        offset = (curPos-self.startPos)
        offset = float(offset)*((self.GetMaxValue()-self.GetMinValue())*self.accuracy)
        value = self.startValue-offset
        if value > self.GetMaxValue():
            value = self.GetMaxValue()
        if value < self.GetMinValue():
            value = self.GetMinValue()
        self.SetValue(value)
        self.SetStatVal()

    def mousePressEvent(self, ev):
        if ev.button() == LMB:
            self.startPos = ev.pos().y()
            self.startValue = self.value
        elif ev.button() == RMB:
            for func in self.binds:
                func(ev, self)
        """
        pos = event.GetPosition().Get()

        if pos[0] < 23 and pos[1] < 23:
            #set value to status
            SetStatVal()
        else:
            pass
            #clear status? no. it will conflict with others
            # but if you use queueing system it will be very good. clearing stat msgs while not in the rect..
        if event.LeftDown():
            self.SetFocus()
            self.CaptureMouse()
            #self.drawing = True
            self.startPos = event.GetPosition().Get()[1]
            self.startValue = self.value
            self.ldragging = True

        elif event.Dragging():
            if self.ldragging:
                pass

        elif event.LeftUp():
            TopWindowSingleton.SetStatusText('', 0)
            self.ldragging = False
            try:
                self.ReleaseMouse()
            except:
                pass
        """

    def GetValue(self):
        return self.value
    def SetValue(self, val):
        self.value = val
        self.repaint()
    def SetMinMax(self, min, max):
        self.minmax = (min, max)
    def GetMinValue(self):
        return self.minmax[0]
    def GetMaxValue(self):
        return self.minmax[1]
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        self.Draw(painter)

    def Draw(self, painter):
        # help text라는 컨트롤이 있으면 그걸 쓴다. knob의 값을 거기서 보여준다.
        bmp = LoadBitmap('knob.png')
        painter.drawPixmap(0,0, bmp)
        value = self.GetValue()
        min = self.GetMinValue()
        max = self.GetMaxValue()
        normalizedMax = max - min
        value -= min
        value = float(value) / float(normalizedMax)
        maxTheta = (math.pi/4)*6
        theta = maxTheta*value
        #theta *= -1
        theta += 3*math.pi/4
        #minTheta = (math.pi/4)*5
        #maxTheta = (math.pi/4)*7
        # 일단 theta값을 뒤집고(-1곱합?) +3*math.pi/4 해주면 된다.
        x1 = 11
        y1 = 11
        x2 = int(math.cos(theta)*9)+11
        y2 = int(math.sin(theta)*9)+11
        col = QtGui.QColor(0, 0, 0)
        painter.setPen(QtGui.QPen(col))
        painter.setBrush(QtGui.QBrush(col))
        painter.drawLine(x1, y1, x2, y2)
    # Knob이 있는 모든 컨트롤에서 이 Knob을 쓰게 하고 복붙 하지 않는다.

class Sizer:
    def __init__(self, parent, horizontal = True):
        self.parent = parent
        self.widgets = []
        self.gap = 0
        self.horizontal = horizontal

    def SetGap(self, gap):
        self.gap = gap
    def AddWidget(self, widget):
        self.widgets += [widget]

    def SetLayout(self):
        lastPos = 0
        largestSize = 0
        for widget in self.widgets:
            w,h = widget.size().width(), widget.size().height()
            if self.horizontal:
                if largestSize < h:
                    largestSize = h
            else:
                if largestSize < w:
                    largestSize = w
        for widget in self.widgets:
            w,h = widget.size().width(), widget.size().height()
            if self.horizontal:
                offset = (largestSize - h)/2
                widget.move(lastPos, offset)
                lastPos += self.gap + widget.size().width()
            else:
                offset = (largestSize - w)/2
                widget.move(offset, lastPos)
                lastPos += self.gap + widget.size().height()


class TextEntryDialog(QtGui.QDialog):
    def __init__(self, title, msg, value, Set):
        super(TextEntryDialog, self).__init__(None, Qt.WindowTitleHint | Qt.WindowSystemMenuHint)
        self.setWindowTitle(title)
        self.Set = Set

        extensionLayout = QtGui.QVBoxLayout()
        extensionLayout.setMargin(10)
        label = QtGui.QLabel(msg)
        extensionLayout.addWidget(label)
        self.lineEdit = lineEdit = QtGui.QLineEdit()
        self.lineEdit.setText(value)
        extensionLayout.addWidget(lineEdit)

        buttonsL = QtGui.QHBoxLayout()

        btn1 = QtGui.QPushButton("OK")
        self.connect(btn1, QtCore.SIGNAL("clicked()"),
                     self.OnOK)
        btn1.setDefault(True)
        btn2 = QtGui.QPushButton("Cancel")
        self.connect(btn2, QtCore.SIGNAL("clicked()"),
                     self.OnCancel)
        buttonsL.addWidget(btn1)
        buttonsL.addWidget(btn2)
        extensionLayout.addLayout(buttonsL)
        self.setLayout(extensionLayout)

    def OnOK(self):
        self.Set(str(self.lineEdit.text()))
        self.accept()
    def OnCancel(self):
        self.reject()

class TextEntryDialogManager:
    def __init__(self, title, msg, value):
        self.dialog = TextEntryDialog(title, msg, value, self.SetValue)
        self.value = value
    def DoModal(self):
        if self.dialog.exec_():
            return self.value
        else:
            return None

    def SetValue(self, txt):
        self.value = txt

class InstrumentPanel(QtGui.QWidget):
    # 심심하니 FL Studio같은 비트 에디터를 만들자. Piano Roll View버튼도 넣는다. 필수인데 너무 이 버튼을 안 넣음...
    def __init__(self, parent, fileName):
        apply(QtGui.QWidget.__init__, (self,parent))
        self.parent = parent

        self.vst = VSTWindow(fileName, self, True)

        sizer = Sizer(self)
        sizer.SetGap(5)

        msb = MultiStateButton(self)
        sizer.AddWidget(msb)

        knob = Knob(self)
        knob.SetMinMax(0, 0xFF)
        knob.SetValue(215)
        knob.SetToolTipString("Volume")
        #knob.Bind(wx.EVT_CONTEXT_MENU, self.OnVolumeContext)
        knob.BindRDown(self.OnVolumeContext)
        self.volume = knob
        sizer.AddWidget(knob)
        self.volumeMenu = QtGui.QMenu(knob) 
        self.volumeMenu.addAction("Set Volume", self.OnSetVolume) 


        knob = Knob(self)
        knob.SetToolTipString("Panning")
        knob.SetMinMax(-1, 1)
        knob.SetValue(0)
        knob.BindRDown(self.OnPanContext)
        #knob.Bind(wx.EVT_CONTEXT_MENU, self.OnPanContext)
        self.pan = knob
        sizer.AddWidget(knob)
        self.panMenu = QtGui.QMenu(knob) 
        self.panMenu.addAction("Set Panning", self.OnSetPan) 

        btn = QtGui.QPushButton(self.vst.vstEff.get_name(), self, size=QtCore.QSize(70, 23))
        sizer.AddWidget(btn)
        self.connect(btn, QtCore.SIGNAL("clicked()"),
                    self.OnShowGUI)
        #btn.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        #btn.SetToolTipString("Instrument; Right-click to show menu")
        #sizer.addWidget(btn)

        btn1 = BitmapButton('proll.png', QtCore.QSize(23, 23), self)
        sizer.AddWidget(btn1)
        #self.prBtn = btn.SetToolTipString("Piano Roll")
        #btn.Bind(wx.EVT_CONTEXT_MENU, lambda evt: None)
        #sizer.addWidget(btn)

        btn = BitmapButton('keysel.png', QtCore.QSize(23, 23), self)
        sizer.AddWidget(btn)

        beat = BeatEditor(self)
        sizer.AddWidget(beat)

        sizer.SetLayout()
        self.connect(btn1, QtCore.SIGNAL("clicked()"),
                     beat.OnPianoRoll)

        self.notes = {}

        """
        비트 키 셀렉터는 그냥 간단하게 팝업 다얄로그에다가 리스트 컨트롤 넣고 리스트 아이템 클릭할 때마다 소리나게 하고
        OK누르면 그 키로 하게 하면 됨.
        리스트 아이템이 바뀔 때마다 소리가 나는게 아니라 리스트 아이템이 클릭될 때마다 소리나야함
        
        그 전에 음 툴바를 만들자.
        """
    def minimumSizeHint(self):
        return QtCore.QSize(PatternManagerWidth, 30)

    def sizeHint(self):
        return QtCore.QSize(PatternManagerWidth, 30)

    def OnReplace(self, evt):
        pass
    def OnInsert(self, evt):
        self.parent.OnInsert(evt)
    def OnDelete(self, evt):
        pass
    def OnShowGUI(self):
        self.vst.OpenGUI()

    def OnSetPan(self):
        dlg = TextEntryDialogManager('Set Panning', 'Set Panning(-1.0~1.0; 0 means center; -1.0 means fully left channel only; 1.0 means fully right channel only.)', `self.pan.GetValue()`)
        result = dlg.DoModal()
        if result:
            try:
                num = float(result)
                if num > 1.0:
                    num = 1.0
                if num < -1.0:
                    num = -1.0
                self.pan.SetValue(num)
            except:
                pass
    def OnPanContext(self, ev, knob):
        self.panMenu.exec_( knob.mapToGlobal(ev.pos()) ) 
    def OnSetVolume(self):
        dlg = TextEntryDialogManager('Set Volume', 'Set Volume(0~255)', `self.volume.GetValue()`)
        result = dlg.DoModal()
        if result:
            try:
                num = int(result)
                if num > 255:
                    num = 255
                if num < 0:
                    num = 0
                self.volume.SetValue(num)
            except:
                pass

    def OnVolumeContext(self, ev, knob):
        self.volumeMenu.exec_( knob.mapToGlobal(ev.pos()) ) 
    def OnContextMenu(self, event):
        # only do this part the first time so the events are only bound once
        #
        # Yet another anternate way to do IDs. Some prefer them up top to
        # avoid clutter, some prefer them close to the object of interest
        # for clarity. 
        if not hasattr(self, "popupID1"):
            for i in range(30):
                setattr(self, "popupID" + `i+1`, wx.NewId())

            self.Bind(wx.EVT_MENU, self.OnReplace, id=self.popupID1)
            self.Bind(wx.EVT_MENU, self.OnInsert, id=self.popupID2)
            self.Bind(wx.EVT_MENU, self.OnDelete, id=self.popupID3)
            self.Bind(wx.EVT_MENU, self.OnShowGUI, id=self.popupID4)
            self.Bind(wx.EVT_MENU, self.OnShowGUI, id=self.popupID5)
            self.Bind(wx.EVT_MENU, self.OnShowGUI, id=self.popupID6)
            self.Bind(wx.EVT_MENU, self.OnShowGUI, id=self.popupID7)
            """
            self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
            self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
            self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
            self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)
            self.Bind(wx.EVT_MENU, self.OnPopupSix, id=self.popupID6)
            self.Bind(wx.EVT_MENU, self.OnPopupSeven, id=self.popupID7)
            self.Bind(wx.EVT_MENU, self.OnPopupEight, id=self.popupID8)
            self.Bind(wx.EVT_MENU, self.OnPopupNine, id=self.popupID9)
            """

        menu = wx.Menu()
        menu.Append(self.popupID4, "Show GUI")
        menu.AppendSeparator()
        menu.Append(self.popupID15, "Rename")
        menu.AppendSeparator()
        item = wx.MenuItem(menu, self.popupID1,"Replace")
        menu.AppendItem(item)
        menu.Append(self.popupID2, "Insert")
        menu.Append(self.popupID3, "Delete")
        menu.Append(self.popupID5, "Clone")
        menu.AppendSeparator()
        sm = wx.Menu()
        sm.Append(self.popupID6, "Cut")
        sm.Append(self.popupID7, "Copy")
        sm.Append(self.popupID8, "Paste")
        sm.AppendSeparator()
        sm.Append(self.popupID14, "Shift Left")
        sm.Append(self.popupID13, "Shift Right")
        menu.AppendMenu(self.popupID12, "Beat Edit", sm)
        menu.AppendSeparator()
        menu.Append(self.popupID9, "Fill Each 2 Steps")
        menu.Append(self.popupID10, "Fill Each 4 Steps")
        menu.Append(self.popupID11, "Fill Each 8 Steps")
        """
        menu.Append(self.popupID2, "Two")
        menu.Append(self.popupID3, "Three")
        menu.Append(self.popupID4, "Four")
        menu.Append(self.popupID5, "Five")
        menu.Append(self.popupID6, "Six")
        # make a submenu
        sm = wx.Menu()
        sm.Append(self.popupID8, "sub item 1")
        sm.Append(self.popupID9, "sub item 1")
        menu.AppendMenu(self.popupID7, "Test Submenu", sm)
        """


        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu)
        menu.Destroy()

class PatternManagerFrame(QtGui.QScrollArea):
    def __init__(self, parent):
        """
 QLabel *imageLabel = new QLabel;
 QImage image("happyguy.png");
 imageLabel->setPixmap(QPixmap.fromImage(image));

 scrollArea = new QScrollArea;
 scrollArea->setBackgroundRole(QPalette.Dark);
 scrollArea->setWidget(imageLabel);
class HelloWindow(QMainWindow):

    def __init__(self, *args):
        self.button=HelloButton(self)
        self.setCentralWidget(self.button)

        """
        apply(QtGui.QScrollArea.__init__, (self,))
        self.pMgr = PatternManager(parent)
        self.setWidget(self.pMgr)
        self.setWindowTitle("Instruments/Pattern Manager")
    def GetPatternManager(self):
        return self.pMgr
    def closeEvent(self, ev):
        if not g_WindowClosed:
            ev.ignore()



 
class MultiChoiceDialog(QtGui.QDialog):
    def __init__(self, title, msg, lst, selectedIdxList, Add, Remove):
        super(MultiChoiceDialog, self).__init__(None, Qt.WindowTitleHint | Qt.WindowSystemMenuHint)
        self.setWindowTitle(title)
        self.lst = lst
        self.Add = Add
        self.Remove = Remove

        model = QtGui.QStandardItemModel() 
        self.connect(model, QtCore.SIGNAL("itemChanged (QStandardItem *)"),
                     self.OnItemChange)

        for lstidx in range(len(lst)):
            itemText = lst[lstidx]
            item = QtGui.QStandardItem(itemText) 
            if lstidx in selectedIdxList:
                check = Qt.Checked
            else:
                check = Qt.Unchecked 
            item.setCheckState(check) 
            item.setCheckable(True) 
            item.setEditable(False)
            model.appendRow(item) 
        
        
        view = QtGui.QListView() 
        view.setModel(model) 
        extensionLayout = QtGui.QVBoxLayout()
        extensionLayout.setMargin(10)
        label = QtGui.QLabel(msg)
        extensionLayout.addWidget(label)
        extensionLayout.addWidget(view)

        buttonsL = QtGui.QHBoxLayout()

        btn1 = QtGui.QPushButton("OK")
        self.connect(btn1, QtCore.SIGNAL("clicked()"),
                     self.OnOK)
        btn1.setDefault(True)
        btn2 = QtGui.QPushButton("Cancel")
        self.connect(btn2, QtCore.SIGNAL("clicked()"),
                     self.OnCancel)
        buttonsL.addWidget(btn1)
        buttonsL.addWidget(btn2)
        extensionLayout.addLayout(buttonsL)
        self.setLayout(extensionLayout)

    def OnOK(self):
        self.accept()
    def OnCancel(self):
        self.reject()
    def OnItemChange(self, item):
        if item.checkState() == Qt.Checked:
            try:
                self.Add(item.index().row())
            except:
                pass
        else:
            try:
                self.Remove(item.index().row())
            except:
                pass

class MultiChoiceDialogManager:
    def __init__(self, title, msg, lst, selectedIdx):
        self.dialog = MultiChoiceDialog(title, msg, lst, selectedIdx, self.AddSelection, self.RemoveSelection)
        self.selectedIdx = selectedIdx
    def DoModal(self):
        if self.dialog.exec_():
            return self.selectedIdx
        else:
            return None

    def AddSelection(self, idx):
        self.selectedIdx += [idx]
        self.selectedIdx = list(set(self.selectedIdx))
    def RemoveSelection(self, idx):
        lidx = self.selectedIdx.index(idx)
        del self.selectedIdx[lidx]

class SingleChoiceDialog(QtGui.QDialog):
    def __init__(self, title, msg, lst, SetSelectionFunc):
        super(SingleChoiceDialog, self).__init__(None, Qt.WindowTitleHint | Qt.WindowSystemMenuHint)
        self.setWindowTitle(title)
        self.lst = lst
        self.SetSelection = SetSelectionFunc

        self.listBox = QtGui.QListWidget()
        QtCore.QObject.connect(self.listBox, QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.OnItemSelect)
        QtCore.QObject.connect(self.listBox, QtCore.SIGNAL("itemActivated(QListWidgetItem *)"), self.OnItemDoubleClick)
        QtCore.QObject.connect(self.listBox, QtCore.SIGNAL("itemSelectionChanged ()"), self.OnItemSelectionChanged)
        
        for item in lst:
            self.listBox.addItem(QtCore.QString(item))
        extensionLayout = QtGui.QVBoxLayout()
        extensionLayout.setMargin(10)
        label = QtGui.QLabel(msg)
        extensionLayout.addWidget(label)
        extensionLayout.addWidget(self.listBox)

        buttonsL = QtGui.QHBoxLayout()

        btn1 = QtGui.QPushButton("OK")
        self.connect(btn1, QtCore.SIGNAL("clicked()"),
                     self.OnOK)
        btn1.setDefault(True)
        btn2 = QtGui.QPushButton("Cancel")
        self.connect(btn2, QtCore.SIGNAL("clicked()"),
                     self.OnCancel)
        buttonsL.addWidget(btn1)
        buttonsL.addWidget(btn2)
        extensionLayout.addLayout(buttonsL)
        self.setLayout(extensionLayout)

    def OnItemSelect(self, item):
        txt = str(item.text())
        self.SetSelection((self.lst.index(txt), txt))
    def OnItemDoubleClick(self, item):
        self.OnItemSelect(item)
        self.accept()
    def OnItemSelectionChanged(self):
        try:
            self.OnItemSelect(self.listBox.selectedItems()[0])
        except:
            pass
    def OnOK(self):
        self.accept()
    def OnCancel(self):
        self.reject()


class SingleChoiceDialogManager:
    def __init__(self, title, msg, lst):
        self.dialog = SingleChoiceDialog(title, msg, lst, self.SetSelection)
        self.selection = None # (index, value)
    def DoModal(self):
        if self.dialog.exec_():
            return self.selection
        else:
            return None

    def SetSelection(self, selection):
        self.selection = selection



class PatternManager(QtGui.QWidget):
    def __init__(self, parent):
        """
 QLabel *imageLabel = new QLabel;
 QImage image("happyguy.png");
 imageLabel->setPixmap(QPixmap.fromImage(image));

 scrollArea = new QScrollArea;
 scrollArea->setBackgroundRole(QPalette.Dark);
 scrollArea->setWidget(imageLabel);
class HelloWindow(QMainWindow):

    def __init__(self, *args):
        self.button=HelloButton(self)
        self.setCentralWidget(self.button)
        btn = wx.Button(self, wx.NewId(), "Select Path")
        self.Bind(wx.EVT_BUTTON, self.OnVSTPath, btn)
        btn2 = wx.Button(self, wx.NewId(), "Scan VST Plugins")
        self.Bind(wx.EVT_BUTTON, self.OnDumpVST, btn2)
        btn3 = wx.Button(self, wx.NewId(), "Set VST Instruments")
        self.Bind(wx.EVT_BUTTON, self.OnSetVSTI, btn3)
        btn4 = wx.Button(self, wx.NewId(), "Set VST Effects")
        self.Bind(wx.EVT_BUTTON, self.OnSetVSTE, btn4)
        sizer.Add(st, 0, wx.TOP, 5)
        sizer.Add(self.st2, 0, wx.TOP, 5)
        sizer.Add(btn, 0, wx.TOP, 5)
        sizer.Add(btn2, 0, wx.TOP, 25)
        sizer.Add(btn3, 0, wx.TOP, 25)
        sizer.Add(btn4, 0, wx.TOP, 5)
        vst, 피아노데이터로드저장
        """
        apply(QtGui.QWidget.__init__, (self,))
        self.parent = parent
        self.insPanels = []
        self.playing = False
        global PatternManagerSingleton 
        PatternManagerSingleton = self

 
        # Popup Menu 
        self.popMenu = QtGui.QMenu( self ) 
        self.popMenu.addAction("New", self.OnNew) 
        self.popMenu.addSeparator() 
        self.popMenu.addAction("New2", self.OnNew) 
        self.sizer = sizer = QtGui.QVBoxLayout()
        sizer.setMargin(2)
        self.setLayout(sizer)
        self.label = QtGui.QLabel("")


    def mousePressEvent(self, ev):
        DoPopup(self, self.popMenu, ev)

    def minimumSizeHint(self):
        return QtCore.QSize(PatternManagerWidth, 400)

    def sizeHint(self):
        return QtCore.QSize(PatternManagerWidth, 400)

    def OnInsert(self, evt):

        vsti = SettingsSingleton.GetData("VSTInstruments")
        dlg = wx.SingleChoiceDialog(
                self, 'Select VST Instrument and click OK', 'Insert VST Instrument',
                vsti, 
                wx.CHOICEDLG_STYLE
                )

        if dlg.ShowModal() == wx.ID_OK:
            fileName = dlg.GetStringSelection()
            fileName = SettingsSingleton.GetData("VSTPath") + "/" + fileName
            self.insPanels += [InstrumentPanel(self, fileName)]

            self.sizer.Add(self.insPanels[-1], 0, wx.TOP|wx.LEFT, 10)
            self.Layout()

            # 파일 이름을 읽어와서 인스트루먼트 패널을 추가한다.

        dlg.Destroy()

    def OnNew(self):
        vsti = SettingsSingleton.GetData("VSTInstruments")
        vsti.sort()
        dlg = SingleChoiceDialogManager("Select VST Instrument", "Select VST Instrument", vsti)
        result = dlg.DoModal()
        if result:
            fileName = result[1]
            fileName = SettingsSingleton.GetData("VSTPath") + "/" + fileName
            if len(self.insPanels):
                self.sizer.setStretch(len(self.insPanels), 0)
                self.sizer.removeWidget(self.label)
            self.insPanels += [InstrumentPanel(self, fileName)]
            self.resize(PatternManagerWidth, len(self.insPanels)*35+100)

            self.sizer.addWidget(self.insPanels[-1])
            self.sizer.addWidget(self.label)
            self.sizer.setStretch(len(self.insPanels), 1)


    def mousePressEvent(self, ev):
        if ev.button() == RMB:
            self.popMenu.exec_( self.mapToGlobal(ev.pos()) ) 

    def Load(self):
        insts = CurProjectSingleton.GetData("instruments")
        if insts:
            for inst in insts:
                fileName = inst["fileName"]
                self.insPanels += [InstrumentPanel(self, fileName)]
                self.insPanels[-1].notes = inst["pianoRoll"]

    def OnPlay(self):
        if self.playing:
            self.playing = False
            VSTThreadSingleton.StopNotes()
        else:
            self.playing = True
            #self.notes.midi.PlayNotes(self.notes.notes)
            VSTThreadSingleton.PlayNotes(self, None, self.MakePattern())
    
    def MakePattern(self):
        pattern = []
        for panel in self.insPanels:
            notes = {}
            for key in panel.notes.keys():
                notes[key] = panel.notes[key] + (panel.vst,)
            pattern += [notes]
        return pattern


    def OnContextMenu(self, event):
        # only do this part the first time so the events are only bound once
        #
        # Yet another anternate way to do IDs. Some prefer them up top to
        # avoid clutter, some prefer them close to the object of interest
        # for clarity. 
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
            self.popupID3 = wx.NewId()
            self.popupID4 = wx.NewId()
            self.popupID5 = wx.NewId()
            self.popupID6 = wx.NewId()
            self.popupID7 = wx.NewId()
            self.popupID8 = wx.NewId()
            self.popupID9 = wx.NewId()

            self.Bind(wx.EVT_MENU, self.OnInsert, id=self.popupID1)
            """
            self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
            self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
            self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
            self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)
            self.Bind(wx.EVT_MENU, self.OnPopupSix, id=self.popupID6)
            self.Bind(wx.EVT_MENU, self.OnPopupSeven, id=self.popupID7)
            self.Bind(wx.EVT_MENU, self.OnPopupEight, id=self.popupID8)
            self.Bind(wx.EVT_MENU, self.OnPopupNine, id=self.popupID9)
            """

        # make a menu
        menu = wx.Menu()
        # Show how to put an icon in the menu
        item = wx.MenuItem(menu, self.popupID1,"Insert")
        menu.AppendItem(item)
        # add some other items
        """
        menu.Append(self.popupID2, "Two")
        menu.Append(self.popupID3, "Three")
        menu.Append(self.popupID4, "Four")
        menu.Append(self.popupID5, "Five")
        menu.Append(self.popupID6, "Six")
        # make a submenu
        sm = wx.Menu()
        sm.Append(self.popupID8, "sub item 1")
        sm.Append(self.popupID9, "sub item 1")
        menu.AppendMenu(self.popupID7, "Test Submenu", sm)
        """

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu)
        menu.Destroy()


msg = "Some text will appear mixed in the image's shadow..."
USE_BUFFERED_DC = True

def InRect(x,y,w,h, x2, y2):
    if x <= x2 < x+w and y <= y2 < y+h:
        return True
    else:
        return False


def GetDevice():
    for loop in range(pypm.CountDevices()):
        interf,name,inp,outp,opened = pypm.GetDeviceInfo(loop)
        if loop == 9:
            return interf,name,inp,outp,opened

class MIDI(object):
    def __init__(self, parent):
        self.parent = parent
        pypm.CountDevices()
        pypm.GetDeviceInfo(9)
        latency = 50
        pypm.Initialize() # always call this first, or OS may crash when you try to open a stream
        self.midiOut = pypm.Output(9, latency)
        self.midiOut.Write([[[self.GetInstrument(0),0,0],pypm.Time()]])
        self.playingNote = None
        self.instruments = [
            "Acoustic Grand Piano",
            "Bright Acoustic Piano",
            "Electric Grand Piano",
            "Honky-tonk Piano",
            "Electric Piano 1",
            "Electric Piano 2",
            "Harpsichord",
            "Clavi",
            "Celesta",
            "1Glockenspiel",
            "Music Box",
            "Vibraphone",
            "Marimba",
            "Xylophone",
            "Tubular Bells",
            "Dulcimer",
            "Drawbar Organ",
            "Percussive Organ",
            "Rock Organ",
            "Church Organ",
            "Reed Organ",
            "Accordion",
            "Harmonica",
            "Tango Accordion",
            "Acoustic Guitar (nylon)",
            "Acoustic Guitar (steel)",
            "Electric Guitar (jazz)",
            "Electric Guitar (clean)",
            "Electric Guitar (muted)",
            "Overdriven Guitar",
            "Distortion Guitar",
            "Guitar harmonics",
            "Acoustic Bass",
            "Electric Bass (finger)",
            "Electric Bass (pick)",
            "Fretless Bass",
            "Slap Bass 1",
            "Slap Bass 2",
            "Synth Bass 1",
            "Synth Bass 2",
            "Violin",
            "Viola",
            "Cello",
            "Contrabass",
            "Tremolo Strings",
            "Pizzicato Strings",
            "Orchestral Harp",
            "Timpani",
            "String Ensemble 1",
            "String Ensemble 2",
            "SynthStrings 1",
            "SynthStrings 2",
            "Choir Aahs",
            "Voice Oohs",
            "Synth Voice",
            "Orchestra Hit",
            "Trumpet",
            "Trombone",
            "Tuba",
            "Muted Trumpet",
            "French Horn",
            "Brass Section",
            "SynthBrass 1",
            "SynthBrass 2",
            "Soprano Sax",
            "Alto Sax",
            "Tenor Sax",
            "Baritone Sax",
            "Oboe",
            "English Horn",
            "Bassoon",
            "Clarinet",
            "Piccolo",
            "Flute",
            "Recorder",
            "Pan Flute",
            "Blown Bottle",
            "Shakuhachi",
            "Whistle",
            "Ocarina",
            "Lead 1 (square)",
            "Lead 2 (sawtooth)",
            "Lead 3 (calliope)",
            "Lead 4 (chiff)",
            "Lead 5 (charang)",
            "Lead 6 (voice)",
            "Lead 7 (fifths)",
            "Lead 8 (bass + lead)",
            "Pad 1 (new age)",
            "Pad 2 (warm)",
            "Pad 3 (polysynth)",
            "Pad 4 (choir)",
            "Pad 5 (bowed)",
            "Pad 6 (metallic)",
            "Pad 7 (halo)",
            "Pad 8 (sweep)",
            "FX 1 (rain)",
            "FX 2 (soundtrack)",
            "FX 3 (crystal)",
            "FX 4 (atmosphere)",
            "FX 5 (brightness)",
            "FX 6 (goblins)",
            "FX 7 (echoes)",
            "FX 8 (sci-fi)",
            "Sitar",
            "Banjo",
            "Shamisen",
            "Koto",
            "Kalimba",
            "Bag pipe",
            "Fiddle",
            "Shanai",
            "Tinkle Bell",
            "Agogo",
            "Steel Drums",
            "Woodblock",
            "Taiko Drum",
            "Melodic Tom",
            "Synth Drum",
            "Reverse Cymbal",
            "Guitar Fret Noise",
            "Breath Noise",
            "Seashore",
            "Bird Tweet",
            "Telephone Ring",
            "Helicopter",
            "Applause",
            "Gunshot",]
        self.tempo = 100
        self.timer = None
        self.startTime = 0
    def GetInstrument(self, channel):
        return 0xc0 | channel
    def GetPlayNote(self, channel):
        return 0x90 | channel
    def GetControlChange(self, channel):
        return 0xB0 | channel

    def PlayNote(self, key):
        if self.playingNote:
            self.midiOut.Write([[[self.GetPlayNote(0),self.playingNote,0],pypm.Time()]])
            self.playingNote = None
        self.midiOut.Write([[[self.GetPlayNote(0),key,100],pypm.Time()]])
        self.playingNote = key
    def StopNote(self):
        if self.playingNote:
            self.midiOut.Write([[[self.GetPlayNote(0),self.playingNote,0],pypm.Time()]])
            self.playingNote = None

    def PlayNotes(self, notes):
        notesByTime = {}
        for note in notes.itervalues():
            if note[2] not in notesByTime.keys():
                notesByTime[note[2]] = []
            pos = 1.0/float(note[1])*float(note[2])
            len_ = 1.0/float(note[1])*float(note[3]+note[2])
            pos = (60000.0/float(TempoSingleton.GetTempo()/4.0)) * pos
            len_ = (60000.0/float(TempoSingleton.GetTempo()/4.0)) * len_
            notesByTime[note[2]] += [[note[0], pos, len_]]

        def compare(x, y):
            return int(math.ceil(x[0] - y[0]))

        def BuildMsgs(notesByTime_):
            msgs = []
            keys = notesByTime_.keys()
            keys.sort()
            volumes = []
            for key in keys:
                for note in notesByTime_[key]:
                    key, pos, len_ = note
                    msgs += [[pos, key, 0xFF]]
                    msgs += [[len_, key, 0]]
                    counter = 0
                    count = 100
                    time = 0
                    vol = 1
                    volumeDef = [[0,20], [30,40], [50, 60], [70, 80], [90, 100], [110, 127]]
                    volCouter = 0
                    while counter < count:
                        volumes += [[pos+time-1, min(127, int(vol/float(count)*100.0))]]
                        time += ((len_-pos)/float(count)) / 5.0
                        for i in range(len(volumeDef)):
                            if counter < count*i/float(len(volumeDef)):
                                idx = i
                        vol = volumeDef[idx][0] + (volumeDef[idx][1] - volumeDef[idx][0]) / float(100-volCouter)
                        counter += 1
                    counter = 0
                    volCouter += len(volumeDef)
                    if volCouter >= 99:
                        volCouter = 0
                    time = len_-pos
                    vol = 127
                    """
                    while counter < count:
                        volumes += [[pos+time, max(0, int(vol/float(count)*100.0))]]
                        time -= ((len-pos)/float(count)) / 3.0
                        vol -= counter*0.5
                        counter += 1
                    """

            #msgs = sorted(msgs+volumes, cmp=compare)
            msgs = sorted(msgs, cmp=compare)
            return msgs

                    
        self.msgs = BuildMsgs(notesByTime)
        self.startTime = pypm.Time()
        self.timer = threading.Timer(0, self.OnTime)
        self.keepGoing = True
        self.timer.start()

    def OnTime(self):
        for msg in self.msgs:
            while self.startTime+msg[0] > pypm.Time() and self.keepGoing:
                pass
            if self.keepGoing:
                if len(msg) == 3:
                    self.midiOut.Write([[[self.GetPlayNote(0),msg[1],msg[2]],self.startTime+msg[0]]])
                elif len(msg) == 2:
                    self.midiOut.Write([[[self.GetControlChange(0),0x07,msg[1]],self.startTime+msg[0]]])
            else:
                self.midiOut.Write([[[self.GetControlChange(0),0x07,127],self.startTime+msg[0]]])
                break
        self.midiOut.Write([[[self.GetControlChange(0),0x07,127],self.startTime+msg[0]]])

        self.parent.playing = False
    def Stop(self):
        if self.timer:
            self.timer.cancel()
            self.keepGoing = False
            self.timer = None
            self.startTime = 0
        for i in range(120):
            self.midiOut.Write([[[self.GetPlayNote(0),i,0],pypm.Time()+100]])


            

class Subdivisions:
    def __init__(self):
        self.grids = []
        self.snaps = []
        self.defaultSize = (1,1)
    def AddGridSub(self, sub):
        self.grids += [sub]
    def AddSnap(self, *args): #sub분음표가 11개일 때 11개로 나누어 numLeft와 나머지 갯수의 중간에 스냅을 넣는다.
        self.snaps += [args]
    def SetDefaultSize(self, *args):
        self.defaultSize = args
    def GetSnaps(self):
        return self.snaps




#images = ["keyend.png", "keymiddle.png", keystart.png, pianokeys.png, sharp.png
#app = MyApp(redirect=False)
#app.MainLoop()
#pypm.Terminate() 하면 크래쉬 뜨는 경우가 많음. 음 플레이 도중이라던가 이런거라서

#import mdi_rc



class Object(QtCore.QObject):
    def __init__(self, parent):
        QtCore.QObject.__init__(self, parent)
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.ShortcutOverride:
            ev = event
            if ev.key() == QtCore.Qt.Key_W:
                ev.ignore()
                # this doesn't work!
                return True
        return QtCore.QObject.eventFilter(self, obj, event)

class MainWindow(QtGui.QMainWindow):

    def __init__(self):
        global StatusBarSingleton
        super(MainWindow, self).__init__()
        global ParentFrameSingleton, OpenedWindowSingleton
        ParentFrameSingleton = self
        OpenedWindowSingleton = OpenedWindow()

        self.mdiArea = QtGui.QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdiArea)

        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.windowMapper = QtCore.QSignalMapper(self)
        self.windowMapper.mapped[QtGui.QWidget].connect(self.setActiveSubWindow)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.readSettings()

        self.setWindowTitle("PyMusicSequencer")
        self.setUnifiedTitleAndToolBarOnMac(True)




        self.AddSubWindow(PianoRollWindow(self)).resize(600, 500)

        child = PatternManagerFrame(self)
        self.AddSubWindow(child).resize(PatternManagerWidth+30, 400)

        child = Mixer(self)
        self.AddSubWindow(child)

        self.settings = SettingsFile("./MusicTheory/settings.pkl")
        self.projectFile = SettingsFile("./MusicTheory/myProj.pys")
        global SettingsSingleton, CurProjectSingleton
        SettingsSingleton = self.settings
        CurProjectSingleton = self.projectFile
        StatusBarSingleton = self.statusBar()

        self.setContextMenuPolicy(Qt.NoContextMenu)

    def AddSubWindow(self, child):
        mdi = self.mdiArea.addSubWindow(child)
        obj = Object(self)
        mdi.installEventFilter(obj)
        child.show()
        return mdi

    def IsVisible(self, x, y, w, h):
        return True
    """
        sx,sy = self.CalcCurVirtualPos()
        sw,sh = self.GetClientTuple()
        if (sx <= x < sx+sw and sy <= y < sy+sh) or (sx <= x+w < sx+sw and sy <= y+h < sy+sh):
            return True
        else:
            return False
    """

    def keyPressEvent(self, ev):
        if ev.key() == 0x20:
            PatternManagerSingleton.OnPlay()

    def GetClientTuple(self):
        size = (500, 500)#self.GetClientSize()
        return size#size.GetWidth(), size.GetHeight()
    def CalcCurVirtualPos(self):
        """
        size = self.GetClientSize()
        sw = size.GetWidth()
        sh = size.GetHeight()
        """
        sw, sh = 500, 500
        rightMost = self.vW-sw
        bottomMost = self.vH-sh
        sx = (self.scrHPos/100.0)*rightMost
        sy = (self.scrVPos/100.0)*bottomMost
        import math
        return math.ceil(sx), math.ceil(sy)


    def closeEvent(self, event):
        global g_WindowClosed
        g_WindowClosed = True
        self.mdiArea.closeAllSubWindows()
        if self.activeMdiChild():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()

    def newFile(self):
        child = self.createMdiChild()
        #child.newFile()
        child.show()

    def open(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self)
        if fileName:
            existing = self.findMdiChild(fileName)
            if existing:
                self.mdiArea.setActiveSubWindow(existing)
                return

            child = self.createMdiChild()
            if child.loadFile(fileName):
                self.statusBar().showMessage("File loaded", 2000)
                child.show()
            else:
                child.close()

    def save(self):
        if self.activeMdiChild() and self.activeMdiChild().save():
            self.statusBar().showMessage("File saved", 2000)

    def saveAs(self):
        if self.activeMdiChild() and self.activeMdiChild().saveAs():
            self.statusBar().showMessage("File saved", 2000)

    def cut(self):
        if self.activeMdiChild():
            self.activeMdiChild().cut()

    def copy(self):
        if self.activeMdiChild():
            self.activeMdiChild().copy()

    def paste(self):
        if self.activeMdiChild():
            self.activeMdiChild().paste()

    def options(self):
        o = Options()
        o.exec_()

    def about(self):
        QtGui.QMessageBox.about(self, "About PyMusicSequencer",
                "Music Sequencer written in Python<br>"
                "Copyright(C) 2010 Jin Ju Yu<br>"
                "Licensed under the GPL v3 license<br><br>"
                "<a href=http://www.gnu.org/licenses/gpl-3.0.html>http://www.gnu.org/licenses/gpl-3.0.html</a><br>"
                """\
This program is free software: you can redistribute it and/or modify<br>
    it under the terms of the GNU General Public License as published by<br>
    the Free Software Foundation, either version 3 of the License, or<br>
    (at your option) any later version.<br>
<br>
    This program is distributed in the hope that it will be useful,<br>
    but WITHOUT ANY WARRANTY; without even the implied warranty of<br>
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the<br>
    GNU General Public License for more details.<br>

    You should have received a copy of the GNU General Public License<br>
    along with this program.  If not, see http://www.gnu.org/licenses/.""")

    def updateMenus(self):
        hasMdiChild = (self.activeMdiChild() is not None)
        self.saveAct.setEnabled(hasMdiChild)
        self.saveAsAct.setEnabled(hasMdiChild)
        self.pasteAct.setEnabled(hasMdiChild)
        self.closeAct.setEnabled(hasMdiChild)
        self.closeAllAct.setEnabled(hasMdiChild)
        self.tileAct.setEnabled(hasMdiChild)
        self.cascadeAct.setEnabled(hasMdiChild)
        self.nextAct.setEnabled(hasMdiChild)
        self.previousAct.setEnabled(hasMdiChild)
        self.separatorAct.setVisible(hasMdiChild)

        """
        hasSelection = (self.activeMdiChild() is not None and
                        self.activeMdiChild().textCursor().hasSelection())
        self.cutAct.setEnabled(hasSelection)
        self.copyAct.setEnabled(hasSelection)
        """

    def updateWindowMenu(self):
        self.windowMenu.clear()
        self.windowMenu.addAction(self.closeAct)
        self.windowMenu.addAction(self.closeAllAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.nextAct)
        self.windowMenu.addAction(self.previousAct)
        self.windowMenu.addAction(self.separatorAct)

        windows = self.mdiArea.subWindowList()
        self.separatorAct.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            text = "%d %s" % (i + 1, child.userFriendlyCurrentFile())
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child == self.activeMdiChild())
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, child)

    def createMdiChild(self):
        #child = PianoRollWindow(self)
        #self.mdiArea.addSubWindow(child)

        #child.copyAvailable.connect(self.cutAct.setEnabled)
        #child.copyAvailable.connect(self.copyAct.setEnabled)

        return child

    def createActions(self):
        self.newAct = QtGui.QAction(QtGui.QIcon('./MusicTheory/images/new.png'), "&New",
                self, shortcut=QtGui.QKeySequence.New,
                statusTip="Create a new file", triggered=self.newFile)

        self.openAct = QtGui.QAction(QtGui.QIcon('./MusicTheory/images/open.png'),
                "&Open...", self, shortcut=QtGui.QKeySequence.Open,
                statusTip="Open an existing file", triggered=self.open)

        self.saveAct = QtGui.QAction(QtGui.QIcon('./MusicTheory/images/save.png'),
                "&Save", self, shortcut=QtGui.QKeySequence.Save,
                statusTip="Save the document to disk", triggered=self.save)

        self.saveAsAct = QtGui.QAction("Save &As...", self,
                shortcut=QtGui.QKeySequence.SaveAs,
                statusTip="Save the document under a new name",
                triggered=self.saveAs)

        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
                statusTip="Exit the application",
                triggered=QtGui.qApp.closeAllWindows)

        self.cutAct = QtGui.QAction(QtGui.QIcon('./MusicTheory/images/cut.png'), "Cu&t",
                self, shortcut=QtGui.QKeySequence.Cut,
                statusTip="Cut the current selection's contents to the clipboard",
                triggered=self.cut)

        self.copyAct = QtGui.QAction(QtGui.QIcon('./MusicTheory/images/copy.png'),
                "&Copy", self, shortcut=QtGui.QKeySequence.Copy,
                statusTip="Copy the current selection's contents to the clipboard",
                triggered=self.copy)

        self.pasteAct = QtGui.QAction(QtGui.QIcon('./MusicTheory/images/paste.png'),
                "&Paste", self, shortcut=QtGui.QKeySequence.Paste,
                statusTip="Paste the clipboard's contents into the current selection",
                triggered=self.paste)
        self.optionsAct = QtGui.QAction("&Options", self, statusTip="Paste the clipboard's contents into the current selection",
                triggered=self.options)

        self.closeAct = QtGui.QAction("Cl&ose", self, shortcut="Ctrl+F4",
                statusTip="Close the active window",
                triggered=self.mdiArea.closeActiveSubWindow)

        self.closeAllAct = QtGui.QAction("Close &All", self,
                statusTip="Close all the windows",
                triggered=self.mdiArea.closeAllSubWindows)

        self.tileAct = QtGui.QAction("&Tile", self,
                statusTip="Tile the windows",
                triggered=self.mdiArea.tileSubWindows)

        self.cascadeAct = QtGui.QAction("&Cascade", self,
                statusTip="Cascade the windows",
                triggered=self.mdiArea.cascadeSubWindows)

        self.nextAct = QtGui.QAction("Ne&xt", self,
                shortcut=QtGui.QKeySequence.NextChild,
                statusTip="Move the focus to the next window",
                triggered=self.mdiArea.activateNextSubWindow)

        self.previousAct = QtGui.QAction("Pre&vious", self,
                shortcut=QtGui.QKeySequence.PreviousChild,
                statusTip="Move the focus to the previous window",
                triggered=self.mdiArea.activatePreviousSubWindow)

        self.separatorAct = QtGui.QAction(self)
        self.separatorAct.setSeparator(True)

        self.aboutAct = QtGui.QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self.about)

        self.aboutQtAct = QtGui.QAction("About &Qt", self,
                statusTip="Show the Qt library's About box",
                triggered=QtGui.qApp.aboutQt)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAsAct)
        self.fileMenu.addSeparator()
        action = self.fileMenu.addAction("Switch layout direction")
        action.triggered.connect(self.switchLayoutDirection)
        self.fileMenu.addAction(self.exitAct)

        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.optionsAct)

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("Meter")
        #self.fileToolBar.addAction(self.newAct)
        #self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.setIconSize(QtCore.QSize(10, 10))
        self.fileToolBar.setFloatable(False)
        self.fileToolBar.setMovable(False)
        self.tempo = Tempo_(None)
        self.display = Display(None)
        self.pattern = Pattern(None)
        global TempoSingleton
        TempoSingleton = self.tempo
        self.fileToolBar.addWidget(self.display)
        self.fileToolBar.addWidget(self.tempo)
        self.fileToolBar.addWidget(self.pattern)

        self.addToolBarBreak()
        self.editToolBar = self.addToolBar("File")
        self.editToolBar.setFloatable(False)
        self.editToolBar.setMovable(False)
        self.editToolBar.addAction(self.saveAct)
        #self.editToolBar.addAction(self.cutAct)
        #self.editToolBar.addAction(self.copyAct)
        #self.editToolBar.addAction(self.pasteAct)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def readSettings(self):
        settings = QtCore.QSettings('PyMusicSequencer', 'PyMusicSequencer')
        pos = settings.value('pos', QtCore.QPoint(200, 200))
        size = settings.value('size', QtCore.QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QtCore.QSettings('PyMusicSequencer', 'PyMusicSequencer')
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())

    def activeMdiChild(self):
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def findMdiChild(self, fileName):
        canonicalFilePath = QtCore.QFileInfo(fileName).canonicalFilePath()

        for window in self.mdiArea.subWindowList():
            if window.widget().currentFile() == canonicalFilePath:
                return window
        return None

    def switchLayoutDirection(self):
        if self.layoutDirection() == QtCore.Qt.LeftToRight:
            QtGui.qApp.setLayoutDirection(QtCore.Qt.RightToLeft)
        else:
            QtGui.qApp.setLayoutDirection(QtCore.Qt.LeftToRight)

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)



#----------------------------------------------------------------------
class ScrollBar(QtGui.QWidget):
    def __init__(self, parent, x, y, size, horizontal=True):
        self.parent = parent
        self.x = x
        self.y = y
        self.size_ = size
        self.scrollbarPos = 0.0 # percentage, 0~100
        self.horizontal = horizontal
        self.dragging = False
        self.dragStartPos = (0, 0)
        self.binds = []
        self.scrollRate = 20 # in pixel

        self.lastMouse = (-1, -1)

        super(ScrollBar, self).__init__(parent, pos=QtCore.QPoint(self.x, self.y))

        self.pen = QtGui.QPen()
        self.brush = QtGui.QBrush()
        self.pixmap = QtGui.QPixmap()
        self.antialiased = False

        self.setBackgroundRole(QtGui.QPalette.Base)
        self.setAutoFillBackground(True)

    def minimumSizeHint(self):
        if self.horizontal:
            return QtCore.QSize(self.size_, 20)
        else:
            return QtCore.QSize(20, self.size_)

    def sizeHint(self):
        if self.horizontal:
            return QtCore.QSize(self.size_, 20)
        else:
            return QtCore.QSize(20, self.size_)

    def setPen(self, pen):
        self.pen = pen
        self.update()

    def setBrush(self, brush):
        self.brush = brush
        self.update()

    def setAntialiased(self, antialiased):
        self.antialiased = antialiased
        self.update()

    def mouseMoveEvent(self, ev):
        if ev:
            x, y = ev.pos().x(), ev.pos().y()
            self.lastMouse = (x, y)
        else:
            x, y = self.lastMouse
        if self.IsMouseInButton(x, y, True):
            if self.pushStart != -1 and (time.clock() - self.pushStart) > 0.25 and (time.clock()-self.pushScrolledLast) > 0.1:
                self.IncreaseScroll()
        elif self.IsMouseInButton(x, y, False):
            if self.pushStart != -1 and (time.clock() - self.pushStart) > 0.25 and (time.clock()-self.pushScrolledLast) > 0.1:
                self.DecreaseScroll()

        if self.dragging:
            if self.horizontal:
                self.SetScrollBarPixel(x-24-self.dragOffset)
            else:
                self.SetScrollBarPixel(y-24-self.dragOffset)

    def mouseReleaseEvent(self, ev):
        if ev.button() == LMB:
            self.lastMouse = (-1, -1)
            self.dragging = False
            self.pushStart = -1
    def mousePressEvent(self, ev):
        if ev.button() == LMB:
            x, y = ev.pos().x(), ev.pos().y()
            self.lastMouse = (x, y)
            if self.IsMouseInBar(x, y):
                self.dragging = True
                if self.horizontal:
                    self.dragOffset = (x-24)-self.GetScrollBarPixelPos(self.scrollbarPos, self.size_)
                else:
                    self.dragOffset = (y-24)-self.GetScrollBarPixelPos(self.scrollbarPos, self.size_)
            elif self.IsMouseInMe(x, y):
                self.dragging = True
                self.dragOffset = 15
                if self.horizontal:
                    self.SetScrollBarPixel(x-(24)-15)
                else:
                    self.SetScrollBarPixel(y-(24)-15)

            if self.IsMouseInButton(x, y, True):
                self.dragging = False
                self.pushStart = time.clock()
                self.pushScrolledLast = time.clock()
                self.pushedIncrease = True
                self.IncreaseScroll()
            elif self.IsMouseInButton(x, y, False):
                self.dragging = False
                self.pushStart = time.clock()
                self.pushScrolledLast = time.clock()
                self.pushedIncrease = False
                self.DecreaseScroll()
            else:
                self.pushStart = -1

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        if self.antialiased:
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

        color = (71, 103, 10)
        color2 = (40, 55, 10)
        painter.save()
        brush = QtGui.QBrush(QtGui.QColor(*color))
        pen = QtGui.QPen(QtGui.QColor(*color2))
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.translate(0, 0)

        if self.horizontal:
            rect = QtCore.QRect(0, 0, self.size_, 20)
            painter.drawRect(rect)
            bmp = LoadBitmap('scrollleft.png')
            painter.drawPixmap(0,0, bmp)
            bmp = LoadBitmap('scrollbar.png')
            painter.drawPixmap(0+24+self.GetScrollBarPixelPos(0, self.size_),0, bmp)
            bmp = LoadBitmap('scrollright.png')
            painter.drawPixmap(0+self.size_-25,0, bmp)
        else:
            rect = QtCore.QRect(0, 0, 0+20, 0+self.size_)
            painter.drawRect(rect)
            bmp = LoadBitmap('scrollup.png')
            painter.drawPixmap(0,0, bmp)
            bmp = LoadBitmap('scrollbarV.png')
            painter.drawPixmap(0,0+24+self.GetScrollBarPixelPos(0, self.size_), bmp)
            bmp = LoadBitmap('scrolldown.png')
            painter.drawPixmap(0,0+self.size_-25, bmp)

        painter.restore()

        """
        if self.transformed:
            painter.translate(50, 50)
            painter.rotate(60.0)
            painter.scale(0.6, 0.9)
            painter.translate(-50, -50)
        """
        """
                elif self.shape == RenderArea.Points:
                    painter.drawPoints(RenderArea.points)
                elif self.shape == RenderArea.Polyline:
                    painter.drawPolyline(RenderArea.points)
                elif self.shape == RenderArea.Polygon:
                    painter.drawPolygon(RenderArea.points)
                elif self.shape == RenderArea.Rect:
                    painter.drawRect(rect)
                elif self.shape == RenderArea.RoundedRect:
                    painter.drawRoundedRect(rect, 25, 25,
                            QtCore.Qt.RelativeSize)
                elif self.shape == RenderArea.Ellipse:
                    painter.drawEllipse(rect)
                elif self.shape == RenderArea.Arc:
                    painter.drawArc(rect, startAngle, arcLength)
                elif self.shape == RenderArea.Chord:
                    painter.drawChord(rect, startAngle, arcLength)
                elif self.shape == RenderArea.Pie:
                    painter.drawPie(rect, startAngle, arcLength)
                elif self.shape == RenderArea.Path:
                    painter.drawPath(path)
                elif self.shape == RenderArea.Text:
                    painter.drawText(rect, QtCore.Qt.AlignCenter,
                            "Qt by\nQt Software")
                elif self.shape == RenderArea.Pixmap:
        """

        """
        painter.setPen(self.palette().dark().color())
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(QtCore.QRect(0, 0, self.width() - 1,
                self.height() - 1))
        """
    def Bind(self, func):
        self.binds += [func]
    def Resize(self, size):
        self.size_ = size
    def SetPos(self, x, y):
        self.x = x
        self.y = y

    def IsMouseInBar(self, x, y):
        if self.horizontal:
            width = 30
            height = 20
            pos = self.GetScrollBarPixelPos(0, self.size_)
            if 24+pos <= x < 24+pos+width and 0 <= y < height:
                return True
        else:
            width = 20
            height = 30
            pos = self.GetScrollBarPixelPos(0, self.size_)
            if 24+pos <= y < 24+pos+height and 0 <= x < width:
                return True
        return False
    def IsMouseInMe(self, x, y):
        if self.horizontal:
            if 24 <= x < self.size_-24 and 0 <= y <= 20:
                return True
        else:
            if 24 <= y < self.size_-24 and 0 <= x <= 20:
                return True
        return False

    def IsMouseInButton(self, x, y, increase):
        if self.horizontal:
            if increase:
                if 0+self.size_-24 <= x < 0+self.size_ and 0 <= y <= 0+20:
                    return True
            else:
                if 0 <= x < 0+24 and 0 <= y <= 0+20:
                    return True
        else:
            if increase:
                if 0+self.size_-24 <= y < 0+self.size_ and 0 <= x <= 0+20:
                    return True
            else:
                if 0 <= y < 0+24 and 0 <= x <= 0+20:
                    return True



    def IncreaseScroll(self):
        self.pushScrolledLast = time.clock()
        if self.horizontal:
            self.SetScrollBarPos(self.scrollbarPos + (float(self.scrollRate) / float(self.parent.vW))*100.0)
        else:
            self.SetScrollBarPos(self.scrollbarPos + (float(self.scrollRate) / float(self.parent.vH))*100.0)
    def DecreaseScroll(self):
        self.pushScrolledLast = time.clock()
        if self.horizontal:
            self.SetScrollBarPos(self.scrollbarPos - (float(self.scrollRate) / float(self.parent.vW))*100.0)
        else:
            self.SetScrollBarPos(self.scrollbarPos - (float(self.scrollRate) / float(self.parent.vH))*100.0)

    def GetScrollBarPixelPos(self, pos, size, scpos=None):
        if not scpos:
            scpos = self.scrollbarPos
        leftMost = 24
        rightMost = size-25-29
        length = rightMost-leftMost
        scpos = max(scpos,0.0)
        scpos = min(scpos,100.0)
        return int((float(scpos) / 100.0)*length)
    def GetBarPercentage(self, pos):
        return (float(pos) / float(self.size_-24-25-29))*100.0

    def SetScrollBarPixel(self, pos):
        self.SetScrollBarPos(self.GetBarPercentage(pos))
    def SetScrollBarPos(self, pos):
        oldPos = self.scrollbarPos
        self.scrollbarPos = pos
        self.scrollbarPos = max(self.scrollbarPos,0.0)
        self.scrollbarPos = min(self.scrollbarPos,100.0)

        if self.horizontal:
            scpos = self.GetScrollBarPixelPos(0, self.size_, oldPos)
            #scpos = min(oldPos, pos)
            size = 30+abs(oldPos-pos)
            self.repaint()
        else:
            scpos = self.GetScrollBarPixelPos(0, self.size_, oldPos)
            #scpos = min(oldPos, pos)
            size = 30+abs(oldPos-pos)
            self.repaint()
        for func in self.binds:
            func(self.scrollbarPos)

class PianoKeys:#(QtGui.QWidget):
    # 음..............................................
    # 그대로 변환하자.
    # yoffset은 없애지만 버추얼 포지션 같은 건 그냥 놔두고?
    # 음...... yoffset도 필요하다? 이거의 위치 자체를 옮길 수는 없나?
    # 부모가 스크롤 될 때 이것도 스크롤 되어야 한다는 사실만 중요함.
    # 정확한 위치를 어떻게 잡나? yoffset없이 이 위젯 자체의 위치로 offset을 준다. 위젯 위치는 또 어케 잡나? ;;
    # 전에는 이게 위젯이 아니라, 부모가 그려질 때 그냥 그려지는 것이었다. 마우스 이벤트도 부모에서 잡았고.....
    # 그렇게 구현한다? ok 그렇게 구현한다.
    # 라지만 그럴려면 음.... 맞다 그렇게 한다.
    # 스크롤링도ㅓ 그냥 내 구현을 쓴다?
    def __init__(self, parent, yoffset):
        self.parent = parent
        self.keyboardWidth = 71
        self.keyboardHeight = 144
        self.yoffset = yoffset
        self.kh = 12
        self.pushedKeys = {}
        self.pushedByLMB = -1
        self.prevPushedByLMB = -1
        self.dragging = False

        """
        super(PianoKeys, self).__init__(parent)
        self.setBackgroundRole(QtGui.QPalette.Base)
        self.setAutoFillBackground(True)
        """

    def minimumSizeHint(self):
        return QtCore.QSize(self.keyboardWidth, self.keyboardHeight)

    def sizeHint(self):
        return QtCore.QSize(self.keyboardWidth, self.keyboardHeight)

    """
    def j(self, ev):
        if ev:
            x, y = ev.pos().x(), ev.pos().y()
            self.lastMouse = (x, y)
    """

    def mousePressEvent(self, ev):
        x, y = ev.pos().x(), ev.pos().y()
        self.OnClick(x, y)
    def mouseMoveEvent(self, ev):
        x, y = ev.pos().x(), ev.pos().y()
        if self.dragging:
            self.OnClick(x, y)
    def mouseReleaseEvent(self, ev):
        x, y = ev.pos().x(), ev.pos().y()
        self.dragging = False
        self.prevPushedByLMB = self.pushedByLMB
        self.pushedByLMB = -1
        sx,sy = self.parent.CalcCurVirtualPos()
        sw,sh = self.parent.GetClientTuple()
        self.parent.repaint(QtCore.QRect(0, -sy, self.keyboardWidth, sh))
        #self.Draw(self.parent.GetDC())

    def GetClickedKeyAndPos(self, x, y):
        if y > self.yoffset and x < self.parent.GetClientTuple()[0]-20:
            sx,sy = self.parent.CalcCurVirtualPos()
            realY = sy+y-self.yoffset
            keyPos = realY-(realY%self.kh)
            key = keyPos/self.kh
            return key, keyPos
        else:
            return -1, 0
    def GetKeyPos(self, key):
        return key*self.kh

    def OnClick(self, x, y):
        key, keyPos = self.GetClickedKeyAndPos(x, y)
        self.prevPushedByLMB = self.pushedByLMB
        self.pushedByLMB = key

        sx,sy = self.parent.CalcCurVirtualPos()
        sw,sh = self.parent.GetClientTuple()
        if key != -1:
            self.dragging = True
            if self.parent.IsVisible(0, self.yoffset+self.GetKeyPos(self.pushedByLMB)-sy, sw, self.kh):
                self.parent.repaint()
        #self.Draw(self.parent.GetDC())



    def Draw(self, painter):
        keyHighlights= [
                (2, 105, "keystart.png"),
                (1, 97, "sharp.png"),
                (2, 88, "keymiddle.png"),
                (1, 80, "sharp.png"),
                (1, 70, "keyend.png"),
                (2, 53, "keystart.png"),
                (1, 46, "sharp.png"),
                (2, 36, "keymiddle.png"),
                (1, 29, "sharp.png"),
                (2, 18, "keymiddle.png"),
                (1, 12, "sharp.png"),
                (1, 0, "keyend.png"),
                ]
        bmp = LoadBitmap('pianokeys.png')


        sx,sy = self.parent.CalcCurVirtualPos()
        sw,sh = self.parent.GetClientTuple()
        #painter = QtGui.QPainter(self)

        """
        if self.prevPushedByLMB != -1 and self.pushedByLMB == -1:
            if self.parent.IsVisible(0, self.GetKeyPos(self.prevPushedByLMB)+self.yoffset, sw-20, self.kh):
                color = QtGui.QColor(42,59,33, 128)
                pen = QtGui.QPen(color)
                brush = QtGui.QBrush(color)
                painter.setPen(pen)
                painter.setBrush(brush)
                if self.GetKeyPos(self.prevPushedByLMB)-sy+self.yoffset >= 20:
                    rect = QtCore.QRect(0, self.GetKeyPos(self.prevPushedByLMB)-sy+self.yoffset, self.keyboardWidth, self.kh)
                    painter.drawRect(rect)
            self.prevPushedByLMB = -1
        """


        for i in range(10):
            if self.parent.IsVisible(sx, i*self.keyboardHeight+self.yoffset, self.keyboardWidth, self.keyboardHeight):
                #painter.DrawBitmap(bmp, 0,i*self.keyboardHeight-sy+self.yoffset, True)
               # painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0)))
                pen = QtGui.QPen(QtGui.QColor(*(0, 0, 0)))
                painter.drawPixmap(0,i*self.keyboardHeight-sy+self.yoffset, bmp)
                labels = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
                j = 0
                for label in labels:
                    rect = QtCore.QRect(45, (i+1)*self.keyboardHeight-13-sy+self.yoffset - j*self.kh, 30, 15)
                    painter.drawText(rect, QtCore.Qt.AlignLeft, label+`9-i-2`)
                    j += 1

        if self.pushedByLMB != -1:
            if self.parent.IsVisible(0, self.GetKeyPos(self.pushedByLMB)+self.yoffset, self.keyboardWidth, self.kh):
                color = QtGui.QColor(42,59,33, 190)
                pen = QtGui.QPen(color)
                brush = QtGui.QBrush(color)
                painter.setPen(pen)
                painter.setBrush(brush)
                if self.GetKeyPos(self.pushedByLMB)-sy+self.yoffset >= 20:
                    rect = QtCore.QRect(0, self.GetKeyPos(self.pushedByLMB)-sy+self.yoffset, self.keyboardWidth, self.kh)
                    painter.drawRect(rect)

        color = QtGui.QColor(255, 255, 255)
        pen = QtGui.QPen(color)
        brush = QtGui.QBrush(color)
        painter.setPen(pen)
        painter.setBrush(brush)

        rect = QtCore.QRect(0, 0, self.keyboardWidth, 20)
        painter.drawRect(rect)



class Grid(object):
    def __init__(self, parent, x, y, woffset=0, hoffset=0):
        self.x = x
        self.y = y
        self.parent = parent
        self.bufW = 0
        self.bufH = 0
        self._Buffer = None
        self.kh = self.parent.pianoKeys.kh
        self.kw = 12
        self.redraw = False

    def GetLRTB(self):
        width = self.parent.GetClientTuple()[0]-self.x-20
        height = self.parent.GetClientTuple()[1]-self.y
        return self.x, self.x+width, self.y, self.y+height
    def UpdateRect(self, x, y, w, h):
        self.parent.repaint(x, y, w, h)
        """
        painter = self.parent.GetDC()
        width = self.parent.GetClientTuple()[0]-self.x-20
        height = self.parent.GetClientTuple()[1]-self.y
        grid1 = self.parent.sub.grids[-1] # 16
        grid2 = self.parent.sub.grids[-2] # 4

        numOfLines = (height) / self.kh
        numHorLines = (width) / self.kw
        vX, vY = self.parent.CalcCurVirtualPos()
        xOffset = vX%self.kw
        yOffset = vY%self.kh
        firstLineOnScreenNumber = (vY-(vY%self.kh))/self.kh
        firstHor = (vX-(vX%self.kw))/self.kw

        fVerOffst = firstLineOnScreenNumber % 12
        fHorOffst = firstHor % grid1
        memory = wx.MemoryDC()
        memory.SelectObject(self._Buffer)
        painter.Blit(self.x+x, self.y+y, w, h, memory, xOffset+(fHorOffst*self.kw)+x, yOffset+(fVerOffst*self.kh)+y)
        """

    def Draw(self, painter):
        # 클라이언트 영역보다 가로 1pianoKeys.0*grid1 세로 1pianoKeys.0*12만큼 더 크게 그려둔 후 그 버퍼를 클라이언트 DC에다가 오프셋으로 블리팅만 한다.
        width = self.parent.GetClientTuple()[0]-self.x-20
        height = self.parent.GetClientTuple()[1]-self.y
        grid1 = self.parent.sub.grids[-1] # 16
        grid2 = self.parent.sub.grids[-2] # 4
        if not self._Buffer or (self.bufW != width+self.kw*grid1) or (self.bufH != height+self.kh*12) or self.redraw:
            self.redraw = False
            self.bufW = width+self.kw*grid1
            self.bufH = height+self.kh*12
            self._Buffer = QtGui.QPixmap(self.bufW, self.bufH)
            numOfLines = (self.bufH) / self.kh
            numHorLines = (self.bufW) / self.kw
            color = (42,59,33)
            color2 = (52,69,43)
            color3 = (39,41,15)
            colorBG = (77, 75, 51)
            self._Buffer.fill(QtGui.QColor(*colorBG))
            painter2 = QtGui.QPainter()
            painter2.begin(self._Buffer)
            
            painter2.setPen(QtGui.QPen(QtGui.QColor(*colorBG)))
            painter2.setBrush(QtGui.QBrush(QtGui.QColor(*colorBG)))

            for i in range(numHorLines):
                x = i*self.kw
                painter2.setPen(QtGui.QPen(QtGui.QColor(*color2)))
                painter2.setBrush(QtGui.QBrush(QtGui.QColor(*color2)))
                painter2.drawLine(x, 0, x, self.bufH)

            for i in range(numOfLines):
                y = i*self.kh
                if not(i%12):
                    painter2.setPen(QtGui.QPen(QtGui.QColor(*color)))
                    painter2.setBrush(QtGui.QBrush(QtGui.QColor(*color)))
                else:
                    painter2.setPen(QtGui.QPen(QtGui.QColor(*color2)))
                    painter2.setBrush(QtGui.QBrush(QtGui.QColor(*color2)))
                painter2.drawLine(0, y, self.bufW, y)

            for i in range(numHorLines):
                x = i*self.kw
                if not(i%grid2):
                    painter2.setPen(QtGui.QPen(QtGui.QColor(*color)))
                    painter2.setBrush(QtGui.QBrush(QtGui.QColor(*color)))
                    painter2.drawLine(x, 0, x, self.bufH)

            for i in range(0, numHorLines):
                x = i*self.kw
                if not(i%grid1):
                    painter2.setPen(QtGui.QPen(QtGui.QColor(*color3)))
                    painter2.setBrush(QtGui.QBrush(QtGui.QColor(*color3)))
                    painter2.drawLine(x, 0, x, self.bufH)
            painter2.end()

        numOfLines = (height) / self.kh
        numHorLines = (width) / self.kw
        vX, vY = self.parent.CalcCurVirtualPos()
        xOffset = vX%self.kw
        yOffset = vY%self.kh
        firstLineOnScreenNumber = (vY-(vY%self.kh))/self.kh
        firstHor = (vX-(vX%self.kw))/self.kw

        fVerOffst = firstLineOnScreenNumber % 12
        fHorOffst = firstHor % grid1

        painter.drawPixmap(self.x,self.y, width, height, self._Buffer, xOffset+(fHorOffst*self.kw), yOffset+(fVerOffst*self.kh), width, height)

class PianoRollWindow(QtGui.QWidget):
    def event(self, ev):
        #TODO 여기서 플레잉바를 그리는 거를 한다.
        # 뭐.... 그냥 간단히 다른 쓰레드에서 여기다 뭘 쓰고
        # 그 쓴 값을 다른 버퍼에 저장하고
        # 그 다른 버퍼에 있는 값이 "이전값"과 다르다면 다른버퍼에있는 걸 이전값에 넣고 repaint한다.
        # 그릴 때는 "이전값"을 읽어서 하게 된다.

        return QtGui.QWidget.event(self, ev)
    def __init__(self, parent):
        # playing bar stuff
        self.barPos = 0
        self.prevBarPos = 0


        self.instrument = None
        super(PianoRollWindow, self).__init__(parent, size=QtCore.QSize(400, 400))
        self.setBackgroundRole(QtGui.QPalette.Base)
        self.setAutoFillBackground(True)
        self.setWindowTitle("Piano Roll")

        self.scrollH = ScrollBar(self, 0, 0, 400)
        self.scrollV = ScrollBar(self, 400, 0, 400, False)
        self.scrHPos = 0
        self.scrVPos = 0
        self.scrollH.Bind(self.OnHScroll)
        self.scrollV.Bind(self.OnVScroll)
        self.scrollV.SetScrollBarPos(50.0)

        self.sub = Subdivisions()
        self.sub.AddGridSub(4)
        self.sub.AddGridSub(16)
        self.sub.AddSnap(16, 0)
        self.sub.SetDefaultSize(16, 1)

        self.pianoKeys = PianoKeys(self, 20)
        self.grid = Grid(self, self.pianoKeys.keyboardWidth, 20)
        self.minW = self.size().width()
        self.vW = 300+self.minW
        self.vH = self.pianoKeys.keyboardHeight*10+20
        self.notes = Notes(self)
        #self.vst = VSTWindow(r"D:\Program Files\VstPlugins\Drumatic 3.dll", self)
        #self.vstFX = VSTWindow(r"D:\Program Files\VstPlugins\JCM900(Guitar amplifier).dll", self)
        global VSTThreadSingleton, PianoRollSingleton
        VSTThreadSingleton = self.vstThd = VSTSoundWorker(self)
        self.vstThd.start()
        PianoRollSingleton = self
        self.enabled = False

        """
        #self.SetScrollRate(20,20)

        self.instrument = None
        self.patternNum = None
        """
        """
        기본적으로 모든 음표는 온음표를 기준으로 2개로 나뉜다.
        만약 AddSub로 32분음표가 11개로 나뉜다고 정하면 11개가 어떤 그룹을 짓는지 정해야 한다.
        Sub로 몇개로 나뉘는지 정하고
        AddGrid로 어떤 그룹을 짓는지 대충 정한다.

        AddSub에서 기본적으로 32, 11을 해주는 것은 64, 11을 하면 어떻게 되나?

        아. 32분음표의 분할과 64분음표의 분할은 기본적으로 다르다. 32분음표에서 11개로 나누었다고 해서 64분음표를 5개씩 나누지 말라는 법은 없다.
        32개를 11개로 나누고, 동시에 폴리리듬으로 32분음표를 둘로 나누어 64분음표를 5개씩 해서 나누면 된다.
        그러므로 그리드는 그대로 놔두고, Snap부분만 고친다.

        self.sub.AddSub(32, 11)
        self.sub.AddGridSub(4)
        self.sub.AddGridSub(16)
        self.sub.AddSnap(16) # 16분음표에 스냅
        self.sub.AddSnap(32) # 32분음표의 시작부분에 스냅, FL Studio는 16분음표에만 스냅함.
        self.sub.AddSnap(32, 8) # 32분음표의 끝나는 부분에 스냅
        """
        """-
        # 우왕 빨리 코드 제네럴화 해서 여러가지로 해보자. ㅇㅇ ㅠㅠ
        # 음 스냅을 새로 정해서 메뉴에서 스냅을 바꿀 수 있게 한다.
        # 선택->이동이랑 뭐 그런거 얼른 만든다.
        # 흠 일단 기본적인 리듬감의 비밀은 여러 라인의 복합적인 진행이다.
        # DAW로 해도 충분히 그런 리듬감은 산다.
        # 아... 세분화가 중요한 게 아니라 온음표 4개를 
        #
        # 음 지금 스크롤바가 뭐랄까 위젯인데 그건 그냥 그대로 두고 쓰자. 오프셋을 다 없애버렸으니...
        # 이거를 부모로 두고 그리면 그게 될까?
        self.sub.SetDefaultSize(16, 1)
        size = parent.GetClientSize()
        self.scrollH = ScrollBar(self, self.pianoKeys.keyboardWidth, 0, size.GetWidth()-self.pianoKeys.keyboardWidth)
        self.scrollV = ScrollBar(self, size.GetWidth()-20, 20, size.GetHeight()-20, False)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnButtonEvent)
        self.Bind(wx.EVT_LEFT_UP,   self.OnButtonEvent)
        self.Bind(wx.EVT_MOTION,    self.OnButtonEvent)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnButtonEvent)
        self.Bind(wx.EVT_RIGHT_UP, self.OnButtonEvent)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.SetDoubleBuffered(True)
        class Temp:
            def GetSize(self2):
                return parent.GetClientSize()
        self.OnSize(Temp())
        self.scrollV.SetScrollBarPos(50.0)
        self.ldragging = False
        self.rdragging = False
        self.playing = False


        self.vst = VSTWindow(r"D:\Program Files\VstPlugins\LoganA.dll", self)
        #self.vst = VSTWindow(r"D:\Program Files\VstPlugins\Synth1 VST.dll", self)
        #self.vst = VSTWindow(r"D:\Program Files\VstPlugins\LoganA.dll", self)
        # 뭔가 프로그램을 강제종료시킬 수 있는 게 필요한데...
        VSTThreadSingleton = self.vstThd = VSTSoundWorker(self.vst.vstEff, self.vst)
        self.vstThd.start()
        self.vstFX = VSTWindow(r"D:\Program Files\VstPlugins\JCM900(Guitar amplifier).dll", self)
        # 음 출력하는 사운드를 vstFX로 리플레이싱해서 출력하면 되는데...
        # GUI가 없다..;; ㄷㄷㄷ
        # GUI가 없는 놈들은 파라메터를 보여줘야 한다. 파라메터 뷰를 만든다.
        
        #print DumpVSTData(r"D:\Program Files\VstPlugins\Synth1 VST.dll")
        #self.vst = VSTWindow(r"D:\Program Files\VstPlugins\dblue_Glitch_v1_3.dll", self)
        #self.vst = VSTWindow(r"D:\Program Files\VstPlugins\LoganA.dll", self)
        """

    def GetCurInstrument(self):
        return self.instrument
    def SetWidth(self):
        rightMost = None
        curX = self.CalcCurVirtualPos()[0]
        for note in self.notes.notes.itervalues():
            key, dividedby, pos, length = note
            if rightMost:
                if rightMost[2]+rightMost[3] < pos+length:
                    rightMost = note
            else:
                rightMost = note

        if rightMost:
            x,y,w,h = self.notes.GetPixelPos(*note)
            self.vW = x+w+300
            if self.vW < self.minW:
                self.vW = self.minW

            size = self.size()
            sw = size.width()
            sh = size.height()
            rightMost = self.vW-sw
            if rightMost == 0:
                rightMost = 1
            scrHPos = curX*100.0/rightMost
            self.scrollH.SetScrollBarPos(scrHPos)
            self.repaint()

    def closeEvent(self, ev):
        if not g_WindowClosed:
            ev.ignore()

    def minimumSizeHint(self):
        return QtCore.QSize(150, 200)

    def sizeHint(self):
        return self.size()

    def resizeEvent(self, ev):
        size = ev.size()
        self.minW = size.width()
        self.scrollH.move(self.pianoKeys.keyboardWidth, 0)
        self.scrollH.Resize(size.width()-self.pianoKeys.keyboardWidth)
        self.scrollH.resize(size.width()-self.pianoKeys.keyboardWidth, 20)
        self.scrollV.move(size.width()-20, 20)
        self.scrollV.Resize(size.height()-20)
        self.scrollV.resize(20, size.height()-20)

    def paintEvent(self, ev):
        painter = QtGui.QPainter(self)
        if self.enabled:
            self.grid.Draw(painter)
            self.notes.Draw(painter)
            self.pianoKeys.Draw(painter)
        else:
            col = QtGui.QColor(0, 0, 0)#"#a5b84c"
            painter.setPen(QtGui.QPen(col))
            painter.setBrush(QtGui.QBrush(col))
            painter.drawText(0, 30, "Disabled. Add Instrument and push Piano Roll Button")


    def SetInstrumentPattern(self, instrument, patternNum):
        self.enabled = True
        self.instrument = instrument
        self.patternNum = patternNum
        self.notes.SetNotes(instrument.notes)
        self.repaint()

    def Disable(self):
        self.enabled = False
        self.instrument = None
        self.patternNum = None
        self.notes.notes = []
        self.repaint()

    def OnHScroll(self, pos):
        self.scrHPos = pos
        size = self.size()
        self.repaint(self.pianoKeys.keyboardWidth, 0, size.width()-self.pianoKeys.keyboardWidth, size.height())

    def OnVScroll(self, pos):
        self.scrVPos = pos
        size = self.size()
        self.repaint(0, 20, size.width(), size.height()-20)

    def OnPaint(self, event):
        # All that is needed here is to draw the buffer to screen
        #self.UpdateDrawing()
        #painter = wx.BufferedPaintDC(self, self._Buffer, wx.BUFFER_VIRTUAL_AREA)
        painter = wx.PaintDC(self)
        #painter = wx.BufferedDC(wx.ClientDC(self), self._Buffer)
        self.Draw(painter)

    def UpdateDrawing(self):
        painter = wx.PaintDC(self)
        #painter = wx.BufferedDC(wx.ClientDC(self), self._Buffer)
        self.Draw(painter)

    def GetDC(self):
        painter = wx.PaintDC(self)
        return painter#wx.BufferedDC(wx.ClientDC(self), self._Buffer)


    def SetXY(self, event):
        self.x, self.y = self.ConvertEventCoords(event)

    def ConvertEventCoords(self, event):
        #newpos = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
        newpos = event.GetX(), event.GetY()
        return newpos

    def OnButtonEvent(self, event):
        if event.LeftDown():
            self.SetFocus()
            #self.SetXY(event)
            #self.curLine = []
            self.CaptureMouse()
            #self.drawing = True
            self.scrollH.OnLDown(event.GetPosition())
            self.scrollV.OnLDown(event.GetPosition())
            self.pianoKeys.OnLDown(event.GetPosition())
            self.notes.OnLDown(event.GetPosition())
            self.ldragging = True
            self.rdragging = False
        elif event.RightDown():
            self.SetFocus()
            self.CaptureMouse()
            self.ldragging = False
            self.rdragging = True
            self.notes.OnRightClick(event.GetPosition())

        elif event.Dragging():
            if self.ldragging:
                self.scrollH.OnLDragging(event.GetPosition())
                self.scrollV.OnLDragging(event.GetPosition())
                self.pianoKeys.OnLDragging(event.GetPosition())
                self.notes.OnLDragging(event.GetPosition())
            elif self.rdragging:
                self.notes.OnRightClick(event.GetPosition())

        elif event.LeftUp():
            self.ldragging = False
            self.scrollH.OnLUp()
            self.scrollV.OnLUp()
            self.pianoKeys.OnLUp()
            self.notes.OnLUp()
            try:
                self.ReleaseMouse()
            except:
                pass
        elif event.RightUp():
            self.rdragging = False
            try:
                self.ReleaseMouse()
            except:
                pass
        self.rdragging = False
        self.notes.OnLMouseAction(event.GetPosition())

    def GetClientTuple(self):
        size = self.size()
        sw = size.width()
        sh = size.height()
        return sw, sh
    def CalcCurVirtualPos(self):
        size = self.size()
        sw = size.width()
        sh = size.height()
        rightMost = self.vW-sw
        bottomMost = self.vH-sh
        sx = (self.scrHPos/100.0)*rightMost
        sy = (self.scrVPos/100.0)*bottomMost
        import math
        return math.ceil(sx), math.ceil(sy)

    def IsVisible(self, x, y, w, h):
        sx,sy = self.CalcCurVirtualPos()
        sw,sh = self.GetClientTuple()
        if (sx <= x < sx+sw and sy <= y < sy+sh) or (sx <= x+w < sx+sw and sy <= y+h < sy+sh):
            return True
        else:
            return False
    def Draw(self, painter):
        painter.SetBackground(QtGui.QBrush("WHITE"))
        painter.Clear()
        #painter.SetFont(wx.Font(16, wx.SWISS, wx.NORMAL, wx.BOLD, True))
        #painter.DrawText("Bitmap alpha blending (on all ports but gtk+ 1.2)",
        #            25,25)

        self.grid.Draw(painter)
        self.notes.Draw(painter)
        self.scrollH.Draw(painter)
        self.scrollV.Draw(painter)
        self.pianoKeys.Draw(painter)

    def mouseMoveEvent(self, ev):
        if self.enabled:
            self.notes.OnMouseMove(ev)
            self.notes.OnLDragging(ev)
            self.pianoKeys.mouseMoveEvent(ev)

    def mousePressEvent(self, ev):
        if self.enabled:
            if ev.button() == LMB:
                self.notes.OnLDown(ev)
                self.pianoKeys.mousePressEvent(ev)
            elif ev.button() == RMB:
                self.notes.OnRightClick(ev)

    def mouseReleaseEvent(self, ev):
        if self.enabled:
            self.notes.OnLUp()
            self.pianoKeys.mouseReleaseEvent(ev)



class Notes(object):
    # TODO: 더블 버퍼링으로 해야되네..........
    # wxPython은 그냥 더블버퍼링 온하면 되는데......
    def __init__(self, parent):
        self.parent = parent
        try:
            self.notes = pickle.load(open("test.pys", "r"))
        except:
            self.notes = {}
        if self.notes:
            keys = self.notes.keys()
            keys = [key for key in keys if type(key) is int]
            keys.sort()
            self.noteID = keys[-1] + 1
        else:
            self.noteID = 0
        
        self.draggingNoteKey = None
        self.resizingNoteKey = None
        self.midi = MIDI(self.parent)
        self.parent.setMouseTracking(True)

    def SetNotes(self, notes):
        self.notes = notes
        if self.notes:
            keys = self.notes.keys()
            keys = [key for key in keys if type(key) is int]
            keys.sort()
            self.noteID = keys[-1] + 1
        else:
            self.noteID = 0

    def OnMouseMove(self, ev):
        x, y = ev.pos().x(), ev.pos().y()
        cnum = QtGui.QCursor(QtCore.Qt.ArrowCursor)
        note = self.IsNoteAtPos(x, y)
        if note:
            noteKey, note = note
            if self.IsMouseInResizeArea(note, x, y):
                cnum = QtGui.QCursor(QtCore.Qt.SizeHorCursor)
            else:
                cnum = QtGui.QCursor(QtCore.Qt.PointingHandCursor)
        if self.draggingNoteKey:
            cnum = QtGui.QCursor(QtCore.Qt.PointingHandCursor)
        elif self.resizingNoteKey:
            cnum = QtGui.QCursor(QtCore.Qt.SizeHorCursor)


        #self.parent.SetCursor(cursor)
        self.parent.setCursor(cnum)
    def OnRightClick(self, ev):
        x, y = ev.pos().x(), ev.pos().y()
        note = self.IsNoteAtPos(x, y)
        if note:
            noteKey, note = note
            del self.notes[noteKey]
            f = open("test.pys", "wb")
            pickle.dump(self.notes, f)
            f2 = open("testtempo.pkl", "wb")
            pickle.dump(TempoSingleton.GetTempo(), f2)
            f2.close()
            f.close()

            x2,y2,w,h = self.GetPixelPos(*note)
            size = note[3]
            sx, sy = self.parent.CalcCurVirtualPos()
            sw, sh = self.parent.GetClientTuple()
            oX, oY = self.parent.grid.x, self.parent.grid.y
            self.parent.repaint(oX+x2-sx, oY+y2+1-sy, w, h)
            #self.parent.grid.UpdateRect(x2-sx, y2+1-sy, w, h)

    def GetClicked(self, x, y):
        # 화면을 클릭하면 그리드의 스냅에 맞춰서 가로 어디 세로 어디인지를 찾는다.
        # 이거만 고치면 된다.
        # 리턴하는 snapsub는 모든 섭디비젼의 최소공배수를 골라서 그거의 갯수를 리턴한다.
        cliW, cliH = self.parent.GetClientTuple()
        l, r, t, b = self.parent.grid.GetLRTB()
        kh = self.parent.grid.kh
        kw = self.parent.grid.kw # kw는 16분음표이다. 음... 또는 Grid의 가장 작은 레벨의 길이이다.
        snaps = self.parent.sub.GetSnaps() # 한 편, lowestSnap은 스냅들 중 가장 작은 레벨이며 기준은 온음표 기준이다.
        # 스냅을 만약 레벨들에서 찾을 수 없다면 그냥 한 음이 2분된걸로 생각하면 된다.
        gridPerWhole = self.parent.sub.grids[-1]

        # tempX는 kw*gridPerWhole로 %한다.
        # 일단 모든 스냅의 섭디비젼을 얻어와서 최소공배수를 구하고, 그 최소공배수의 길이를 기준으로 한
        # 길이들로 스냅을 정렬한다.
        # 만약 스냅을 나누는 숫자들의 맨 첫번째가 8(분음표)이었다면 온음표안에 그게 8개 있으므로
        # 그 스냅을 다음 8분음표들의 숫자 만큼(8번) 반복해 준다. 반복마다 몇을 더해야하나?
        # 8분음표의 길이만큼의 최소공배수의 숫자만큼을 더해줘야 한다.

        lcm = 1
        for snap in snaps:
            theSub = 1
            for num in snap[:-1]:
                theSub *= num
            lcm = GetLCM(lcm, theSub)
        lowestSubPerWhole = GetLCM(lcm, 64)

            # 4, 12의 경우
            # 일단 최대공약수를 구해서 그게 있으면 그걸

        
        snapposPixel = float(kw*gridPerWhole) / float(lowestSubPerWhole)


        def GetSnapPosition(x): # 어차피 스냅은 뭐랄까 음... 눈에 보이는 수준에서만 스냅해줄 거니까
            # 스냅의 반복은 무조건 첫번째 분할 수준에서만 반복?
            # 4/3/5:3 일 때는 3번째에서도 스냅 해줘야 하지 않나? 헐... 12/5:3일 때는 해줄 거 아냐..! 흠..
            # 12/5:3일 때만 해주고 즉 반복은 첫번째 레벨에서만 해준다 그냥....귀찮으니까.
            # 음 스냅을 여러 레벨로 하게되니까 이런 문제가 있구나. 그냥 코드는 이래도 쓸 때는 무조건 2단계로만 하게 해야겠다.
            # 4/5:3이랑
            # 3/5:3 그냥 따로 해주고....
            # 스냅 끝. 이제 음을 더블클릭해서 어느 분할의 어느번째의 어느길이만큼인지 정하게 한다.
            # 키만 이동하는 경우에는 스냅에 붙이는 게 아니라 X좌표를 유지하도록 한다.
            snapPositions = []
            for snap in snaps:
                theSub = 1
                for num in snap[:-1]:
                    theSub *= num
                snapPos = (snap[-1]/float(theSub))*lowestSubPerWhole
                snapPositions += [snapPos]
                for i in range(1, snap[0]):
                    snapPositions += [snapPos+(lowestSubPerWhole / snap[0])*i]
            snapPositions += [lowestSubPerWhole]

            if snapPositions:
                snapPositions.sort()
                tempXPixel = x%(kw*gridPerWhole)
                xOffsetPixel = x-(x%(kw*gridPerWhole))
                xOffsetSnaps = xOffsetPixel / snapposPixel
                i = 0
                for snappos in snapPositions:
                    if snappos*snapposPixel <= tempXPixel < snapPositions[i+1]*snapposPixel:
                        return snappos*snapposPixel+xOffsetPixel, lowestSubPerWhole, snappos+xOffsetSnaps

                    i += 1
                    if i == len(snapPositions):
                        break

        sx,sy = self.parent.CalcCurVirtualPos()
        realX, realY = sx+x-l, sy+y-t

        if l <= x <= r and t <= y <= b:
            pixelX, snapSub, snapPos = GetSnapPosition(realX)
            pixY = realY-(realY%kh)
            posY = pixY/kh
            return int(pixelX), int(pixY), snapSub, int(snapPos), int(119-posY)
        else:
            return None

    def AddNote(self, key, dividedby, pos, length): # 온음표를 몇개로 나눈 것을 기준으로 위치와 길이를 삼았는가 하는 것. 아무리 섭디비젼이 많아도 결국 온음표를 몇개로 나눈거인가로 표현이 가능하므로 그렇게 한다.
        self.notes[self.noteID] = note = (key, dividedby, pos, length)
        self.noteID += 1
        f = open("test.pys", "wb")
        f2 = open("testtempo.pkl", "wb")

        pickle.dump(TempoSingleton.GetTempo(), f2)
        f2.close()

        pickle.dump(self.notes, f)
        f.close()
        sx, sy = self.parent.CalcCurVirtualPos()
        sw, sh = self.parent.GetClientTuple()
        oX, oY = self.parent.grid.x, self.parent.grid.y

        x2,y2,w,h = self.GetPixelPos(*note)
        self.parent.repaint(oX+x2-sx, oY+y2+1-sy, w+1, h)



    def IsNoteAtPos(self, x, y):
        noteKeys = self.notes.keys()
        noteKeys.reverse()
        for noteKey in noteKeys:
            note = self.notes[noteKey]
            sx, sy = self.parent.CalcCurVirtualPos()
            sw, sh = self.parent.GetClientTuple()
            oX, oY = self.parent.grid.x, self.parent.grid.y
            x2,y2,w,h = self.GetPixelPos(*note)
            if InRect(oX+x2-sx-1,oY+y2+1-sy,w+2,h-2, x,y):
                return noteKey, note

        return None

    def IsMouseInResizeArea(self, note, x, y):
        #노트의 픽셀 길이의 1/3 이상부터 픽셀길이+1부분까지 리사이즈영역이다.
        # 그 영역의 길이를 최대 12픽셀kw로 한다.
        sx, sy = self.parent.CalcCurVirtualPos()
        sw, sh = self.parent.GetClientTuple()
        oX, oY = self.parent.grid.x, self.parent.grid.y
        x2,y2,w,h = self.GetPixelPos(*note)
        w += 2
        h -= 2
        x2 = oX+x2-sx-1
        y2 = oY+y2+1-sy
        kw = self.parent.grid.kw
        neww = math.ceil(float(w)*(1.0/3.0))
        if neww > kw+5:
            neww = kw
        x2 += w-neww
        neww += 5
        if InRect(x2,y2,neww,h, x,y):
            return True
        else:
            return False

    def GetClickedNoteSnapPosOffset(self, x, y):
        noteKeys = self.notes.keys()
        noteKeys.reverse()
        for noteKey in noteKeys:
            note = self.notes[noteKey]
            sx, sy = self.parent.CalcCurVirtualPos()
            sw, sh = self.parent.GetClientTuple()
            oX, oY = self.parent.grid.x, self.parent.grid.y
            x2,y2,w,h = self.GetPixelPos(*note)
            if InRect(oX+x2-sx-1,oY+y2+1-sy,w+2,h-2, x,y):
                kw = self.parent.grid.kw
                offset = (x - (oX+x2-sx-1))
                offset = (offset-(offset%kw))/kw
                return offset

        return None
    def OnLDown(self, ev):
        x, y = ev.pos().x(), ev.pos().y()
        note = self.IsNoteAtPos(x, y)
        if note:
            noteKey, note = note
            del self.notes[noteKey]
            self.notes[self.noteID] = note
            f = open("test.pys", "wb")
            pickle.dump(self.notes, f)
            f2 = open("testtempo.pkl", "wb")
            pickle.dump(TempoSingleton.GetTempo(), f2)
            f2.close()

            f.close()

            #self.Draw(self.parent.GetDC())
            if self.IsMouseInResizeArea(note, x, y):
                self.resizingNoteKey = self.noteID
            else:
                self.draggingNoteKey = self.noteID
                self.draggingStartSnapPosOffset = self.GetClickedNoteSnapPosOffset(x, y)
                self.parent.vstThd.PlayNote(note[0])
            self.noteID += 1
        else:
            clicked = self.GetClicked(x, y)
            if clicked:
                pixX, pixY, snapSub, snapPos, posY = clicked
                defaultSize = self.parent.sub.defaultSize
                if snapSub == defaultSize[0]:
                    self.AddNote(posY, snapSub, snapPos, defaultSize[1])
                    #self.midi.PlayNote(posY)
                    self.parent.vstThd.PlayNote(posY)
                else:
                    theSub = 1
                    for num in defaultSize[:-1]:
                        theSub *=num

                    lcm = GetLCM(theSub, snapSub)
                    newSub = lcm
                    newSize = (defaultSize[-1]/float(theSub)) * newSub
                    self.AddNote(posY, newSub, int((snapPos/float(snapSub))*newSub), newSize)
                    self.parent.vstThd.PlayNote(posY)
                    #self.midi.PlayNote(posY)

                #self.Draw(self.parent.GetDC())

        self.parent.SetWidth()
    def OnLDragging(self, ev):
        x, y = ev.pos().x(), ev.pos().y()

        if x < 71 or y < 30:
            return
        clicked = self.GetClicked(x, y)
        if self.draggingNoteKey and clicked:
            kw = self.parent.grid.kw
            pixX, pixY, snapSub, snapPos, posY = clicked
            snapPos -= (snapSub/16) * self.draggingStartSnapPosOffset
            if snapPos < 0:
                snapPos = 0
            note = self.notes[self.draggingNoteKey]
            x2,y2,w,h = self.GetPixelPos(*note)
            size = note[3]
            if posY != note[0]:
                #self.midi.PlayNote(posY)
                self.parent.vstThd.PlayNote(posY)
            gridPerWhole = self.parent.sub.grids[-1]
            snapposPixel = float(kw*gridPerWhole) / float(note[1])
            sx,sy = self.parent.CalcCurVirtualPos()
            l, r, t, b = self.parent.grid.GetLRTB()
            realX, realY = sx+x-l, sy+y-t
            if note[2]*snapposPixel < realX < (note[2]+note[3])*snapposPixel and ShiftOn():
                self.notes[self.draggingNoteKey] = (posY,) + note[1:]
                f = open("test.pys", "wb")
                pickle.dump(self.notes, f)
                f.close()

            else:
                if snapSub == note[1]:
                    self.notes[self.draggingNoteKey] = posY, snapSub, snapPos, size
                else:
                    lcm = GetLCM(snapSub, note[1])
                    snapPos = lcm/snapSub*snapPos
                    size = lcm/note[1]*size
                    self.notes[self.draggingNoteKey] = posY, lcm, snapPos, size
                f = open("test.pys", "wb")
                pickle.dump(self.notes, f)
                f2 = open("testtempo.pkl", "wb")
                pickle.dump(TempoSingleton.GetTempo(), f2)
                f2.close()

                f.close()

            sx, sy = self.parent.CalcCurVirtualPos()
            sw, sh = self.parent.GetClientTuple()
            oX, oY = self.parent.grid.x, self.parent.grid.y
            self.parent.repaint(oX+x2-sx-25, oY+y2+1-sy-25, w+1+25, h+25)
            #self.parent.grid.UpdateRect(x2-sx, y2+1-sy, w+1, h)
            #self.Draw(self.parent.GetDC())

        elif self.resizingNoteKey and clicked: # 현재 마우스의 x위치로 스냅을 얻어와야한다.
            # FL Studio처럼 고침.
            kw = self.parent.grid.kw
            clicked = self.GetClicked(x+kw/2, y)
            altDown = AltOn()
            sx, sy = self.parent.CalcCurVirtualPos()
            sw, sh = self.parent.GetClientTuple()
            oX, oY = self.parent.grid.x, self.parent.grid.y

            if clicked:
                pixX, pixY, snapSub, snapPos, posY = clicked
                note = self.notes[self.resizingNoteKey]
                if not altDown:
                    x2,y2,prevW,h = self.GetPixelPos(*self.notes[self.resizingNoteKey])
                    lcm = GetLCM(snapSub, note[1])
                    snapPos = lcm/snapSub*snapPos
                    size = lcm/note[1]*note[2]
                    newSize = snapPos-size

                    if newSize < 0:
                        newSize = 1
                    if newSize < snapSub/16:
                        newSize = snapSub/16
                    self.parent.sub.defaultSize = (lcm, newSize)
                    self.notes[self.resizingNoteKey] = note[0], lcm, lcm/note[1]*note[2], newSize
                    x2,y2,w,h = self.GetPixelPos(*self.notes[self.resizingNoteKey])
                    if prevW > w:
                        w = prevW
                else:
                    x2,y2,prevW,h = self.GetPixelPos(*self.notes[self.resizingNoteKey])
                    snapSub = 16
                    snapSub *= kw
                    lcm = GetLCM(snapSub, note[1])
                    newNotePos = lcm/note[1]*note[2]
                    offsetX = (x+sx-oX) - x2
                    newSize = lcm/snapSub*offsetX

                    if newSize < 0:
                        newSize = 1
                    self.parent.sub.defaultSize = (lcm, newSize)
                    self.notes[self.resizingNoteKey] = note[0], lcm, lcm/note[1]*note[2], newSize
                    x2,y2,w,h = self.GetPixelPos(*self.notes[self.resizingNoteKey])
                    if prevW > w:
                        w = prevW
                f = open("test.pys", "wb")
                pickle.dump(self.notes, f)
                f2 = open("testtempo.pkl", "wb")
                pickle.dump(TempoSingleton.GetTempo(), f2)
                f2.close()

                f.close()

                self.parent.repaint(oX+x2-sx, oY+y2+1-sy, w+1, h)
                #self.parent.grid.UpdateRect(x2-sx, y2+1-sy, w+1, h)
                #self.Draw(self.parent.GetDC())

    def OnLUp(self):
        self.draggingNoteKey = None
        self.resizingNoteKey = None
        self.parent.vstThd.StopNote()
    def OnClick(self, x, y):
        pass

    def Draw(self, painter):
        def DrawNote(theDC, x, y, width, height):
            body = QtGui.QColor(158, 171, 209)
            light1 = QtGui.QColor(230, 244, 255)
            light2 = QtGui.QColor(173, 204, 224)
            shade1 = QtGui.QColor(76, 93, 127)
            shade2 = QtGui.QColor(0, 0, 0)
            theDC.setPen(QtGui.QPen(body))
            theDC.setBrush(QtGui.QBrush(body))
            theDC.drawRect(x, y, width-1, height-1)
            theDC.setPen(QtGui.QPen(light1))
            theDC.setBrush(QtGui.QBrush(light1))
            theDC.drawLine(x+1, y+1, x+width-2, y+1)
            theDC.drawLine(x+1, y+1, x+1, y+height-2)
            theDC.setPen(QtGui.QPen(light2))
            theDC.setBrush(QtGui.QBrush(light2))
            theDC.drawLine(x+2, y+height-3, x+width-3, y+height-3)
            theDC.drawLine(x+width-3, y+2, x+width-3, y+height-2)
            theDC.setPen(QtGui.QPen(shade1))
            theDC.setBrush(QtGui.QBrush(shade1))
            theDC.drawLine(x, y+height-2, x+width-1, y+height-2)
            theDC.drawLine(x+width-2, y, x+width-2, y+height-2)
            theDC.setPen(QtGui.QPen(shade2))
            theDC.setBrush(QtGui.QBrush(shade2))
            theDC.drawLine(x, y+height-1, x+width-1, y+height-1)
            theDC.drawLine(x+width-1, y, x+width-1, y+height-1)

        for note in self.notes.itervalues():
            sx, sy = self.parent.CalcCurVirtualPos()
            sw, sh = self.parent.GetClientTuple()
            oX, oY = self.parent.grid.x, self.parent.grid.y
            key, dividedby, pos, length = note
            x, y, w, h = self.GetPixelPos(key, dividedby, pos, length)
            if self.parent.IsVisible(oX+x,oY+y,w,h):
                DrawNote(painter, oX+x-sx, oY+y+1-sy, w, h-1)
                #self.parent.repaint(oX+x-sx, oY+y+1-sy, w, h-1)

    def GetPixelPos(self, key, sub, pos, length):
        kh = self.parent.grid.kh
        kw = self.parent.grid.kw
        gridPerWhole = self.parent.sub.grids[-1]
        # sub=1
        # 1/16
        # 12/1/16
        lenPerGrid = float(sub) / float(gridPerWhole)
        pixelPerLen = float(kw)/float(lenPerGrid)
        w = pixelPerLen*length
        h = kh
        x = pos*pixelPerLen
        y = kh*(119-key)
        neww = math.ceil(w)
        if neww < 4:
            neww = 4
        return math.ceil(x), math.ceil(y), neww, math.ceil(h)



class MyApp(QtGui.QApplication):
    def __init__(self, argv):
        QtGui.QApplication.__init__(self, argv)
if __name__ == '__main__':

    import sys

    app = MyApp([])
    ApplicationSingleton = app

    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())


"""
일단GUI를 만든다.
간단한 피아노 롤 에디터를 그린다.
노트를 ADD/DELETE할 수 있게 한다.
인터페이스는 FL Studio처럼.
"""
"""
from midiutil.MidiFile import MIDIFile
# Create the MIDIFile Object with 1 track 
MyMIDI = MIDIFile(1) 
Octaves = 10
Names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
Pitch = {}
i = 0
for o in range(Octaves):
    for name in Names:
        Pitch[name+`o`] = i
        i += 1
# Tracks are numbered from zero. Times are measured in beats. 

trackName = "Sample Track"
fileName = "output.mid"
track = 0    
time = 0 
tempo = 120
 
# Add track name and tempo. 
MyMIDI.addTrackName(track,time,trackName) 
MyMIDI.addTempo(track,time,tempo) 
 
# Add a note. addNote expects the following information: 
track = 0 
channel = 0 
pitch = 0  # c5 in  FL Studio, C3 in everything else, 0 = c0 in fl studio
time = 0 
duration = 1 # 4개의 16분음표, 최소 (1.0/4.0)/24.0
volume = 100 
 
# Now add the note. 
MyMIDI.addProgramChange(track,channel,time, 2)
MyMIDI.addNote(track,channel,pitch,time,duration,volume) 
MyMIDI.addNote(track,channel,59,1,(1.0/4.0)/24.0,volume) 
 
# And write it to disk. 
binfile = open(fileName, 'wb') 
MyMIDI.writeFile(binfile) 
binfile.close()
"""
"""
음 하나가 11박자. 8분음표 하나가 11박자. 그래서 16분음표의 길이는 6.
FL Studio랑 똑같은 음 도면에 놓기 기법. 대신 뭐 1' 11" 이렇게 하는 게 아니라 6:1레벨 5:2레벨 3:3레벨 길이 이렇게 지정.
5레벨보다 작은 레벨은 텍스트로 6,5,3,1,4,5,6 이런식으로 할 수 있게.
당연히 악보설정에 악보의 박자 설정이 있어야함.(각레벨마다) 마찬가지로 5레벨까지 설정창주고 그 이상은 3,4,5,6 이런걸로 지정.
길이 설정 뿐만 아니라 위치설정도 해야한다.
세로 그리드는 그대로 써도 되지만 가로 그리드는 32분음표를 기준으로 그려서 8분음표가 11개로 나뉠 때 16분음표가 예를들어 6개인 경우 그걸 놓기 쉽게 해준다.

음.... 그러지 말고 16분음표 기준으로 그리고 6/5/6/5간격으로 그리드를 하고 8분음표 나뉨선은 조금 진하게, 4분음표 좀 더 진하게 1분음표 완전진하게.
FL Studio는 8분음표 나뉨선이 없다. 하지만 6/5/6/5로 나뉘므로 내건 필요하다.

아하. 32분음표를 11로 나누고 16분음표는 2로 나눠서 16분음표1개+32분음표6/11개를 한 음으로? (...)

흠...

음의 위치가 달라졌을 땐 그만큼의 이전 음과의 간격과 어울리게 그 다음에 오는 음의 길이가 정해지면 좀 더 어울린가?

이런 게 있다. 음과 음 사이에 쉼표가 있는 것과 없는것, 오버래핑하는 것의 느낌이 다르다.
0----------
박자 밀고 당기고, 음길이 32분음표이하로 조절하는 것을 지원한다.
-------
리사이즈 할 때 너무 음들이 왼쪽으로만 가는 걸 막기 위해 마우스Coord를 음.... 오른쪽으로 12칸만큼 옮긴다? 리사이즈할 때만.
--------
어택시간동안 볼륨이 빠르게 변하는 걸 구현한다. 이걸 먼저 구현해보자.
어떤 룰로 볼륨이 변할 때 어떤 느낌이 나는가...
------
노트 Off가 있다. note on으로 볼륨 0으로 끄는걸 하는데 off로 바꾼다.
--------------------
VST옵션 canDo에서 VSTHost 에서 yes한 부분만 yes하도록 해보자.
--------------------
흠...악기마다 고유의 리듬이 있어서 그 리듬에 맞게 하면 특유의 소리가 나는 게 아닐까?
------------------
일반 DAW를 이용해서 음악을 만들어보고 거기에 정말로 부족한 걸 느낀다면 이걸 다시 재개하자. 봉인~!
3D(Ogre)를 이용해서 16분음표까지의 그리드를 만들고 그 이상의 조절은 Z좌표로 조절하도록 한다? 음의 길이는 z좌표의 두께로 결정?
--------
음악의 짧은 음과 긴 음이 어울리는 부분이 있다. 짧은 음으로 인트로를 주고 긴 음으로 음악을 진행한다.
------
오 CTYPES에 Structure를 에뮬레이트 하는 기능이 있다. 크래쉬도 안나니 이걸 완성해 보자.
-------
1. 미디 이벤트를 VST로 보내서 사운드를 낸다.
2. 노트들을 사운드로 렌더링한다.
3. VST이펙트를 넣어서 렌더링하거나 사운드를 낸다.

노트 델타:
    마이크로세컨드(1000이 1초) * SamplingRate/1000000
    0부터 시작하는 건지 아니면 또 뭐가 있는지는 모르겠음... 뭐지..
    미디는 0부터 시작 안하고 시작이 있는데.... 아마 VST를 로드하고부터 0부터 시작하나?

    아 processReplacing의 시작이 deltaFrames와 관련이 있고, deltaFrames는 blockSize의 크기보다 커질 수 없다.
    processReplacing의 시작부분이 deltaFrames의 0이고 deltaFrames=blockSize가 바로 끝부분임. 아닌가?
    만약 이렇다면 음 길이가 blockSize보다 긴 건 어쩌고;; 이게 아닌 듯 다시 보자.
--------
알트키를 누르면 음길이 조절되게 한다.
-----------
음... processReplacing이 시간 간격을 정확하게 맞춰주는 게 아니다. 시간 간격은 내가 맞춰서 사운드 버퍼로 보내야 함....
processReplacing이 맞춰주는 시간 간격은 blockSize보다 작은 deltaFrames만큼들의 note들밖에 없다.
그러므로 그거에 맞춰서 이벤트를 보내주고
blockSize(512라면 512로 나눠서)라는 오프셋으로 델타를 분할해서 보내줘야 하는 것인 듯 하다.
1, 40, 200, 500, 700이라면
1,40,200,500 먼저 보내고 그 다음에
700-512 보내야 하는 것이다.

아하... mda piano에서 noteOn의 velocity가 0이 되는 순간 릴리즈가 발동된다.
음.....

이제 사운드도 난다.


노트 읽어서 플레이하는 건 성공!
플레이 도중 플레이를 끊는 걸 해야하고 플레이가 끝나면 자동으로 playing이 아니라는 걸 표시해줘야 한다.
스테레오를 지원해야 한다. 스테레오로 pyaudio를 쓰는법을 배운다.

스테레오 진짜 빡친다. interleave를 numpy로 하는법도 배웠다. ㅋㅋㅋ
-----------
float32는 1.0~-1.0이고 int16은 32767~-32768(?)이므로 32767을 곱해주면 변환이 된다.
wave는 그냥 이러한 숫자의 연속인 듯 하다.
하여간에 렌더링도 성공!
------
음악 이론

하루를 보낸다. 아침에 일어나서 화장실을 갔다가 밥을 먹고 컴퓨터를 하고 영화를 보고 음악을 듣고 뭐 여러가지를 한다.
랜덤한 이벤트.
각각의 이벤트는 여러가지 감정이 있을 것이다. 아침에 일어나서 힘드니 편하게 하기위한 감정이라던가...

이러한 각각의 이벤트에 연결된 감정을 나열한다. 각각의 이벤트의 감정은 연관이 있을 수도 있고 없을 수도 있다.
------------
신디사이져의 비밀.
주파수는 유지하되 3/4박자 또는 4/4박자에 맞추어 볼륨의 낮아졌다 커졌다 한다. 떨림처럼 들리는 박자에 맞는 음색.
음색이 있다. 특정한 음색은 특정한 느낌을 낸다.
또한, 박자의 쉬프트가 있다. 440주파수는 동일한 간격의 사인웨이브가 440개 있는 게 아니라 각각의 440개가 특정한 길이나 특정한 템포를 가지고 있다.
이걸 읽고있는 당신은 이걸 구현해보세영 (...)

또한 거시적인 위이잉잉잉잉잉 하는 "울음소리"가 있다. 이것은 좀 더 거시적인 볼륨의 차이와 거시적인 주파수 각각의 한 개의 주기의 묶음의 변화로 구현된다.

이러한 것들은 첼로 등에서 매우 거시적으로 표현되고 피아노 등에서는 압축된 형태로 표시된다.


"화음" 으로 박자를 구현하는 것이다. 4/4박자와 3/4박자가 혼합된(3/4박자 안에 4/4박자) 것은 바로 화음의 효과이다.

음색의 기본은 FM처럼 음의 쉬프트이다. 이 쉬프트는 박자에 맞게 되면 더욱 음악같은 느낌이 나지만 랜덤해도 된다.

아 화음으로 박자를 구현한다면 템포 역시 중요하게 된다. 440mhz 4/4박자로
------------
frequency = 440*2^((d-69)/12)
---------
음의 길이나 위치 역시 이 웨이브파형의 주기의 갯수에 맞춘다면?
헐... 드디어 비밀을 풀었다. 이로써 내부적인 3박자 4박자 5박자 13박자 등등등... 모두 구현 가능.

하지만 이 박자들은 모두 "실질적인" 박자들일 뿐이고 만약 어떤 "가상의, 음과 관계없이 상상으로 구현되는 박자" 같은 고스트 박자들이 있다면
그런건 어떻게 구현하나? 그런 게 있나?

실제 연주되는 음악에서 어떤 한 라인을 뻈는데도 불구하고 그 라인이 연주되는 듯한 글렌 굴드의 음악 같은 것...


흠 하여간에 이 이론은 뭐랄까 허무맹랑한 소리 같기도 하고, 정말 맞는 이야기 같기도 하나 뭔가가 빠져있고 부족한 건 사실이다.
좀 더 복잡하면서도 수학적으로 아름다운 이론들이 있을 것이다. 여기까지의 발견으로 세계적인 음악가의 비밀을 밝혀낼 수 있을까?

어떤 레시피에는 분명히 특정한 비밀이 있다. 전체 레시피가 완벽하게 똑같은 건 아닐지라도 어떤 특정한 성분이 특정한 맛을 내는 그런 것.

완벽하게 똑같지는 않지만 그 중에서도 중요한 부분을 찾은 기분이 든다. 사실 기분은 오해란 게 있어서 믿을게 못 되지만 글쎄 뭐 하여간에.


아 고스트노트란 건 "시작 부터 그 음이 진행되는 동안 지속적으로 80bpm과 473bpm이 싱크가 맞는 주기가 있듯이" 그러한 여러 주기의 반복으로 인하여
어떠한 "핏치 벤드"의 효과를 낸다. 핏치 쉬프트가 선형적이라면 화음으로 이루어지고 또한 음의 주기의 차이로 이루어지는 핏치 쉬프트는
여러가지 패턴의 정보를 표현하는 랜덤 효과가 있다.
-----------------
Undo가 필요함. ....
저장과 렌더링
메뉴를 만들고 파일이름을 지정해서 저장... 일단 하드코딩으로 저장?
저장했다. 렌더링을 해보자. wave로 렌더링만...
오른쪽 드래그하면 음들이 지워지게 한다. 음 셀렉트하는 기능. 줌인아웃은 투두.
VSTPlugins 폴더를 지정하면 거기서 VST를 읽어와서 이펙트인지 vSTi인지를 테스트해서 목록에 넣고
목록에서 악기를 어딘가에 추가하고
어딘가와 연계해서 거기서 피아노 롤을 열고
악기 목록은 패턴이 있어서 패턴마다 각각의 피아노롤이 있고
플레이리스트가 있어서 각각의 패턴을 넣을 수 있는데...

일단 vSTPlugins부터
그다음은 vst의 Program을 지정하는 것을 한다. 다음 프로그램 로드 버튼을 VSTGUI창에 넣는다. GUI가 없는 플러그인도 있다.
OVST용으로 multichoice dialog를 쓴다. 좋은데?
OVST Option페이지에 플러그인 디렉토리
O스캔 플러그인
O플러그인 리스트도 보여주고
OSet Instruments
OSet Effects버튼을 넣어서 멀티쵸이스로 보여준다.
알트키로 음의 이동도 자세히 할 수 있게 한다. 그 외에 음 더블클릭으로 위치 정하는 것도 하게 하자.
Onote읽어서 뭐 사운드 내고 렌더링 하고 그걸 만들고, 노트 에디터 알트리사이즈 하고 이동시 오프셋줘서 이동할 때 노트의 시작위치가 마우스 포인터쪽으로 점프하는거 해결
O사운드 세이브 하게 한다.
여러 패턴 만들게 한다.
플레이리스트 만든다.
FL studio클론...
선택기능추가


다시.
저장
언두/리두
렌더링
멀티패턴
멀티인스트루먼트
VST이펙트체인
플레이리스트
피아노롤 선택, 이동 삭제 줌인
비트 에디터에서 1키만 가능한데 여러키를 넣을 수 있게 하는 건 필요 없다. 멀티패턴으로 구현 가능하게 한다.


멀티 인스트루먼트부터 해보자
    인스트루먼트에서 VSTWindow를 추가하고 피아노롤과 연계..
O다음은 효과....
OVST의 프로그램 셋팅창
멀티 인스트루먼트와 피아노롤의 연계
    VST창에서 피아노롤을 클릭하면 피아노롤에 setvst룰 허고 setnotes를 하고 플레이를 누르면 그 노트로 플레이...
    사운드 워커나 뭐 렌더 플레이노트워커 다 수정해줘야하고 피아노롤 윈도 수정해준다.
    피아노롤은 했으니 이제 각 피아노롤을 플레이하는 것만 남았다.
저장할 때 모든 데이터를 한개의 피클파일에다가... 세이브파일이라는 클래스를 만든다. 커렌트 프로젝트라는 싱글톤을 만든다.

----------------
두 악기를 합칠 때 그냥 덧셈만 하면 되나? 클리핑되면 어떻게?
-----------------
vst의 program과 파라메터를 읽어와서 종료전에 저장한다.
----------
vst 셋팅창을 1개만 보이게 한다. vst역시 1개만 보이게 한다.
 ---------
 vST이펙트 모노일 때 그냥 스테레오 각각 채널을 따로따로 2번 보낸다. 합치지 말고....
 --------
 이제 효과창을 만들고
 플레이노트워커의 플레이리스트지원과
 렌더노트는 플레이노트워커의코드를복사하지말고 뭔가 제네럴라이제이션을 한다.
 ---------------
 믹서에서 FX를 넣고
 VST셋팅창에서 FX와 연결한다.
 FX는 99개
 FX당 효과 갯수 제한은 걍 무제한으로 한다.

 그 전에, 셋팅 저장하는 거부터 구현한다. 2트랙 만들고 뭐 계속 ㄱ러는거 너무 힘듬..
 ----------
 CDLL을 언로드하는 방법이 있을까?
 걍 gc.collect 해 주자....
----------------------
으 슈발 에러가 너무 많아 wxPython..........
마치 모달 상태가 된 것처럼 창은 안 뜨는데 클릭이 안되는 그런 게 있다.

일단 pyqt로 바꾸고 뭘 진행하도록 하자.

으 힘들어........
pyqt는 GPL이네 근데........음........

뭐 상관 없지. 팔 거 아니니... 일단 고치고 보자.
wxPython예제가 많아서 정말 좋은데, 이 클릭이 안되는 에러때문에 쓸 수가 없다.
파이큐티로 ㄱㄱ
---------------------
피아노롤 또는 패턴마다 여러 폴리리듬을 설정할 수 있도록 각각의 박자를 둔다.
피아노롤 플레이 할 때 다른 패턴을 흐릿하게 보여주고 플레이할 때 그 패턴과 함께 플레이하는 기능도 넣는다? 아니면 그냥 플레이리스트에서 해결?
----------------------
플레이 노트 워커에 RenderMode=True를 주면 렌더하게 한다. 코드 하나만 쓰기!
----------
쉬프트키 스페이스바 등은 MDI부모에서 한번 해보고 전역적으로 되면 그걸 쓰고 안되면 엑셀러레이터 해보고
음..... 전역 키 받기가 되는지 살펴보자.
------
핏치 벤드는 어떻게 하나?
템포 오토메이션!
canDo에있는 기능들 구현
선택적으로 렌더링시 각 음마다 VST파라메터를 조절 가능? 이건 하지 말까...
오토메이션은 어케하는거지.. 한개의 process_replacing이 굉장히 짧은 시간동안이니까 한번 하고 바꾸고 한번 하고 바꾸고 이러면 되는거겠지 물론;;
--------------------
만약 신스에 있는게 로딩시 이펙트로 밝혀지면 이펙트로 이동시키고 반대경우도 그대로 한다.
-------------
플레이리스트를 만들고 플레이리스트의 트랙별 렌더링도 가능하게 한다. 패턴만 렌더링하는 것도 되게 한다. 여기서 중요한 건 정확한 길이로 렌더링하는 것.
---------
PyQt는 Mdi 툴바 윗쪽까지 윈도우 리사이즈가 되는 버그가 있다. ㅡㅡ;;;;;;;;;;
Fix Window Position이란 걸 만들어서 모든 열린 윈도우의 위치를 바꾸는 걸 만든다.
아니다. 스크롤바가 생긴다. LMMS는 스크롤바가 없어서 생기는 버그였다.....
----------------------
이제 믹서를 완성하고 이펙트를 추가, 연결 그리고 이펙트를 먹인 VST에서 소리내는 거까지 한다.
--------------
이제 이펙트를 추가했으니 피아노롤을 악기패널과 연결, 음 하나하나의 FX까지 적용된 소리내기와 음 플레이 음 렌더링을 구현하고
음을 알트키 누르고 이동하면 부드럽게 이동하게 한다.
O패턴 매니져 윈도우 악기 추가할 때마다 리사이즈 해줘야 한다.
O피아노롤 음 추가할 때마다 오른쪽으로 길이 점점 늘어나야 한다. 가장 오른쪽에 있는 음에서 한화면 정도 더 추가해 준다?
O피아노롤이 이미 열려있을 땐 이펙트 추가하면 자동으로 셋인스트루먼트 다시.
이제 플레이와 렌더링을 구현한다. 피아노롤 선택바를 만들고 그 바의 위치
음 선택삭제이동기능
세이브로드
O스크롤 포지션도 바꿔줘야한다.(찍어보면 점프하는게 보임)
삭제하기를 해야한다. 악기,효과삭제하기그리고 기타 팝업메뉴
비트에디터완성
오토메이션 완성
플레이리스트 완성
하악................많다........

그리고 뭔가 노트 찍는게 노트가 많아질수록 느려지는 거 같은 기분이 든다능...ㅡㅡ;;
# TODO:그리기가느림.... PyQt 예제데모에 뭐 빠르게 움직이는 공같은 거 그거 그리는 거 빠른 거 같은데 그거 어케 했나 보고 따라한다
#
오토메이션을 더 자세히 ㅈ효과를 주려면 버퍼 크기를 줄이면 됨...
TODO: VSTi 중에 거의 뭐 10초동안 꼬리가 길~~~~게 유지되는 악기도 있더라.
볼륨이 거의 완전 0에 가까운 것이 512버퍼만큼 지속되는 게 나오기 전까지는 VSTi 클리닝업(렌더링 전에 이전에 플레이하던 거의 꼬리 찌꺼기를 제거하는 것)을 계속
해야한다. 512버퍼 다 검사하면 오래걸리니까 뭐 4개씩 건너 뛰면서 검사한다던가 이래도 된다.
----------
그리기: PyQt데모의 appchooser등을 이용한다. 배경 그리드는 어떻게 그리는지, 배경 그리드에 마우스 이벤트 찍을 때 어떻게 되는 건진 모르겠지만...
------------------------
음 모든것을 내가 알기 쉽게 이해하기 편한 형태로 바꾸어놓고 그걸 진행한다.
소스를 짤 때에도 뭔가 소스를 직접 짜는 것도 좋지만 글로 먼저 써두고 그걸 진행하면 더 좋을 듯.
113.151.8.227 ET
--------------------
아................. 이거 음..... VST가 많이 로드되도 크래쉬나고
Note를 플레이하는거 끝나자마자 "악보 플레이"하면 크래쉬난다능...
어케 해결하나.... 이건 "큐"를 써서 notestop되야 playnotes되게하고... 그리고 코드가 연결되게 해서 크래쉬 안나게 하고ㅓ..... 코드 연결 말고 크래쉬 안나는 법은 없나.....
VST를 많이 한다고 크래쉬뜨는 건 아닌 것 같고 뭔가 다른 DLL이 뭔가 하는 도중에 ADD를 하면 크래쉬뜨는 거 같기도 하고...
Add를 할 때에는 VST에서 뭐 다른 거 안하게 하면 되ㅏ나?
--------
pyqt의 메인루프에서 dll로드 등을 한다. dll사용중에 다른 dll로드하거나 코드를 부르면 에러나는걸지도 모른다.
dll을 로드하기 전에 vst쓰레드를 멈춘다? 흠....
또는 dll로드를 vst쓰레드에게 맡긴다.
-------------
VST 이펙트를 vST악기 하나에다가 추가하게 하고 여러 악기가 1개 vST공유하는 건 마스터 하나로 족하게 한다.
그 이유는 VST이펙트 1개는 공유하는데 그 다음체인이 공유 안하는 거 나오면 합친 거 분리 못하기 때문....
아? 그럴 일은 없겠구나! 무조건 1개의 이펙트만 선택 가능하니.........;; 이건 취소.
--------ggg1
FreeLibrary를 하든 gc.collect를 하든 일단 VST를 다 로드하는 것을 해본다. 수동으로 FL Studio처럼 하는 게 안정적이긴 한데 너무 불편함...
다운 안되게 만들어 보자.
----
subprocess 모듈을 이용해서 DLL을 아예 다른 프로세스에서 로드해버리고 그게 끝나면 자동으로 끝나게?
from msdn about FreeLibrary: When a module's reference count reaches zero or the process terminates, the system unloads the module from the address space of the process.

일단 main이나 VSTMain?이거를 있나 확인해서 발견된 것들만 리스트로 만들고
프로세스 하나하나 띄워서 VST플러그인인지 확인한다.
----------------------------------
쓰레드 말고 프로세스에다 VST를 로드하면 확실히 크래쉬 문제가 해결될 듯 보인다.
아예 VST를 다른 "프로그램"으로 로드해 버리면 더 확실할텐데....
--------
루아로 플러그인을 짜게 한다. 보안때매..
파일 로드 저장 지원 안하지만, 유져가 세이브로드시에 플러그인 데이터를 저장할 수 있도록 저장소 레지스트리에 데이터 등록은 하게 한다.
OnNewFile에 뭐 레지스트리에 등록 이러거나 OnDataRegistryInit에다가 하게 하던가 뭐....
--------------
음.. subprocess는 popen으로 쉘실행만 되고 뭐 같은 프로그램 내의 함수를 다른 프로세스에서 실행하거나 하는 건 안된다.
그냥 VST관련 스크립트를 만들고 파이프로 통신하게 하면서 popen을 쓰자.
------------
threading.Lock을 쓴다.
----------------------
음........ 파이프로 하는 것도 좋지만 일단 그냥 한 함수에서 모든걸 부르면 에러가 안나니까 쓰레드로 해도 될 듯.
-----------------
파라메터 에디터를 잘 만든다. 음 하나하나마다 파라메터를 바꿀 수 있도록.
오토메이션은 걱정할 것 없다. 512프레임마다 파라메터를 바꾸면....;; ㄷㄷ 0.000몇초다.
인터폴레이션을 쓸지 아니면 계단방식을 쓸지 결정한다.

파라메터 "프리셋"을 만들어서, 마치 악기 뱅크처럼 파라메터 에디터에서만 불러올 수 있는 프리셋으로 노가다를 피하게 한다.
preset1 - attack:3, release:4

파람에딧에서: preset1을 현재 음 용으로 사용!
프리셋 2개가 있으면 그 사이의 값을 인터폴레이트 해서 사용 가능!
익스포넨셜하게 인터폴레이트 하는 걸 할까?
---------------------
띠우우웅우우띠웅 이런 드럼의 가죽의 소리와 드럼통의 두우웅 하는 소리가 합쳐져서 드럼소리가 난다.
가죽소리도 절대 무시 불가능. 가죽소리가 드럼통에 울려서 나는거므로?

아니다. 그냥 띠이이이잉 하는 소리만 잘내도 된다. 그 물리적인건 좀 무시해도 가능.

여기서 8개 드럼소리를 다 만들어 본 후에 바로 안드로이드 작업을 착수한다.
"""

