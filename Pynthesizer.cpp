//
// VST2 Plug-in: "p Pynthesizer" v1.1
//
// Copyright(c)1999-2001 Paul Kellett (maxim digital audio)
// Based on VST2 SDK (c)1996-1999 Steinberg Soft und Hardware GmbH, All Rights Reserved
//
#pragma warning(disable: 4244 4305 4996 4819)
#include <Windows.h>
#include <stdio.h>
#include <stdlib.h> //rand()
#include <math.h>
#include "Pynthesizer.h"


AudioEffect *createEffectInstance(audioMasterCallback audioMaster)
{
  return new Pynthesizer(audioMaster);
}


PynthesizerProgram::PynthesizerProgram()
{
  param[0]  = 0.00f; //OSC Mix
  param[1]  = 0.0f; //OSC Tune
  param[2]  = 0.00f; //OSC Fine

  param[3]  = 0.00f; //OSC Mode
  param[4]  = 0.05f; //OSC Rate
  param[5]  = 0.00f; //OSC Bend

  param[6]  = 0.00f; //VCF Freq
  
  //param[7]  = 0.0f; //VCF Reso
  /*param[8]  = 0.75f; //VCF <Env

  param[9]  = 0.00f; //VCF <LFO
  param[10] = 0.50f; //VCF <Vel
  param[11] = 0.00f; //VCF Att

  param[12] = 0.30f; //VCF Dec
  param[13] = 0.00f; //VCF Sus
  param[14] = 0.25f; //VCF Rel

  param[15] = 0.00f; //ENV Att
	param[16] = 0.50f; //ENV Dec
  param[17] = 1.00f; //ENV Sus
	
  param[18] = 0.30f; //ENV Rel
	param[19] = 0.81f; //LFO Rate
	param[20] = 0.50f; //Vibrato
  
  param[21] = 0.00f; //Noise   - not present in original patches
  param[22] = 0.50f; //Octave
  param[23] = 0.50f; //Tuning*/
  strcpy (name, "Default");  
}


Pynthesizer::Pynthesizer(audioMasterCallback audioMaster) : AudioEffectX(audioMaster, NPROGS, NPARAMS)
{
  VstInt32 i=0;
  mOSCIdx = 0;
  mPrevY1 = 0.0;
  mPrevY2 = 0.0;

  programs = new PynthesizerProgram[NPROGS];
	if(programs)
  {
    fillpatch(i++, "Default", 10.0f/125.0f, 25.0f/125.0f, 0.0f, 1000.0/1000.0f, 0.6, 0.4, 0.4f, 0.6f,
		0.12f, 0.0f, 0.5f, 0.9f, 0.89f, 0.9f, 0.73f, 0.0f, 0.5f, 1.0f, 0.71f, 0.81f, 0.65f, 0.0f, 0.5f, 0.5f);
	/*
    fillpatch(i++, "Echo Pad [SA]", 0.88f, 0.51f, 0.5f, 0.0f, 0.49f, 0.5f, 0.46f, 0.76f, 0.69f, 0.1f, 0.69f, 1.0f, 0.86f, 0.76f, 0.57f, 0.3f, 0.8f, 0.68f, 0.66f, 0.79f, 0.13f, 0.25f, 0.45f, 0.5f);
    fillpatch(i++, "Space Chimes [SA]", 0.88f, 0.51f, 0.5f, 0.16f, 0.49f, 0.5f, 0.49f, 0.82f, 0.66f, 0.08f, 0.89f, 0.85f, 0.69f, 0.76f, 0.47f, 0.12f, 0.22f, 0.55f, 0.66f, 0.89f, 0.34f, 0.0f, 1.0f, 0.5f);
    fillpatch(i++, "Solid Backing", 1.0f, 0.26f, 0.14f, 0.0f, 0.35f, 0.5f, 0.3f, 0.25f, 0.7f, 0.0f, 0.63f, 0.0f, 0.35f, 0.0f, 0.25f, 0.0f, 0.5f, 1.0f, 0.3f, 0.81f, 0.5f, 0.5f, 0.5f, 0.5f);
    fillpatch(i++, "Velocity Backing [SA]", 0.41f, 0.5f, 0.79f, 0.0f, 0.08f, 0.32f, 0.49f, 0.01f, 0.34f, 0.0f, 0.93f, 0.61f, 0.87f, 1.0f, 0.93f, 0.11f, 0.48f, 0.98f, 0.32f, 0.81f, 0.5f, 0.0f, 0.5f, 0.5f);
    fillpatch(i++, "Rubber Backing [ZF]", 0.29f, 0.76f, 0.26f, 0.0f, 0.18f, 0.76f, 0.35f, 0.15f, 0.77f, 0.14f, 0.54f, 0.0f, 0.42f, 0.13f, 0.21f, 0.0f, 0.56f, 0.0f, 0.32f, 0.2f, 0.58f, 0.22f, 0.53f, 0.5f);
    fillpatch(i++, "808 State Lead", 1.0f, 0.65f, 0.24f, 0.4f, 0.34f, 0.85f, 0.65f, 0.63f, 0.75f, 0.16f, 0.5f, 0.0f, 0.3f, 0.0f, 0.25f, 0.17f, 0.5f, 1.0f, 0.03f, 0.81f, 0.5f, 0.0f, 0.68f, 0.5f);
    fillpatch(i++, "Mono Glide", 0.0f, 0.25f, 0.5f, 1.0f, 0.46f, 0.5f, 0.51f, 0.0f, 0.5f, 0.0f, 0.0f, 0.0f, 0.3f, 0.0f, 0.25f, 0.37f, 0.5f, 1.0f, 0.38f, 0.81f, 0.62f, 0.0f, 0.5f, 0.5f);
    fillpatch(i++, "Detuned Techno Lead", 0.84f, 0.51f, 0.15f, 0.45f, 0.41f, 0.42f, 0.54f, 0.01f, 0.58f, 0.21f, 0.67f, 0.0f, 0.09f, 1.0f, 0.25f, 0.2f, 0.85f, 1.0f, 0.3f, 0.83f, 0.09f, 0.4f, 0.49f, 0.5f);
    fillpatch(i++, "Hard Lead [SA]", 0.71f, 0.75f, 0.53f, 0.18f, 0.24f, 1.0f, 0.56f, 0.52f, 0.69f, 0.19f, 0.7f, 1.0f, 0.14f, 0.65f, 0.95f, 0.07f, 0.91f, 1.0f, 0.15f, 0.84f, 0.33f, 0.0f, 0.49f, 0.5f);
    fillpatch(i++, "Bubble", 0.0f, 0.25f, 0.43f, 0.0f, 0.71f, 0.48f, 0.23f, 0.77f, 0.8f, 0.32f, 0.63f, 0.4f, 0.18f, 0.66f, 0.14f, 0.0f, 0.38f, 0.65f, 0.16f, 0.48f, 0.5f, 0.0f, 0.67f, 0.5f);
    fillpatch(i++, "Monosynth", 0.62f, 0.26f, 0.51f, 0.79f, 0.35f, 0.54f, 0.64f, 0.39f, 0.51f, 0.65f, 0.0f, 0.07f, 0.52f, 0.24f, 0.84f, 0.13f, 0.3f, 0.76f, 0.21f, 0.58f, 0.3f, 0.0f, 0.36f, 0.5f);
    fillpatch(i++, "Moogcury Lite", 0.81f, 1.0f, 0.21f, 0.78f, 0.15f, 0.35f, 0.39f, 0.17f, 0.69f, 0.4f, 0.62f, 0.0f, 0.47f, 0.19f, 0.37f, 0.0f, 0.5f, 0.2f, 0.33f, 0.38f, 0.53f, 0.0f, 0.12f, 0.5f);
    fillpatch(i++, "Gangsta Whine", 0.0f, 0.51f, 0.52f, 0.96f, 0.44f, 0.5f, 0.41f, 0.46f, 0.5f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f, 0.25f, 0.15f, 0.5f, 1.0f, 0.32f, 0.81f, 0.49f, 0.0f, 0.83f, 0.5f);
    fillpatch(i++, "Higher Synth [ZF]", 0.48f, 0.51f, 0.22f, 0.0f, 0.0f, 0.5f, 0.5f, 0.47f, 0.73f, 0.3f, 0.8f, 0.0f, 0.1f, 0.0f, 0.07f, 0.0f, 0.42f, 0.0f, 0.22f, 0.21f, 0.59f, 0.16f, 0.98f, 0.5f);
    fillpatch(i++, "303 Saw Bass", 0.0f, 0.51f, 0.5f, 0.83f, 0.49f, 0.5f, 0.55f, 0.75f, 0.69f, 0.35f, 0.5f, 0.0f, 0.56f, 0.0f, 0.56f, 0.0f, 0.8f, 1.0f, 0.24f, 0.26f, 0.49f, 0.0f, 0.07f, 0.5f);
    fillpatch(i++, "303 Square Bass", 0.75f, 0.51f, 0.5f, 0.83f, 0.49f, 0.5f, 0.55f, 0.75f, 0.69f, 0.35f, 0.5f, 0.14f, 0.49f, 0.0f, 0.39f, 0.0f, 0.8f, 1.0f, 0.24f, 0.26f, 0.49f, 0.0f, 0.07f, 0.5f);
    fillpatch(i++, "Analog Bass", 1.0f, 0.25f, 0.2f, 0.81f, 0.19f, 0.5f, 0.3f, 0.51f, 0.85f, 0.09f, 0.0f, 0.0f, 0.88f, 0.0f, 0.21f, 0.0f, 0.5f, 1.0f, 0.46f, 0.81f, 0.5f, 0.0f, 0.27f, 0.5f);
    fillpatch(i++, "Analog Bass 2", 1.0f, 0.25f, 0.2f, 0.72f, 0.19f, 0.86f, 0.48f, 0.43f, 0.94f, 0.0f, 0.8f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.61f, 1.0f, 0.32f, 0.81f, 0.5f, 0.0f, 0.27f, 0.5f);
    fillpatch(i++, "Low Pulses", 0.97f, 0.26f, 0.3f, 0.0f, 0.35f, 0.5f, 0.8f, 0.4f, 0.52f, 0.0f, 0.5f, 0.0f, 0.77f, 0.0f, 0.25f, 0.0f, 0.5f, 1.0f, 0.3f, 0.81f, 0.16f, 0.0f, 0.0f, 0.5f);
    fillpatch(i++, "Sine Infra-Bass", 0.0f, 0.25f, 0.5f, 0.65f, 0.35f, 0.5f, 0.33f, 0.76f, 0.53f, 0.0f, 0.5f, 0.0f, 0.3f, 0.0f, 0.25f, 0.0f, 0.55f, 0.25f, 0.3f, 0.81f, 0.52f, 0.0f, 0.14f, 0.5f);
    fillpatch(i++, "Wobble Bass [SA]", 1.0f, 0.26f, 0.22f, 0.64f, 0.82f, 0.59f, 0.72f, 0.47f, 0.34f, 0.34f, 0.82f, 0.2f, 0.69f, 1.0f, 0.15f, 0.09f, 0.5f, 1.0f, 0.07f, 0.81f, 0.46f, 0.0f, 0.24f, 0.5f);
    fillpatch(i++, "Squelch Bass", 1.0f, 0.26f, 0.22f, 0.71f, 0.35f, 0.5f, 0.67f, 0.7f, 0.26f, 0.0f, 0.5f, 0.48f, 0.69f, 1.0f, 0.15f, 0.0f, 0.5f, 1.0f, 0.07f, 0.81f, 0.46f, 0.0f, 0.24f, 0.5f);
    fillpatch(i++, "Rubber Bass [ZF]", 0.49f, 0.25f, 0.66f, 0.81f, 0.35f, 0.5f, 0.36f, 0.15f, 0.75f, 0.2f, 0.5f, 0.0f, 0.38f, 0.0f, 0.25f, 0.0f, 0.6f, 1.0f, 0.22f, 0.19f, 0.5f, 0.0f, 0.17f, 0.5f);
    fillpatch(i++, "Soft Pick Bass", 0.37f, 0.51f, 0.77f, 0.71f, 0.22f, 0.5f, 0.33f, 0.47f, 0.71f, 0.16f, 0.59f, 0.0f, 0.0f, 0.0f, 0.25f, 0.04f, 0.58f, 0.0f, 0.22f, 0.15f, 0.44f, 0.33f, 0.15f, 0.5f);
    fillpatch(i++, "Fretless Bass", 0.5f, 0.51f, 0.17f, 0.8f, 0.34f, 0.5f, 0.51f, 0.0f, 0.58f, 0.0f, 0.67f, 0.0f, 0.09f, 0.0f, 0.25f, 0.2f, 0.85f, 0.0f, 0.3f, 0.81f, 0.7f, 0.0f, 0.0f, 0.5f);
    fillpatch(i++, "Whistler", 0.23f, 0.51f, 0.38f, 0.0f, 0.35f, 0.5f, 0.33f, 1.0f, 0.5f, 0.0f, 0.5f, 0.0f, 0.29f, 0.0f, 0.25f, 0.68f, 0.39f, 0.58f, 0.36f, 0.81f, 0.64f, 0.38f, 0.92f, 0.5f);
    fillpatch(i++, "Very Soft Pad", 0.39f, 0.51f, 0.27f, 0.38f, 0.12f, 0.5f, 0.35f, 0.78f, 0.5f, 0.0f, 0.5f, 0.0f, 0.3f, 0.0f, 0.25f, 0.35f, 0.5f, 0.8f, 0.7f, 0.81f, 0.5f, 0.0f, 0.5f, 0.5f);
    fillpatch(i++, "Pizzicato", 0.0f, 0.25f, 0.5f, 0.0f, 0.35f, 0.5f, 0.23f, 0.2f, 0.75f, 0.0f, 0.5f, 0.0f, 0.22f, 0.0f, 0.25f, 0.0f, 0.47f, 0.0f, 0.3f, 0.81f, 0.5f, 0.8f, 0.5f, 0.5f);
    fillpatch(i++, "Synth Strings", 1.0f, 0.51f, 0.24f, 0.0f, 0.0f, 0.35f, 0.42f, 0.26f, 0.75f, 0.14f, 0.69f, 0.0f, 0.67f, 0.55f, 0.97f, 0.82f, 0.7f, 1.0f, 0.42f, 0.84f, 0.67f, 0.3f, 0.47f, 0.5f);
    fillpatch(i++, "Synth Strings 2", 0.75f, 0.51f, 0.29f, 0.0f, 0.49f, 0.5f, 0.55f, 0.16f, 0.69f, 0.08f, 0.2f, 0.76f, 0.29f, 0.76f, 1.0f, 0.46f, 0.8f, 1.0f, 0.39f, 0.79f, 0.27f, 0.0f, 0.68f, 0.5f);
    fillpatch(i++, "Leslie Organ", 0.0f, 0.5f, 0.53f, 0.0f, 0.13f, 0.39f, 0.38f, 0.74f, 0.54f, 0.2f, 0.0f, 0.0f, 0.55f, 0.52f, 0.31f, 0.0f, 0.17f, 0.73f, 0.28f, 0.87f, 0.24f, 0.0f, 0.29f, 0.5f);
    fillpatch(i++, "Click Organ", 0.5f, 0.77f, 0.52f, 0.0f, 0.35f, 0.5f, 0.44f, 0.5f, 0.65f, 0.16f, 0.0f, 0.0f, 0.0f, 0.18f, 0.0f, 0.0f, 0.75f, 0.8f, 0.0f, 0.81f, 0.49f, 0.0f, 0.44f, 0.5f);
    fillpatch(i++, "Hard Organ", 0.89f, 0.91f, 0.37f, 0.0f, 0.35f, 0.5f, 0.51f, 0.62f, 0.54f, 0.0f, 0.0f, 0.0f, 0.37f, 0.0f, 1.0f, 0.04f, 0.08f, 0.72f, 0.04f, 0.77f, 0.49f, 0.0f, 0.58f, 0.5f);
    fillpatch(i++, "Bass Clarinet", 1.0f, 0.51f, 0.51f, 0.37f, 0.0f, 0.5f, 0.51f, 0.1f, 0.5f, 0.11f, 0.5f, 0.0f, 0.0f, 0.0f, 0.25f, 0.35f, 0.65f, 0.65f, 0.32f, 0.79f, 0.49f, 0.2f, 0.35f, 0.5f);
    fillpatch(i++, "Trumpet", 0.0f, 0.51f, 0.51f, 0.82f, 0.06f, 0.5f, 0.57f, 0.0f, 0.32f, 0.15f, 0.5f, 0.21f, 0.15f, 0.0f, 0.25f, 0.24f, 0.6f, 0.8f, 0.1f, 0.75f, 0.55f, 0.25f, 0.69f, 0.5f);
    fillpatch(i++, "Soft Horn", 0.12f, 0.9f, 0.67f, 0.0f, 0.35f, 0.5f, 0.5f, 0.21f, 0.29f, 0.12f, 0.6f, 0.0f, 0.35f, 0.36f, 0.25f, 0.08f, 0.5f, 1.0f, 0.27f, 0.83f, 0.51f, 0.1f, 0.25f, 0.5f);
    fillpatch(i++, "Brass Section", 0.43f, 0.76f, 0.23f, 0.0f, 0.28f, 0.36f, 0.5f, 0.0f, 0.59f, 0.0f, 0.5f, 0.24f, 0.16f, 0.91f, 0.08f, 0.17f, 0.5f, 0.8f, 0.45f, 0.81f, 0.5f, 0.0f, 0.58f, 0.5f);
    fillpatch(i++, "Synth Brass", 0.4f, 0.51f, 0.25f, 0.0f, 0.3f, 0.28f, 0.39f, 0.15f, 0.75f, 0.0f, 0.5f, 0.39f, 0.3f, 0.82f, 0.25f, 0.33f, 0.74f, 0.76f, 0.41f, 0.81f, 0.47f, 0.23f, 0.5f, 0.5f);
    fillpatch(i++, "Detuned Syn Brass [ZF]", 0.68f, 0.5f, 0.93f, 0.0f, 0.31f, 0.62f, 0.26f, 0.07f, 0.85f, 0.0f, 0.66f, 0.0f, 0.83f, 0.0f, 0.05f, 0.0f, 0.75f, 0.54f, 0.32f, 0.76f, 0.37f, 0.29f, 0.56f, 0.5f);
    fillpatch(i++, "Power PWM", 1.0f, 0.27f, 0.22f, 0.0f, 0.35f, 0.5f, 0.82f, 0.13f, 0.75f, 0.0f, 0.0f, 0.24f, 0.3f, 0.88f, 0.34f, 0.0f, 0.5f, 1.0f, 0.48f, 0.71f, 0.37f, 0.0f, 0.35f, 0.5f);
    fillpatch(i++, "Water Velocity [SA]", 0.76f, 0.51f, 0.35f, 0.0f, 0.49f, 0.5f, 0.87f, 0.67f, 1.0f, 0.32f, 0.09f, 0.95f, 0.56f, 0.72f, 1.0f, 0.04f, 0.76f, 0.11f, 0.46f, 0.88f, 0.72f, 0.0f, 0.38f, 0.5f);
    fillpatch(i++, "Ghost [SA]", 0.75f, 0.51f, 0.24f, 0.45f, 0.16f, 0.48f, 0.38f, 0.58f, 0.75f, 0.16f, 0.81f, 0.0f, 0.3f, 0.4f, 0.31f, 0.37f, 0.5f, 1.0f, 0.54f, 0.85f, 0.83f, 0.43f, 0.46f, 0.5f);
    fillpatch(i++, "Soft E.Piano", 0.31f, 0.51f, 0.43f, 0.0f, 0.35f, 0.5f, 0.34f, 0.26f, 0.53f, 0.0f, 0.63f, 0.0f, 0.22f, 0.0f, 0.39f, 0.0f, 0.8f, 0.0f, 0.44f, 0.81f, 0.51f, 0.0f, 0.5f, 0.5f);
    fillpatch(i++, "Thumb Piano", 0.72f, 0.82f, 1.0f, 0.0f, 0.35f, 0.5f, 0.37f, 0.47f, 0.54f, 0.0f, 0.5f, 0.0f, 0.45f, 0.0f, 0.39f, 0.0f, 0.39f, 0.0f, 0.48f, 0.81f, 0.6f, 0.0f, 0.71f, 0.5f);
    fillpatch(i++, "Steel Drums [ZF]", 0.81f, 0.76f, 0.19f, 0.0f, 0.18f, 0.7f, 0.4f, 0.3f, 0.54f, 0.17f, 0.4f, 0.0f, 0.42f, 0.23f, 0.47f, 0.12f, 0.48f, 0.0f, 0.49f, 0.53f, 0.36f, 0.34f, 0.56f, 0.5f);       
    
    fillpatch(i++,  "Car Horn", 0.57f, 0.49f, 0.31f, 0.0f, 0.35f, 0.5f, 0.46f, 0.0f, 0.68f, 0.0f, 0.5f, 0.46f, 0.3f, 1.0f, 0.23f, 0.3f, 0.5f, 1.0f, 0.31f, 1.0f, 0.38f, 0.0f, 0.5f, 0.5f);
    fillpatch(i++,  "Helicopter", 0.0f, 0.25f, 0.5f, 0.0f, 0.35f, 0.5f, 0.08f, 0.36f, 0.69f, 1.0f, 0.5f, 1.0f, 1.0f, 0.0f, 1.0f, 0.96f, 0.5f, 1.0f, 0.92f, 0.97f, 0.5f, 1.0f, 0.0f, 0.5f);
    fillpatch(i++,  "Arctic Wind", 0.0f, 0.25f, 0.5f, 0.0f, 0.35f, 0.5f, 0.16f, 0.85f, 0.5f, 0.28f, 0.5f, 0.37f, 0.3f, 0.0f, 0.25f, 0.89f, 0.5f, 1.0f, 0.89f, 0.24f, 0.5f, 1.0f, 1.0f, 0.5f);
    fillpatch(i++,  "Thip", 1.0f, 0.37f, 0.51f, 0.0f, 0.35f, 0.5f, 0.0f, 1.0f, 0.97f, 0.0f, 0.5f, 0.02f, 0.2f, 0.0f, 0.2f, 0.0f, 0.46f, 0.0f, 0.3f, 0.81f, 0.5f, 0.78f, 0.48f, 0.5f);
    fillpatch(i++,  "Synth Tom", 0.0f, 0.25f, 0.5f, 0.0f, 0.76f, 0.94f, 0.3f, 0.33f, 0.76f, 0.0f, 0.68f, 0.0f, 0.59f, 0.0f, 0.59f, 0.1f, 0.5f, 0.0f, 0.5f, 0.81f, 0.5f, 0.7f, 0.0f, 0.5f);
    fillpatch(i++,  "Squelchy Frog", 0.5f, 0.41f, 0.23f, 0.45f, 0.77f, 0.0f, 0.4f, 0.65f, 0.95f, 0.0f, 0.5f, 0.33f, 0.5f, 0.0f, 0.25f, 0.0f, 0.7f, 0.65f, 0.18f, 0.32f, 1.0f, 0.0f, 0.06f, 0.5f);
    */
    //for testing...
    //fillpatch(0, "Monosynth", 0.62f, 0.26f, 0.51f, 0.79f, 0.35f, 0.54f, 0.64f, 0.39f, 0.51f, 0.65f, 0.0f, 0.07f, 0.52f, 0.24f, 0.84f, 0.13f, 0.3f, 0.76f, 0.21f, 0.58f, 0.3f, 0.0f, 0.36f, 0.5f);

    setProgram(0);
  }

  if(audioMaster)
	{
		setNumInputs(0);				
		setNumOutputs(NOUTS);
		canProcessReplacing();
		isSynth();
		setUniqueID('MDda');	///
	}
  
  //initialise...
  /*
  for(VstInt32 v=0; v<NVOICES; v++) 
  {
    voice[v].dp   = voice[v].dp2   = 1.0f;
    voice[v].saw  = voice[v].p     = voice[v].p2    = 0.0f;
    voice[v].env  = voice[v].envd  = voice[v].envl  = 0.0f;
    voice[v].fenv = voice[v].fenvd = voice[v].fenvl = 0.0f;
    voice[v].f0   = voice[v].f1    = voice[v].f2    = 0.0f;
    voice[v].note = 0;
  }
  notes[0] = EVENTS_DONE;
  lfo = modwhl = filtwhl = press = fzip = 0.0f; 
  rezwhl = pbend = ipbend = 1.0f;
  volume = 0.0005f;
  K = mode = lastnote = sustain = activevoices = 0;
  noise = 22222;
  */
  update();
	suspend();
}


void Pynthesizer::update()  //parameter change
{
	lenA = programs[curProgram].param[0];
	lenD = programs[curProgram].param[1];
	lenS = programs[curProgram].param[2];
	lenR = programs[curProgram].param[3];
	d = programs[curProgram].param[4];
	s = programs[curProgram].param[5];
	r = programs[curProgram].param[6];
	//mCutOff = programs[curProgram].param[7];
	/*
  double ifs = 1.0 / Fs;
  float * param = programs[curProgram].param;

  mode = (VstInt32)(7.9f * param[3]);
  noisemix = param[21] * param[21];
  voltrim = (3.2f - param[0] - 1.5f * noisemix) * (1.5f - 0.5f * param[7]);
  noisemix *= 0.06f;
  oscmix = param[0];

  semi = (float)floor(48.0f * param[1]) - 24.0f;
  cent = 15.876f * param[2] - 7.938f;
  cent = 0.1f * (float)floor(cent * cent * cent);
  detune = (float)pow(1.059463094359f, - semi - 0.01f * cent);
  tune = -23.376f - 2.0f * param[23] - 12.0f * (float)floor(param[22] * 4.9);
  tune = Fs * (float)pow(1.059463094359f, tune);

  vibrato = pwmdep = 0.2f * (param[20] - 0.5f) * (param[20] - 0.5f);
  if(param[20]<0.5f) vibrato = 0.0f;

  lfoHz = (float)exp(7.0f * param[19] - 4.0f);
  dlfo = lfoHz * (float)(ifs * TWOPI * KMAX); 

  filtf = 8.0f * param[6] - 1.5f;
  filtq  = (1.0f - param[7]) * (1.0f - param[7]); ////// + 0.02f;
  filtlfo = 2.5f * param[9] * param[9];
  filtenv = 12.0f * param[8] - 6.0f;
  filtvel = 0.1f * param[10] - 0.05f;
  if(param[10]<0.05f) { veloff = 1; filtvel = 0; } else veloff = 0;

  att = 1.0f - (float)exp(-ifs * exp(5.5 - 7.5 * param[15]));
  dec = 1.0f - (float)exp(-ifs * exp(5.5 - 7.5 * param[16]));
  sus = param[17];
  rel = 1.0f - (float)exp(-ifs * exp(5.5 - 7.5 * param[18]));
  if(param[18]<0.01f) rel = 0.1f; //extra fast release

  ifs *= KMAX; //lower update rate...

  fatt = 1.0f - (float)exp(-ifs * exp(5.5 - 7.5 * param[11]));
  fdec = 1.0f - (float)exp(-ifs * exp(5.5 - 7.5 * param[12]));
  fsus = param[13] * param[13];
  frel = 1.0f - (float)exp(-ifs * exp(5.5 - 7.5 * param[14]));

  if(param[4]<0.02f) glide = 1.0f; else
  glide = 1.0f - (float)exp(-ifs * exp(6.0 - 7.0 * param[4]));
  glidedisp = (6.604f * param[5] - 3.302f);
  glidedisp *= glidedisp * glidedisp;
  */
}


void Pynthesizer::setSampleRate(float sampleRate)
{
	AudioEffectX::setSampleRate(sampleRate);
  mFs = 1.0/sampleRate;
  mDeltaCoef = sampleRate / 1000000.0;
 
  //dlfo = lfoHz * (float)(TWOPI * KMAX) / Fs; 
}


void Pynthesizer::resume()
{	
  DECLARE_VST_DEPRECATED (wantEvents) ();
}


void Pynthesizer::suspend() //Used by Logic (have note off code in 3 places now...)
{
	mMyVoices.clear();

	/*
  for(VstInt32 v=0; v<NVOICES; v++)
  {
    voice[v].envl = voice[v].env = 0.0f; 
    voice[v].envd = 0.99f;
    voice[v].note = 0;
    voice[v].f0 = voice[v].f1 = voice[v].f2 = 0.0f;
  }*/
}


Pynthesizer::~Pynthesizer()  //destroy any buffers...
{
  if(programs) delete[] programs;
}


void Pynthesizer::setProgram(VstInt32 program)
{
	curProgram = program;
    update();
} //may want all notes off here - but this stops use of patches as snapshots!


void Pynthesizer::setParameter(VstInt32 index, float value)
{
  programs[curProgram].param[index] = value;
  update();

  ///if(editor) editor->postUpdate();
}


void Pynthesizer::fillpatch(VstInt32 p, char *name,
                      float p0,  float p1,  float p2,  float p3,  float p4,  float p5, 
                      float p6,  float p7,  float p8,  float p9,  float p10, float p11,
                      float p12, float p13, float p14, float p15, float p16, float p17, 
                      float p18, float p19, float p20, float p21, float p22, float p23)
{
  strcpy(programs[p].name, name);
  programs[p].param[0]  = p0;   programs[p].param[1]  = p1;
  programs[p].param[2]  = p2;   programs[p].param[3]  = p3;
  programs[p].param[4]  = p4;   programs[p].param[5]  = p5;
  programs[p].param[6]  = p6; /*  programs[p].param[7]  = p7;
  programs[p].param[8]  = p8;   programs[p].param[9]  = p9;
  programs[p].param[10] = p10;  programs[p].param[11] = p11;
  programs[p].param[12] = p12;  programs[p].param[13] = p13;
  programs[p].param[14] = p14;  programs[p].param[15] = p15;
  programs[p].param[16] = p16;  programs[p].param[17] = p17;
  programs[p].param[18] = p18;  programs[p].param[19] = p19;
  programs[p].param[20] = p20;  programs[p].param[21] = p21;
  programs[p].param[22] = p22;  programs[p].param[23] = p23;  */
}


float Pynthesizer::getParameter(VstInt32 index)     { return programs[curProgram].param[index]; }
void  Pynthesizer::setProgramName(char *name)   { strcpy(programs[curProgram].name, name); }
void  Pynthesizer::getProgramName(char *name)   { strcpy(name, programs[curProgram].name); }
void  Pynthesizer::setBlockSize(VstInt32 blockSize) {	AudioEffectX::setBlockSize(blockSize); }
bool  Pynthesizer::getEffectName(char* name)    { strcpy(name, "Pynthesizer"); return true; }
bool  Pynthesizer::getVendorString(char* text)  {	strcpy(text, "The P"); return true; }
bool  Pynthesizer::getProductString(char* text) { strcpy(text, "Pynthesizer"); return true; }


bool Pynthesizer::getOutputProperties(VstInt32 index, VstPinProperties* properties)
{
	if(index<NOUTS)
	{
		sprintf(properties->label, "Pynthesizer %d", index + 1);
		properties->flags = kVstPinIsActive;
		if(index<2) properties->flags |= kVstPinIsStereo; //make channel 1+2 stereo
		return true;
	}
	return false;
}


bool Pynthesizer::getProgramNameIndexed(VstInt32 category, VstInt32 index, char* text)
{
	if ((unsigned int)index < NPROGS)
	{
		strcpy(text, programs[index].name);
		return true;
	}
	return false;
}


bool Pynthesizer::copyProgram(VstInt32 destination)
{
  if(destination<NPROGS)
  {
    programs[destination] = programs[curProgram];
    return true;
  }
	return false;
}


VstInt32 Pynthesizer::canDo(char* text)
{
	if(!strcmp (text, "receiveVstEvents")) return 1;
	if(!strcmp (text, "receiveVstMidiEvent"))	return 1;
	return -1;
}


void Pynthesizer::getParameterName(VstInt32 index, char *label)
{
	switch (index)
	{
		case  0: strcpy(label, "ALen"); break;
		case  1: strcpy(label, "DLen"); break;
		case  2: strcpy(label, "SLen"); break;
		case  3: strcpy(label, "RLen"); break;
		
		case  4: strcpy(label, "DVal"); break;
		case  5: strcpy(label, "SVal"); break;
		case  6: strcpy(label, "RVal"); break;
		case  7: strcpy(label, "Cutoff"); break;
    default: strcpy(label, "Tuning  ");
	}
}


void Pynthesizer::getParameterDisplay(VstInt32 index, char *text)
{
	char string[16];
	float * param = programs[curProgram].param;
  
  switch(index)
  {
    case  0: sprintf(string, "%d", (int)(param[index]*125.0)); break;
    case  1: sprintf(string, "%d", (int)(param[index]*125.0)); break;
    case  2: sprintf(string, "%d", (int)(param[index]*125.0)); break; 
    case  3: sprintf(string, "%d", (int)(param[index]*1000.0)); break; 
    case  4: sprintf(string, "%.4f", param[index]); break; 
    case  5: sprintf(string, "%.4f", param[index]); break; 
    case  6: sprintf(string, "%.4f", param[index]); break; 
	case  7: sprintf(string, "%.4f", param[index]); break; 
    default: sprintf(string, "%.0f", 100.0f * param[index]);
  }
	string[8] = 0;
	strcpy(text, (char *)string);
}


void Pynthesizer::getParameterLabel(VstInt32 index, char *label)
{
  switch(index)
  {
    case  0: 
    case  1: 
	case  2: 
	case  3:
		strcpy(label, "ms");
		break;
    case  4: 
	case  5: 
	case  6:
	case  7:
		strcpy(label, "");
		break;
    default: strcpy(label, "      % ");
  }
}


void Pynthesizer::process(float **inputs, float **outputs, VstInt32 sampleFrames)
{
	processReplacing(inputs,outputs,sampleFrames);

}


void Pynthesizer::processReplacing(float **inputs, float **outputs, VstInt32 sampleFrames)
{
	float* out1 = outputs[0];
	float* out2 = outputs[1];
	for(int j=0;j<sampleFrames;++j)
	{
		out1[j] = 0;
		out2[j] = 0;
	}

	for(vector<ADSR>::iterator i=mMyVoices.begin(); i != mMyVoices.end();++i)
	{
		double amp = (double)i->mVoice.vel/127.0;
		amp *= 0.40;   // 앰프는 무조건 상수여야 한다. 갑자기 줄어들면 노이즈가 생긴다.
		//deltaFrame <= 0일 경우는 델타프레임에 관계없이 그냥 바로 시작하고 <= 0이 아닐 경우 델타 이후에
		// 시작하면 된다.
		// 오프델타는 R이 시작하는 위치이므로 그 때 startrnow를 하면 된다.
		// 걍 다른거 상관없이 모드가 R이 아니고 deltaOffFrame이 있는 경우 샘플+deltaOffFrame
		// 만큼의 위치에서 startrnow를 한다.
		if(i->mVoice.onDeltaFrame == -1) continue;
		if(i->mVoice.onDeltaFrame == 0)
		{
			if(i->mVoice.offDeltaFrame == -1)
			{
				for(int j=0;j<sampleFrames;++j)
				{
					bool suc=true;
					float env = i->Get(suc);
					double val;
					
					if(suc)
						val = FillVal(mFs, i->mVoice.idx, amp, env, *i);
					else
					{
						i->delMe = true;
						break;
					}
					out1[j] += val;
					out2[j] += val;
					i->mVoice.idx++;
				}
				
				i->mVoice.frameFilled += sampleFrames;
			}
			else if(i->mVoice.offDeltaFrame >= 0 && i->mVoice.offDeltaFrame < sampleFrames)
			{
				for(int j=0;j<i->mVoice.offDeltaFrame;++j)
				{
					bool suc=true;
					float env = i->Get(suc);
					double val;
					
					if(suc)
						val = FillVal(mFs, i->mVoice.idx, amp, env, *i);
					else
					{
						i->delMe = true;
						break;
					}
					out1[j] += val;
					out2[j] += val;
					i->mVoice.idx++;
				}
				if(i->mode != ADSR::R && i->mode != ADSR::DONE)
					i->StartRNow();
				for(int j=i->mVoice.offDeltaFrame;j<sampleFrames;++j)
				{
					bool suc=true;
					float env = i->Get(suc);
					double val;
					
					if(suc)
						val = FillVal(mFs, i->mVoice.idx, amp, env, *i);
					else
					{
						i->delMe = true;
						break;
					}
					out1[j] += val;
					out2[j] += val;
					i->mVoice.idx++;
				}

				i->mVoice.frameFilled += sampleFrames;
				i->mVoice.offDeltaFrame = 0;
			}
			else if(i->mVoice.offDeltaFrame >= sampleFrames)
			{
				for(int j=0;j<sampleFrames;++j)
				{
					bool suc=true;
					float env = i->Get(suc);
					double val;
					
					if(suc)
						val = FillVal(mFs, i->mVoice.idx, amp, env, *i);
					else
					{
						i->delMe = true;
						break;
					}
					out1[j] += val;
					out2[j] += val;
					i->mVoice.idx++;
				}
				
				i->mVoice.frameFilled += sampleFrames;
				i->mVoice.offDeltaFrame -= sampleFrames;
			}
		}
		else if(i->mVoice.onDeltaFrame > 0 && i->mVoice.onDeltaFrame < sampleFrames)
		{
			if(i->mVoice.offDeltaFrame == -1)
			{
				for(int j=i->mVoice.onDeltaFrame;j<sampleFrames;++j)
				{
					bool suc=true;
					float env = i->Get(suc);
					double val;
					
					if(suc)
						val = FillVal(mFs, i->mVoice.idx, amp, env, *i);
					else
					{
						i->delMe = true;
						break;
					}
					out1[j] += val;
					out2[j] += val;
					i->mVoice.idx++;
				}
				
				i->mVoice.frameFilled += sampleFrames;
			}
			else if(i->mVoice.offDeltaFrame >= 0 && i->mVoice.offDeltaFrame < sampleFrames)
			{
				for(int j=i->mVoice.onDeltaFrame;j<i->mVoice.offDeltaFrame;++j)
				{
					bool suc=true;
					float env = i->Get(suc);
					double val;
					
					if(suc)
						val = FillVal(mFs, i->mVoice.idx, amp, env, *i);
					else
					{
						i->delMe = true;
						break;
					}
					out1[j] += val;
					out2[j] += val;
					i->mVoice.idx++;
				}
				if(i->mode != ADSR::R && i->mode != ADSR::DONE)
					i->StartRNow();
				for(int j=i->mVoice.offDeltaFrame;j<sampleFrames;++j)
				{
					bool suc=true;
					float env = i->Get(suc);
					double val;
					
					if(suc)
						val = FillVal(mFs, i->mVoice.idx, amp, env, *i);
					else
					{
						i->delMe = true;
						break;
					}
					out1[j] += val;
					out2[j] += val;
					i->mVoice.idx++;
				}

				i->mVoice.frameFilled += sampleFrames;
				i->mVoice.offDeltaFrame = 0;
			}
			else if(i->mVoice.offDeltaFrame >= sampleFrames)
			{
				for(int j=i->mVoice.onDeltaFrame;j<sampleFrames;++j)
				{
					bool suc=true;
					float env = i->Get(suc);
					double val;
					
					if(suc)
						val = FillVal(mFs, i->mVoice.idx, amp, env, *i);
					else
					{
						i->delMe = true;
						break;
					}
					out1[j] += val;
					out2[j] += val;
					i->mVoice.idx++;
				}
				
				i->mVoice.frameFilled += sampleFrames;
				i->mVoice.offDeltaFrame -= sampleFrames;
			}
			// 델타만큼 기다렸다가 채우기 시작하고 끝나면 0으로 셋팅한다.
			i->mVoice.onDeltaFrame = 0;
		}
		else if(i->mVoice.onDeltaFrame >= sampleFrames)
		{
			i->mVoice.onDeltaFrame -= sampleFrames;
		}

		if(i->noteOff && (i->mVoice.frameFilled-i->noteOffPos) > 44100.0*10.0)
		{
			i->delMe = true;
		}
	}
		///

	bool done=false;
	while(!done)
	{
		done=true;
		for(vector<ADSR>::iterator it=mMyVoices.begin();it!=mMyVoices.end();++it)
		{
			
			if(it->delMe)
			{
				done=false;
				mMyVoices.erase(it);
				break;
			}
		}
		
	}

		
	
}

VstInt32 Pynthesizer::processEvents(VstEvents* ev)
{
  VstInt32 npos=0;
  
  for (VstInt32 i=0; i<ev->numEvents; i++)
  {
	if((ev->events[i])->type != kVstMidiType) continue;
	VstMidiEvent* event = (VstMidiEvent*)ev->events[i];
	char* midiData = event->midiData;
	int note;		
	ADSR newADSR;
    switch(midiData[0] & 0xf0) //status byte (all channels)
    {
      case 0x80: //note off
  		note = midiData[1] & 0x7F;
		if(!(0 <= note && note <= 96))
			note = 0;

		for(vector<ADSR>::iterator i=mMyVoices.begin(); i != mMyVoices.end(); ++i)
		{
			if(i->mVoice.note == note && !i->noteOff)
			{
				i->noteOff = true;
				i->mVoice.offDeltaFrame = event->deltaFrames;
				//i->StartRNow();
				break;
			}
		}
		break;

      case 0x90: //note on
		note = midiData[1] & 0x7F;
		if(!(0 <= note && note <= 96))
			note = 0;
		

		newADSR.SetALen((int)(lenA*125.0f*44100.0f/1000.0f));
		newADSR.SetDLen((int)(lenD*125.0f*44100.0f/1000.0f));
		newADSR.SetRLen((int)(lenR*1000.0f*44100.0f/1000.0f));
		newADSR.SetDVal(d);
		newADSR.SetSVal(s);
		newADSR.Reset();
		newADSR.mVoice.onDeltaFrame = event->deltaFrames;
		newADSR.mVoice.offDeltaFrame = -1;
		newADSR.mVoice.frameFilled = 0;
		newADSR.mVoice.vel = midiData[2] & 0x7F;
		newADSR.mVoice.note = note;
		newADSR.noteOff = false;
		newADSR.mVoice.idx = 0;
		newADSR.delMe = false;
		for(int ii=1;ii<=3;++ii)
		{
			newADSR.freqByPI2[ii-1][0] = mSineWave.GetFrequency(note)*ii*M_2PI;
			newADSR.freqByPI2[ii-1][1] = mSineWave.GetFrequency(note)*ii*2*M_2PI;
			newADSR.freqByPI2[ii-1][2] = mSineWave.GetFrequency(note)*ii*4*M_2PI;
			newADSR.freqByPI2[ii-1][3] = mSineWave.GetFrequency(note)*ii*6*M_2PI;
		}
		mMyVoices.push_back(newADSR);
		

		break;

      case 0xB0: //controller
        switch(midiData[1])
        {
          case 0x01:  //mod wheel
            //modwhl = 0.000005f * (float)(midiData[2] * midiData[2]);
            break;
          case 0x02:  //filter +
          case 0x4A:
            //filtwhl = 0.02f * (float)(midiData[2]);
            break;
          case 0x03:  //filter -
            //filtwhl = -0.03f * (float)(midiData[2]);
            break;

          case 0x07:  //volume
            //volume = 0.00000005f * (float)(midiData[2] * midiData[2]);
            break;

          case 0x10:  //resonance
          case 0x47:
            //rezwhl = 0.0065f * (float)(154 - midiData[2]);
            break;

          case 0x40:  //sustain
		
			  /*
            sustain = midiData[2] & 0x40;
            if(sustain==0)
            {
              notes[npos++] = event->deltaFrames;
              notes[npos++] = SUSTAIN; //end all sustained notes, 피아노 소리 울리게하는 페달구현
              notes[npos++] = 0;
            }*/
            break;

          default:  //all notes off
			  mMyVoices.clear();
            break;
        }
        break;

      case 0xC0: //program change
        if(midiData[1]<NPROGS) setProgram(midiData[1]);
        break;

      case 0xD0: //channel aftertouch
        //press = 0.00001f * (float)(midiData[1] * midiData[1]);
        break;
      
      case 0xE0: //pitch bend
        //ipbend = (float)exp(0.000014102 * (double)(midiData[1] + 128 * midiData[2] - 8192));
        //pbend = 1.0f / ipbend;
        break;
      
      default: break;
    }

    //if(npos>EVENTBUFFER) npos -= 3; //discard events if buffer full!!
    event++;
	}
  //notes[npos] = EVENTS_DONE;
	return 1;
}
// 이제 ADSR에서 최소 S값이 있어서 AD+최소S값을 모두 채워야 R모드로 들어가고 그래야 음이 끝나게 한다.
//지금은 음이 짧으면 너무 빨리 끝나는 거 같음. 이게 맞는건가?
// 한 음이 반복될 때 지직거리는 소리난다. 이유는 당연히 보이스를 하나 제거하므로 그렇다.
// 보이스를 제거할 때 바로 끝나버려서 지직거리므로
// 이걸 해결해야 한다.
// 바로 안끝나고 부드럽게 끝나면 되나?
// 새 노트는 바로 시작해야 하므로 64단계에 거쳐 빠른 속도 줄임을 하고 64샘플 이후에 새노트가 시작되
// 도록 한다.
// 음 이렇게 하니까 드럼소리같은 소리처럼 된다. 걍 지금은 이렇게 하고 나중엔 새 보이스를 넣어서
// 한 노트에 여러 보이스가 있도록 한다. 어차피 노트오프 먼저 뜨므로 노트오프 떴으니 새 보이스를
// 넣어서 하면 된다.
// 노트가 바로 끝나게 하는건 잘못된 것. 중간에 또다른 주파수가 생겨 튀는 소리가 난다.
// 델타프레임즈는 다음 process+deltaFrames에서 음이 시작하거나 끊긴다는 걸 의미한다. 지금 잘못쓰고있음.
// TODO: SLen을 추가하고 RVal을 추가한다. 즉, 음이 안끝나도 먼저 끝나거나 음이 끝나도 늦게 끝나거나. 그리고 S값이 서서히 감소한다.
// TODO: 이거 빨리 구현해야 하는데 ADSR에서 AD합친 길이가 음길이보다 길 경우 AD를 다 하고 S최소값이 있어서 S만큼 채우고 릴리즈까지 하고 끝나도록 한다.
// 아 노이즈 버그는 앰프가 상수여야하는데 노트보이스가 늘었을 때 갑자기 볼륨이 줄어들어 생기는 거였다.
// fillval에서 완성된 val을 하나의 주파수로 보고 이거를 10개 만들어서 애디티브랑 모듈레이션을 하면 어떠까?

// 프리퀜시와 pi2를 미리 노트온시에 곱해두고 계속 쓴다.