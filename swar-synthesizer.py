def swar2freq(swar,basefreq):
    F=0
    MAPPER={
        's':{
            '1':basefreq,
            '2':int(0.5*basefreq),
            '3':2*basefreq
            },
        'r':{
            '1':int(1.125*float(basefreq)),
            '2':int(0.5*1.125*float(basefreq)),
            '3':int(2.0*1.125*float(basefreq))
            },
        'g':{
            '1':int(1.266*float(basefreq)),
            '2':int(0.5*1.266*float(basefreq)),
            '3':int(2.0*1.266*float(basefreq))
            },
        'm':{
            '1':int(1.333*float(basefreq)),
            '2':int(0.5*1.333*float(basefreq)),
            '3':int(2.0*1.333*float(basefreq))
            },
        'p':{
            '1':int(1.5*float(basefreq)),
            '2':int(0.5*1.5*float(basefreq)),
            '3':int(2.0*1.5*float(basefreq))
            },
        'd':{
            '1':int(1.688*float(basefreq)),
            '2':int(0.5*1.688*float(basefreq)),
            '3':int(2.0*1.688*float(basefreq))
            },
        'n':{
            '1':int(1.898*float(basefreq)),
            '2':int(0.5*1.898*float(basefreq)),
            '3':int(2.0*1.898*float(basefreq))
            },
        '0':0,
        
    }
    ALLOWEDINPUTS=['s','r','g','m','p','d','n','<','>','0']
    if swar[0] in ALLOWEDINPUTS:
        if len(swar)==1:
            return MAPPER[swar]['1']
        else:
            PRE=swar[0]
            NOTE=swar[1]
            if PRE=='<':
                SELECT='2'
            elif PRE=='>':
                SELECT='3'

            return MAPPER[NOTE][SELECT]
    else:
        return MAPPER['0']
    

def wf_specifier(freq,A,SR,D):
    # Defines waveform for a given duration and frequency
    wf=[]
    # 5% taper
    TAPER=0.05
    for i in range(int((1-TAPER)*D*float(SR))):
        wf.append(int(A*math.cos(freq*math.pi*float(i)/float(SR))))
    for i in range(int((TAPER)*D*float(SR))):
        wf.append(int(0))
    
    return wf
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
    Length=len(bol)
    Waveform=[]
    
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

owncomp=""">s,>sd,>s,>sd,>sd,pm,p,p,m,mr,m,mr,mr,s<d,s,s,rr,sm,r,r,pp,md,p,p,dd,p>s,d,d,>s>s,d>r,>s,>s,>r,>r>s,>r,>sd,>s,dp,d,pm,rm,pd,>s,dp,m,rm,s"""

create_and_save(owncomp,MDuration=0.5,savename='owncomp',basefreq=1047)
