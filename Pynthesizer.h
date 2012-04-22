//See associated .cpp file for copyright and other info

#ifndef __Pynthesizer__
#define __Pynthesizer__

#include <string.h>
#include <math.h>
#include "audioeffectx.h"
#include <vector>
using namespace std;

#define NPARAMS  7      //number of parameters
#define NPROGS   256      //number of programs
#define NOUTS    2       //number of outputs
#define NVOICES  64       //max polyphony
#define SILENCE  0.001f  //voice choking
#define M_PI       3.1415926535897932f
#define M_2PI       2*3.1415926535897932f
#define PI       3.1415926535897932f
#define TWOPI    6.2831853071795864f
#define ANALOG   0.002f  //oscillator drift

class PynthesizerProgram
{
  friend class Pynthesizer;
public:
	PynthesizerProgram();
private:
  float param[NPARAMS];
  char  name[24];
};
inline double LPF(double x, double prevY, double cutOff)
{
	return (1.0-cutOff)*prevY + cutOff*x;
}
inline double HPF(double x, double prevX, double prevY, double cutOff)
{
	return cutOff*(prevY + x - prevX);
}
inline double BPF(double x, double prevX, double prevY, double cutOff)
{
	return LPF(HPF(x,prevX,prevY,cutOff), prevY, cutOff);
}
class SineWave{
public:
	SineWave()
	{
		
/*
note on �̺�Ʈ�� �ް� process�� �ް� noteoff�� �޴´�.
�׷��ٸ� note on�� �� ������ �������� �Ͽ� note off�� �� �������� sampleRate��ŭ��processEvents�� �޾ư���.
noteoff-noteon��ŭ�� process�� sampleAmount(����512)��ŭ���� ������ ������� �Ѵ�.
�׷��� noteoff�� ���� ���� �𸣹Ƿ� process���� noteoff�� ������ Ȯ���ϰ� �ȶ����� ��Ȯ���ϴ�.
noteoff�� �ȶ����� �׳� 512��ŭ �� �����ְ� noteoff�� ���� noteoff-noteon�� sampleAmount���ϸ�
�� ���ϸ� �԰� ���ÿ� noteoff���� Release�� �����Ͽ� ����� �����ش�.
*/	}
	~SineWave()
	{
	}
	inline double EveryFirstOfThree(double freq, double sampleRate)
	{//TODO ���߿� �ɽø���;;
	}
	inline double Gen(int note, double iSampleRate, int idx)
	{//sin(freq * (2 * pi) * index / sampleRate)
		double result = GenFreq(GetFrequency(note), iSampleRate, idx);
		return result;
	}
	inline double GenFreq(double freq, double iSampleRate, int idx)
	{//sin(freq * (2 * pi) * index / sampleRate)
		double result = sinf(freq*(M_2PI)*((double)idx*iSampleRate));
		return result;
	}
	inline double GenFreq2PI(double freqBy2PI, double iSampleRate, int idx)
	{//sin(freq * (2 * pi) * index / sampleRate)
		double result = sinf(freqBy2PI*((double)idx*iSampleRate));
		return result;
	}
	inline double GetFrequency(int note)
	{
		return 440.0*powf(2.0,((float)note-69.0)/12.0);
	}
    
};

struct NOTE
{
	int startFrame;
	int onDeltaFrame;
	int offDeltaFrame;
	int frameFilled;
	int vel;
};
struct MYVOICENOTE
{
};
struct MYVOICE
{
	int idx;
	int startFrame;
	int onDeltaFrame;
	int offDeltaFrame;
	int frameFilled;
	int vel;
	int note;
};


class ADSR {
public:
	enum {
		A,
		D,
		S,
		R,
		DONE
	};
	ADSR(){mPrevX = 0.0;mPrevY = 0.0;}
	~ADSR(){}
	void SetALen(int frameNum) {
		lenA = frameNum;
	}
	void SetDLen(int frameNum) {
		lenD = frameNum;
	}
	void SetDVal(float val) {
		d = val;

	}
	void SetSVal(float val) {
		s = val;
	}
	void SetRLen(int frameNum){
		lenR = frameNum;
	}
	void SetRVal(float val) {
		r = val;
	}
	void SetSLen(int frameNum){
		lenS = frameNum;
	}
	void StartRNow()
	{
		mode = ADSR::R;
		idx2 = 0;
		noteOffPos = mVoice.frameFilled;
	}
	void Reset()
	{
		idx2 = 0;
		mode = ADSR::A;
	}
	inline double Get(bool &success)
	{
		double result = 0.0;
		if(d < s)
		{
			d = s;
		}
		if(lenA < 44100/1000.0)
			lenA = 44100/1000.0;
		if(lenD < 44100/1000.0)
			lenD = 44100/1000.0;
		if(lenS < 44100/1000.0)
			lenS = 44100/1000.0;
		if(lenR < 44100/1000.0)
			lenR = 44100/1000.0;

		
		if(mode == ADSR::A)
		{
			float pos = (float)idx2/(float)lenA;
			result = d*pos;
		}
		else if(mode == ADSR::D)
		{

			float pos = ((float)lenD-(float)idx2)/(float)lenD;
			result = s+(d-s)*pos;
		}
		else if(mode == ADSR::S)
		{
			result = s;

		}
		else if(mode == ADSR::R)
		{
			float pos = ((float)lenR-(float)idx2)/(float)lenR;
			result = s*pos;
			/*if(idx2 == lenR)
			{
				char asd[100];
				sprintf(asd, "%f %d", result, idx2);
				MessageBox(NULL, "a", asd, MB_OK);
			}*/

		}

		idx2 += 1;
		success = true;
		if(mode == ADSR::DONE) success = false;
		if(mode == ADSR::A && idx2 > lenA)
		{
			mode = ADSR::D;
			idx2 = 0;
		}
		else if(mode == ADSR::D && idx2 > lenD)
		{
			
			mode = ADSR::S;
			idx2 = 0;
		}
		else if(mode == ADSR::R && idx2 > lenR)
		{
			mode = ADSR::DONE;
			idx2 = 0;
		}
		
		return result;
	}
	int idx2;
	bool noteOff;
	float d,s,r;
	int lenA,lenD,lenS, lenR;
	int mode;
	MYVOICE mVoice;
	bool delMe;
	double mPrevX;
	double mPrevY;
	double freqByPI2[3][4];
	int noteOffPos;
};

class Pynthesizer : public AudioEffectX
{
public:
	Pynthesizer(audioMasterCallback audioMaster);
	~Pynthesizer();
	float mFs;
	double mDeltaCoef;
	SineWave mSineWave;
	vector<ADSR> mMyVoices;
	float d,s,r;
	float lenA,lenD,lenS, lenR;
	unsigned int mOSCIdx;
	float mCutOff;
	float mPrevY1;
	float mPrevY2;

	inline double FillVal(float fs, int idx, float amp, float env, ADSR &adsr)
	{
		double val = 0.0;
		double curVal = 0.0;
		double mod = 1.0;
		val = FillValFreq2_(fs,idx,amp,env,adsr, 0);
		for(int i=1; i<3;++i)
		{
			curVal += FillValFreq2_(fs,idx,amp,env,adsr, i);
			//curVal += curVal;
			//mod *= curVal;
		}
		val = (val+curVal*0.5)*0.5;
		return val;//(val*0.35 + mod*0.65)*10.0;
	}
	inline double FillValFreq2_(float fs, int idx, float amp, float env, ADSR &adsr, int freqIdx)
	{
		double val = mSineWave.GenFreq2PI(adsr.freqByPI2[freqIdx][0], mFs, idx);
		//LPF(val, adsr.mPrevY, 
		//adsr.mPrevY = val;
		//double val= mSineWave.GenFreq(mSineWave.GetFrequency(note+12), mFs, idx)*0.5;
		//double noteup = mSineWave.GenFreq(mSineWave.GetFrequency(note+12*2), mFs, idx);
		//val = val*0.95 + noteup*0.05;
		
		//val += mSineWave.GenFreq(mSineWave.GetFrequency(note+12*3), mFs, idx)*0.5;
		//val += mSineWave.GenFreq(mSineWave.GetFrequency(note+12*4), mFs, idx)*0.2;
		//val += mSineWave.GenFreq(mSineWave.GetFrequency(note+12*5), mFs, idx)*0.1;
		//val += mSineWave.GenFreq(mSineWave.GetFrequency(note)*7.0, mFs, idx)*0.5;
		//val += mSineWave.GenFreq(mSineWave.GetFrequency(note)*8.0, mFs, idx)*0.5;
		//val += mSineWave.GenFreq(mSineWave.GetFrequency(note)*9.0, mFs, idx)*0.5;
		//val += mSineWave.GenFreq(mSineWave.GetFrequency(note)*10.0, mFs, idx)*0.5;
		//val /= 2.0;
		//val = val2;//val*0.35+val2*0.65;
		/*
		double saw =0.0;
		for(int j=1;j<4;++j)
		{
		
		for(int i=1;i<=64;++i)
		{
			saw += mSineWave.GenFreq(mSineWave.GetFrequency(note+12*j)*i, mFs, idx);
		}
		}
		saw /= 32.0*4.0;
		val += saw;
		val *= 0.5;*/
		float val2 = mSineWave.GenFreq2PI(adsr.freqByPI2[freqIdx][1], mFs, idx);
		float val3 = mSineWave.GenFreq2PI(adsr.freqByPI2[freqIdx][2], mFs, idx);
		//val2 += val3;
		//val2 *= 0.5;
		float val4 = mSineWave.GenFreq2PI(adsr.freqByPI2[freqIdx][3], mFs, idx);
		/*powf(val3,4)*/
		double modulation = powf(val,16)*5*powf(val2,8)*1.5*val4*val4;//*powf(val3,4)*val4;
			//*mSineWave.GenFreq(mSineWave.GetFrequency(note+12*3), mFs, idx)
			//*mSineWave.GenFreq(mSineWave.GetFrequency(note+12*5), mFs, idx)
			//*mSineWave.GenFreq(mSineWave.GetFrequency(note)*7.0, mFs, idx)
			/**mSineWave.GenFreq(mSineWave.GetFrequency(note)*9.0, mFs, idx)
			*mSineWave.GenFreq(mSineWave.GetFrequency(note)*8.0, mFs, idx)
			*mSineWave.GenFreq(mSineWave.GetFrequency(note)*10.0, mFs, idx)*/
			//*mSineWave.GenFreq(mSineWave.GetFrequency(note+12*4), mFs, idx)
			//*mSineWave.GenFreq(mSineWave.GetFrequency(note+12*2), mFs, idx);
		double modulation2 = powf(val,4)*powf(val2,3)*powf(val3,2);//*val4;
			

		
		/*double lfo = mSineWave.GenFreq(0.5, mFs, idx);
		if(lfo < 0)
			lfo = -lfo;*/
		//val = modulation*lfo+modulation2*(1.0-lfo);
		val = modulation+modulation2;
		//val *= 0.9;
		val *= amp;
		val *= (env*env+env*env*env)*0.5;
		/*
		���� ��Ʈ������ ���� ���ϱ� �Ǵ� ���ϱ� �������� �ؼ� ���⼭ �غô� ��� ������
		�� �� �� �ְ� �Ѵ�.
		OSC�� ��Ʈ������ �߰��ϰ� OSC1*OSC2�� ������� �ǰ� �ϰų�
		OSC1+OSC2�� ������� �ǰ� �ϰų�
		OSC1*0.35+OSC2*OSC3*OSC4 �� ������� �ǵ��� �� �׷��� �Ѵ�.
		*/
		return val;
	}
	virtual void process(float **inputs, float **outputs, VstInt32 sampleframes);
	virtual void processReplacing(float **inputs, float **outputs, VstInt32 sampleframes);
	virtual VstInt32 processEvents(VstEvents* events);

	virtual void setProgram(VstInt32 program);
	virtual void setProgramName(char *name);
	virtual void getProgramName(char *name);
	virtual void setParameter(VstInt32 index, float value);
	virtual float getParameter(VstInt32 index);
	virtual void getParameterLabel(VstInt32 index, char *label);
	virtual void getParameterDisplay(VstInt32 index, char *text);
	virtual void getParameterName(VstInt32 index, char *text);
	virtual void setSampleRate(float sampleRate);
	virtual void setBlockSize(VstInt32 blockSize);
  virtual void suspend();
  virtual void resume();

	virtual bool getOutputProperties (VstInt32 index, VstPinProperties* properties);
	virtual bool getProgramNameIndexed (VstInt32 category, VstInt32 index, char* text);
	virtual bool copyProgram (VstInt32 destination);
	virtual bool getEffectName (char* name);
	virtual bool getVendorString (char* text);
	virtual bool getProductString (char* text);
	virtual VstInt32 getVendorVersion () {return 1;}
	virtual VstInt32 canDo (char* text);

private:
	void update();  //my parameter update
  //void noteOn(VstInt32 note, VstInt32 velocity);
  void fillpatch(VstInt32 p, char *name,
                 float p0,  float p1,  float p2,  float p3,  float p4,  float p5, 
                 float p6,  float p7,  float p8,  float p9,  float p10, float p11,
                 float p12, float p13, float p14, float p15, float p16, float p17, 
                 float p18, float p19, float p20, float p21, float p22, float p23);
  
  PynthesizerProgram* programs;
};

#endif
// ���� ���̺� �����ÿ� ó�� ���ۺκ��� y���� 0���� ���� ���ϰų�, 0���� �ȳ����� ������ �����.
// �̰� �ذ��ؾ���. ������ �� �ֱ⸸�� ������ �Ȼ���� �ϰ� �������� ���� �߰����� �����ϰų� �߰����� ������ �� �� �����ؾ� �ϸ�
// ���ο��̺갡 idx�� 0���� �����ϸ� �翬�� 0���� �����ؾ��ϴµ� �׷��� ���ϹǷ� ���ο��̺� ���� �˰����� �� ����.
// ������ ���� 0���� ����. �� podium�� ���׷� �ʹ� 64���� ������ ����� �ν��� ���ؼ� -64 ����.
// 0.001�� ������ ������ �ȶ�.
// ���� ������ �κ�. offDelta�� ������ ���� ���� ���������� ����ؼ�(idx���°�� ��������)
// ���� �������� ������ �ֱⰡ ���۵Ǵ� �κ��� idx���� �ڸ���. �̰� ���� ��������� ����.
// ��... �װ� �ƴ϶� ����� �����ָ� ��
// ���Ϳ� mADSR(myvoice���������adsr�ȿ�)�� �ְ� ��Ʈ�� �ϸ� �ϳ��߰�, ��Ʈ�����ÿ� ���� ���� ����
// �������尡 �ƴ� ��Ʈ�� ã�Ƽ� ��������� ��ȯ, �������尡 ������ ����.
// ������Len�� �ʹ� ��� ���� ������ ���ܼ� ����� �����.
// AD�� �ʹ� ��� ������ ª������ ����� �����. ������ ������ Ȯ��.
// ����� �ʹ� ��� ������ ĵ���� ȿ���� �Ͼ�� ����� �����.
// �� �ƴϳ�;; ���״�
// ������ ���� ������ �ణ �ö󰡴ٰ� ���ڱ� ������������ ��������. �ͱ�? �����ذ�. if(d<s)d=s�� ��������ߴ�.
// ��... ���׵� �׷��� �ѵ� ������ĵ������ �´�. OSC�� idx�� �׳� ��� ����. ����ε� ��Ʈ�� �ϸ�
// �ڵ����� ���ε� �ǰ��� ��;;
// ����� ���۵Ǵ� �κп��� ����� �����. ����� ���� �߸��Ǿ��� ���.
