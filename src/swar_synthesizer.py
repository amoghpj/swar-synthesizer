import wave
import math
import sys
import struct
import pyaudio

def swar2freq(swar,basefreq):
    F=0

    MAPPER={
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


    
    ALLOWEDINPUTS=['s','r','g','m','p','d','n','^','<','>']
    whichoctave=''
    whichswar=''
    
    if swar[0] in ALLOWEDINPUTS:
        if len(swar)==1:
            
            return MAPPER[swar]['shuddh']

        elif len(swar)==2:
            if swar[0] in ['<','>']:
                OCT=swar[0]
                NOTE=swar[1]
               
                return int(octavespecifier(OCT)*float(MAPPER[NOTE]['shuddh']))

            elif swar[0] in ['s','r','g','m','p','d','n']:
                NOTE=swar[0]
                return MAPPER[NOTE]['vakra']

        elif len(swar)==3:

            OCT=swar[0]
            NOTE=swar[1]
            SorV=swar[2]

            return int(octavespecifier(OCT)*float(MAPPER[NOTE]['vakra']))

    else:
        return MAPPER['0']
    
def octavespecifier(octave):
    
    loctave=0.5
    uoctave=2.0
    if octave=='<':
        return loctave
    elif octave=='>':
        return uoctave


def wf_specifier(freq,A,SR,D):
    # Defines waveform for a given duration and frequency
    wf=[]
    # 5% taper
    TAPER=0.00
    for i in range(int((1-TAPER)*D*float(SR))):
        wf.append(int(A*math.cos(freq*math.pi*float(i)/float(SR))))
    for i in range(int((TAPER)*D*float(SR))):
        wf.append(int(0))
    
    return wf
def play_soundfile(path):
    
    CHUNK = 100
    
    # if len(sys.argv) < 2:
    #     print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    #     sys.exit(-1)
    
    wf = wave.open(path, 'rb')
    
    p = pyaudio.PyAudio()
    
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    
    data = wf.readframes(CHUNK)
    
    while len(data)>0 :
        stream.write(data)
        data = wf.readframes(CHUNK)
    
    stream.stop_stream()
    stream.close()
    
    p.terminate()
    
def notationreader(swarstring):
    LOWERSCALEMODIFIER='<'
    UPPERSCALEMODIFIER='>'
    premodifiers=[LOWERSCALEMODIFIER,UPPERSCALEMODIFIER]
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

    
def create_and_save(rawswars,MDuration=1,savename='test_swars',basefreq=440,amplitude=32767,sampleRate=4410):
    # Combines all the waveforms and writes to file
    # By default, will generate one second per entry in list
    bol=notationreader(rawswars)
    print(bol)
    Length=len(bol)
    Waveform=[]
    print(len(bol))
    for B in bol:
        
        if len(B)==1:
            Waveform+=wf_specifier(swar2freq(B[0],basefreq),amplitude,sampleRate,MDuration)
        else:
            if len(B)==0:
                L=1
            else:
                L=len(B)
            subduration=1/float(L)
            for b in B:
                Waveform+=wf_specifier(swar2freq(b,basefreq),amplitude,sampleRate,subduration*float(MDuration))
        
    # Wave file configuration
    wavef = wave.open(savename+'.wav','w')
    wavef.setnchannels(1) # mono
    wavef.setsampwidth(2) 
    wavef.setframerate(sampleRate)
    wavef.setnframes(int(Length * sampleRate))
    
    for w in Waveform:
        data = struct.pack('<h', w)
        wavef.writeframesraw( data )
    wavef.close()

#Sargam='s,r,g,m,p,d,n,>s'
def convert(infP,outfP,freq):
    SwarString=''
    with open(infP,'r') as infile:
        for line in infile.readlines():
            SwarString+=line.strip("\n")
    print("Input string processed as follows:")
    # print(SwarString)
    create_and_save(SwarString,savename=outfP,MDuration=0.5,basefreq=int(freq))
        
#owncomp=""">s,>sd,>s,>sd,>sd,pm,p,p,m,mr,m,mr,mr,s<d,s,s,rr,sm,r,r,pp,md,p,p,dd,p>s,d,d,>s>s,d>r,>s,>s,>r,>r>s,>r,>sd,>s,dp,d,pm,rm,pd,>s,dp,m,rm,s"""

#create_and_save(owncomp,MDuration=0.5,savename='owncomp',basefreq=1047)
