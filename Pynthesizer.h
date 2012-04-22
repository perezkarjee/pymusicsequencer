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
note on 이벤트를 받고 process를 받고 noteoff를 받는다.
그렇다면 note on이 된 시점을 기준으로 하여 note off가 뜬 시점까지 sampleRate만큼씩processEvents가 받아간다.
noteoff-noteon만큼을 process의 sampleAmount(보통512)만큼씩만 나눠서 전해줘야 한다.
그런데 noteoff가 언제 뜰지 모르므로 process전에 noteoff가 떴으면 확실하고 안떴으면 불확실하다.
noteoff가 안떴으면 그냥 512만큼 다 전해주고 noteoff가 떳고 noteoff-noteon이 sampleAmount이하면
그 이하를 함과 동시에 noteoff부터 Release를 생성하여 릴리즈를 전해준다.
*/	}
	~SineWave()
	{
	}
	inline double EveryFirstOfThree(double freq, double sampleRate)
	{//TODO 나중에 심시마면;;
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
		조합 매트릭스를 만들어서 곱하기 또는 더하기 연산으로 해서 여기서 해봤던 모든 조합을
		다 할 수 있게 한다.
		OSC를 매트릭스에 추가하고 OSC1*OSC2가 결과값이 되게 하거나
		OSC1+OSC2가 결과값이 되게 하거나
		OSC1*0.35+OSC2*OSC3*OSC4 가 결과값이 되도록 뭐 그렇게 한다.
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
// 사인 웨이브 생성시에 처음 시작부분의 y값이 0부터 시작 안하거나, 0으로 안끝나면 잡음이 생긴다.
// 이걸 해결해야함. 완전한 한 주기만이 잡음을 안생기게 하고 완전하지 못한 중간에서 시작하거나 중간에서 끝나는 걸 다 제거해야 하며
// 사인웨이브가 idx가 0부터 시작하면 당연히 0부터 시작해야하는데 그렇지 못하므로 사인웨이브 생성 알고리즘을 잘 본다.
// 시작은 이제 0부터 잘함. 걍 podium의 버그로 초반 64개의 샘플을 제대로 인식을 못해서 -64 해줌.
// 0.001초 정도니 눈에도 안띔.
// 이제 끝나는 부분. offDelta가 생기자 마자 언제 끝나는지를 계산해서(idx몇번째에 끝나는지)
// 가장 마지막에 사인의 주기가 시작되는 부분의 idx에서 자른다. 이걸 어케 계산할지가 관건.
// 아... 그게 아니라 릴리즈를 잘해주면 땡
// 벡터에 mADSR(myvoice도들어있음adsr안에)을 넣고 노트온 하면 하나추가, 노트오프시에 가장 먼저 들어온
// 릴리즈모드가 아닌 노트를 찾아서 릴리즈모드로 전환, 릴리즈모드가 끝나면 제거.
// 릴리즈Len이 너무 길면 낮은 볼륨이 생겨서 노이즈가 생긴다.
// AD가 너무 길면 음보다 짧아져서 노이즈가 생긴다. 노이즈 생성시 확인.
// 릴리즈가 너무 길면 노이즈 캔슬링 효과가 일어나서 노이즈가 생긴다.
// 엥 아니네;; 버그다
// 디케이 없이 어택이 약간 올라가다가 갑자기 서스테인으로 가버린다. 왤까? 버그해결. if(d<s)d=s를 잘해줘야했다.
// 아... 버그도 그렇긴 한데 노이즈캔슬링도 맞다. OSC의 idx를 그냥 계속 쓴다. 언사인드 인트로 하면
// 자동으로 래핑도 되겠지 뭐;;
// 릴리즈가 시작되는 부분에서 노이즈가 생긴다. 릴리즈가 뭔가 잘못되었단 얘기.
