import wave
import math
import sys
import struct
import pyaudio

def swar2freq(swar,basefreq):
    f=0
    mapper={
        's':{
            'shuddh':basefreq,
            'vakra':basefreq,
            },
        'r':{
            'shuddh':int(1.125*float(basefreq)),
            'vakra':int(1.058*float(basefreq))
            },
        'g':{
            'shuddh':int(1.266*float(basefreq)),
            'vakra':int(1.188*float(basefreq))
            },
        'm':{
            'shuddh':int(1.333*float(basefreq)),
            'vakra':int(1.412*float(basefreq)),
            },
        'p':{
            'shuddh':int(1.5*float(basefreq)),
            'vakra':int(1.5*float(basefreq)),
            },
        'd':{
            'shuddh':int(1.688*float(basefreq)),
            'vakra':int(1.586*float(basefreq)),
            },
        'n':{
            'shuddh':int(1.898*float(basefreq)),
            'vakra':int(1.78*float(basefreq)),
            },
        '0':0,
        
    }

    allowed_inputs=['s','r','g','m','p','d','n','^','<','>']
    whichoctave=''
    whichswar=''

    if swar[0] in allowed_inputs:
        if len(swar)==1:
            return mapper[swar]['shuddh']
        elif len(swar)==2:
            if swar[0] in ['<','>']:
                _oct=swar[0]
                note=swar[1]
                return int(octavespecifier(_oct)*float(mapper[note]['shuddh']))
            elif swar[0] in ['s','r','g','m','p','d','n']:
                note=swar[0]
                return mapper[note]['vakra']

        elif len(swar)==3:
            _oct=swar[0]
            note=swar[1]
            sor_v=swar[2]

            return int(octavespecifier(_oct)*float(mapper[note]['vakra']))
    else:
        return mapper['0']
    
def octavespecifier(octave):
    
    loctave=0.5
    uoctave=2.0
    if octave=='<':
        return loctave
    elif octave=='>':
        return uoctave


def wf_specifier(freq,a,sr,d):
    # Defines waveform for a given duration and frequency
    wf=[]
    # 5% taper
    taper=0.00
    for i in range(int((1-taper)*D*float(sr))):
        wf.append(int(A*math.cos(freq*math.pi*float(i)/float(sr))))
    for i in range(int((taper)*D*float(sr))):
        wf.append(int(0))

    return wf
def play_soundfile(path):
    
    chunk = 100
    
    # if len(sys.argv) < 2:
    #     print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    #     sys.exit(-1)
    
    wf = wave.open(path, 'rb')
    
    p = pyaudio.PyAudio()
    
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    
    data = wf.readframes(chunk)

    while len(data)>0 :
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()
    
    p.terminate()
    
def notationreader(swarstring):
    lower_scale_modifier='<'
    upper_scale_modifier='>'
    premodifiers=[lower_scale_modifier,upper_scale_modifier]
    postmodifiers=['^','$']
    translatedSwars=[]
    all_swars=[]
    single_swar=''
    for each_raw_matra in swarstring.split(','):
        position=0
        single_swar=''
        while position < len(each_raw_matra):

            if each_raw_matra[position] in premodifiers:
                if (position+2 < len(each_raw_matra)) and (each_raw_matra[position+2] in postmodifiers):
                    single_swar=each_raw_matra[position:position+3]
                    position+=3
                else:
                    single_swar=each_raw_matra[position:position+2]
                    position+=2
            else:
                if (position+1 < len(each_raw_matra)) and (each_raw_matra[position+1] in postmodifiers):
                    single_swar=each_raw_matra[position:position+2]
                    position+=2
                else:
                    single_swar=each_raw_matra[position]
                    position+=1
            #print(position,single_swar)
            all_swars.append(single_swar)
            single_swar=''
        translatedSwars.append(all_swars)
        all_swars=[]
    return translatedSwars 

    
def create_and_save(rawswars,m_duration=1,save_name='test_swars',base_freq=440,amplitude=32767,sample_rate=4410):
    # Combines all the waveforms and writes to file
    # By default, will generate one second per entry in list
    bol=notationreader(rawswars)
    print(bol)
    bol_length=len(bol)
    waveform=[]
    print(bol_length)
    for b in bol:
        if len(b)==1:
            waveform+=wf_specifier(swar2freq(b[0],base_freq),amplitude,sample_rate,m_duration)
        else:
            if len(b)==0:
                l=1
            else:
                l=len(b)
            sub_duration=1/float(l)
            for _ in b:
                waveform+=wf_specifier(swar2freq(_,base_freq),amplitude,sample_rate,sub_duration*float(m_duration))

    # Wave file configuration
    wavef = wave.open(save_name+'.wav','w')
    wavef.setnchannels(1) # mono
    wavef.setsampwidth(2) 
    wavef.setframerate(sample_rate)
    wavef.setnframes(int(bol_length * sample_rate))
    
    for w in waveform:
        data = struct.pack('<h', w)
        wavef.writeframesraw( data )
    wavef.close()

#Sargam='s,r,g,m,p,d,n,>s'
def convert(inf_p, outf_p, freq):
    swar_string=''
    with open(inf_p,'r') as infile:
        for line in infile.readlines():
            swar_string+=line.strip("\n")
    print("Input string processed as follows:")
    # print(SwarString)
    create_and_save(swar_string,save_name=outf_p,m_duration=0.5,base_freq=int(freq))
        
#owncomp=""">s,>sd,>s,>sd,>sd,pm,p,p,m,mr,m,mr,mr,s<d,s,s,rr,sm,r,r,pp,md,p,p,dd,p>s,d,d,>s>s,d>r,>s,>s,>r,>r>s,>r,>sd,>s,dp,d,pm,rm,pd,>s,dp,m,rm,s"""

#create_and_save(owncomp,MDuration=0.5,savename='owncomp',basefreq=1047)
