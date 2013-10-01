def cubicInterpolate(p, x):
    return p[1] + 0.5 * x*(p[2] - p[0] + x*(2.0*p[0] - 5.0*p[1] + 4.0*p[2] - p[3] + x*(3.0*(p[1] - p[2]) + p[3] - p[0])))
class Osc(object):
    def __init__(self, table, isFM = False):
        self.isFM = isFM
        self.phase = 0.0
        self.tableSize = 44100
        self.sampleRate = 44100.0
        self.table = table
    def UpdateWithoutInterpolation(self, freq):
        i = int(self.phase)
        self.phase += freq/(self.sampleRate/float(self.tableSize))
        if self.phase >= float(self.tableSize):
            self.phase -= float(self.tableSize)

        if self.isFM:
            if self.phase < 0.0:
                self.phase += float(self.tableSize)

        return self.table[i%self.tableSize]
    def UpdateWithLinearInterpolation(self, freq):
        i = int(self.phase)
        alpha = self.phase - float(i)

        self.phase += freq/(self.sampleRate/float(self.tableSize))

        if self.phase >= float(self.tableSize):
            self.phase -= float(self.tableSize)
        if self.isFM:
            if self.phase < 0.0:
                self.phase += float(self.tableSize)

        dtable0 = self.table[(i+1)%self.tableSize] - self.table[i%self.tableSize]
        val = self.table[i%self.tableSize] + dtable0*alpha
        #print val
        return val 

    def UpdateWithCubicInterpolation(self, freq):
        i = int(self.phase)
        alpha = self.phase - float(i)
        self.phase += freq/(self.sampleRate/float(self.tableSize))
        if self.phase >= float(self.tableSize):
            self.phase -= float(self.tableSize)
        if self.isFM:
            if self.phase < 0.0:
                self.phase += float(self.tableSize)

        return cubicInterpolate(
            [self.table[(i-1)%self.tableSize],self.table[(i)%self.tableSize],self.table[(i+1)%self.tableSize],self.table[(i+2)%self.tableSize]],
            alpha)

import math
class MougFilter(object):
    def __init__(self, cutoff, res):
        """
        cutoff: freq in Hz
        res: 0~1(resnance)
        """
        self.cutoff = cutoff
        self.fs = 44100.0
        self.res = res
        self.y1=self.y2=self.y3=self.y4=self.oldx=self.oldy1=self.oldy2=self.oldy3=0.0
        self.Calc()

    def Calc(self):
        self.f = (self.cutoff+self.cutoff) / self.fs # [0-1]
        self.p = self.f*(1.8-0.8*self.f)
        #self.k=2.0*math.sin(self.f*math.pi/2.0)-1.0;
        self.k=self.p+self.p-1.0
        self.t = (1.0-self.p)*1.386249
        self.t2 = 12.0+self.t*self.t
        self.r = self.res*(self.t2+6.0*self.t)/(self.t2-6.0*self.t)

    def Process(self, input):
        # process input
        self.x = input - self.r-self.y4

        #Four cascaded onepole filters (bilinear transform)
        self.y1 = self.x*self.p + self.oldx*self.p - self.k*self.y1
        self.y2 = self.y1*self.p + self.oldy1*self.p - self.k*self.y2
        self.y3 = self.y2*self.p + self.oldy2*self.p - self.k*self.y3
        self.y4 = self.y3*self.p + self.oldy3*self.p - self.k*self.y4

        #Clipper band limited sigmoid
        self.y4-=(self.y4*self.y4*self.y4)/6.0
        self.oldx = self.x
        self.oldy1 = self.y1
        self.oldy2 = self.y2
        self.oldy3 = self.y3
        return self.y4


class OnePoleFilter(object):
    def __init__(self, res):
        self.a = res
        self.b = 1.0-res
        self.z = 0.0
    def Process(self, input):
        self.z = (input*self.b) + (self.z*self.a)
        return self.z
    def SetRes(self, res):
        self.a = res
        self.b = 1.0-self.a

class OneRCAndCFilter(object):
    def __init__(self, cutoff, res):
        self.c = 0.5**((128.0-float(cutoff)) / 16.0)
        self.r = 0.5**((float(res)+24.0) / 16.0)
        self.v0 = 0.0
        self.v1 = 0.0

    def Process(self, input):
        self.v0 = (1.0-self.r*self.c)*self.v0 - self.c*self.v1 + self.c*input
        self.v1 = (1.0-self.r*self.c)*self.v1 + self.c*self.v0
        return self.v1
    """
    //Parameter calculation
    //cutoff and resonance are from 0 to 127

    c = pow(0.5, (128-cutoff)   / 16.0);
    r = pow(0.5, (resonance+24) / 16.0);

    //Loop:

    v0 =  (1-r*c)*v0  -  (c)*v1  + (c)*input;
    v1 =  (1-r*c)*v1  +  (c)*v0;

    output = v1;
    """

def CreateTables():
    import math
    SR = 44100.0;
    SAMPLE_RATE = 44100
    sin_tbl = [0.0 for i in range(SAMPLE_RATE*2)]
    tri_tbl = [0.0 for i in range(SAMPLE_RATE*2)]
    squ_tbl = [0.0 for i in range(SAMPLE_RATE*2)]
    saw_tbl = [0.0 for i in range(SAMPLE_RATE*2)]
    for i in range(SAMPLE_RATE):
        sin_tbl[i]=math.sin(float(i)*(math.pi*2.0)/SR)
    for i in range(SAMPLE_RATE):
        tri_tbl[i]=(math.acos(math.cos(float(i)*(math.pi*2.0)/SR))/(math.pi*2.0)-0.25)*3.9
    for i in range(SAMPLE_RATE):
        if i < SAMPLE_RATE/2:
            squ_tbl[i] = 1.0
        else:
            squ_tbl[i] = -1.0
    for i in range(SAMPLE_RATE):
        saw_tbl[i]=((2.0*float(i))-SR)/SR

    for i in range(SAMPLE_RATE):
        sin_tbl[i+SAMPLE_RATE] = sin_tbl[i]
    for i in range(SAMPLE_RATE):
        tri_tbl[i+SAMPLE_RATE] = tri_tbl[i]
    for i in range(SAMPLE_RATE):
        squ_tbl[i+SAMPLE_RATE] = squ_tbl[i]
    for i in range(SAMPLE_RATE):
        saw_tbl[i+SAMPLE_RATE] = saw_tbl[i]
    return sin_tbl, tri_tbl, squ_tbl, saw_tbl
"""
Code : 
input  = input buffer;
output = output buffer;
fs     = sampling frequency; 
fc     = cutoff frequency normally something like: 
         440.0*pow(2.0, (midi_note - 69.0)/12.0); 
res    = resonance 0 to 1; 
drive  = internal distortion 0 to 0.1
freq   = 2.0*sin(PI*MIN(0.25, fc/(fs*2)));  // the fs*2 is because it's double sampled
damp   = MIN(2.0*(1.0 - pow(res, 0.25)), MIN(2.0, 2.0/freq - freq*0.5));
notch  = notch output 
low    = low pass output 
high   = high pass output 
band   = band pass output 
peak   = peaking output = low - high
--
double sampled svf loop:
for (i=0; i<numSamples; i++)
{
  in    = input[i]; 
  notch = in - damp*band;
  low   = low + freq*band;
  high  = notch - low;
  band  = freq*high + band - drive*band*band*band;
  out   = 0.5*(notch or low or high or band or peak);
  notch = in - damp*band;
  low   = low + freq*band;
  high  = notch - low;
  band  = freq*high + band - drive*band*band*band;
  out  += 0.5*(same out as above);
  output[i] = out;
}

I was having problems with this filter when DRIVE is set to MAX and Rezonance is set to MIN. A quick way to fix it was to make DRIVE*REZO, so when there's no resonance, there's no need for DRIVE anyway. That fixed the problem.


이러한 여러가지 Linear한 필터들이 있는데
여러 필터를 종합해서 합치거나
핸드 메이드 필터라는 걸 만들어서 노가다 필터를 만들던지 하면 좋을 것 같다.

예를들어 
0~4영역에는 freq*2가 페이드인->페이드아웃되고
4~8영역에는 freq*3가 페이드인->페이드아웃되면서
기존에 만들었던 무조건 freq*2+freq*3이 아닌 사라졌다 나타나는 그런 일련의 애디티브 신디시스.
"""

def main():
    import wave, numpy
    sin, tri, squ, saw = CreateTables()
    table = tri
    freq = 440
    length = 44100*3

    osc = Osc(table)
    data = [osc.UpdateWithCubicInterpolation(freq)*0.5 for i in range(length)]
    f = wave.open("!test.wav", "wb")
    f.setnchannels(2)
    f.setsampwidth(2)
    f.setframerate(44100)

    #filter = OneRCAndCFilter(53, 64) # unusable creates spike of another frequency at start
    #filter = OnePoleFilter(0.9)
    filter = MougFilter(800.0, 0.2) # use cutoff frequency as relation to MIDI NOTE?
    # 
    for i in range(len(data)):
        data[i] = filter.Process(data[i])

    interleaved = numpy.zeros(length*2, dtype=numpy.int16)
    for i in range(length):
        try:
            interleaved[i*2] = data[i]*32767.0
            interleaved[i*2+1] = data[i]*32767.0
        except:
            print data[i]
    interleaved = interleaved.tostring()
    f.writeframes(interleaved)
    f.close()
   # osc.freq
if __name__ == "__main__":
    main()
