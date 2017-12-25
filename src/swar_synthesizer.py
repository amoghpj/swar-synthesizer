import wave
import math
import sys
import struct
import pyaudio

def swar2freq(swar,basefreq):
    """
    Contains a dictionary (mapper) that stores relates the swar to 
    its defined frequency. I have used the Pythagorean ratios
    to define the relative frequencies based a fixed basefreq
    variable that is set to 440 Hz by default, but can be speci-
    fied by the User.
    This function interprets the octave specifier which halves 
    or doubles the value of the defined note to shift down or up
    on the scale.
    """
    basefreq_float=float(basefreq) # Perform type conversion once
    
    mapper={
        's':{
            'shuddh':basefreq,
            'vakra':basefreq, # Error handling mechanism.
            },
        'r':{
            'shuddh':int(1.125*basefreq_float),
            'vakra':int(1.058*basefreq_float)
            },
        'g':{
            'shuddh':int(1.266*basefreq_float),
            'vakra':int(1.188*basefreq_float)
            },
        'm':{
            'shuddh':int(1.333*basefreq_float),
            'vakra':int(1.412*basefreq_float),
            },
        'p':{
            'shuddh':int(1.5*basefreq_float),
            'vakra':int(1.5*basefreq_float), # Error handling mechanism
            },
        'd':{
            'shuddh':int(1.688*basefreq_float),
            'vakra':int(1.586*basefreq_float),
            },
        'n':{
            'shuddh':int(1.898*basefreq_float),
            'vakra':int(1.78*basefreq_float),
            },
        '0':0,
        
    }

    """
    For any other input, including captialization, this function
    will specify 0 Hz. Might not be ideal.
    """
    allowed_inputs=['s','r','g','m','p','d','n','^','<','>']

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
    """
    Helper function for swar2freq().
    This can be later modified to interpret further lower and 
    higher octaves if the need arises, and not just the 
    adjacent octaves.
    """
    loctave=0.5
    uoctave=2.0
    if octave=='<':
        return loctave
    elif octave=='>':
        return uoctave


def wf_specifier(freq,a,sr,d):

    """
    Function which takes the following waveform paramters
    and generates it explicitly.
    1. Frequency - freq
    2. Amplitude - a
    3. Sample Rate - sr
    4. Duration of each beat or matra - d
    
    This isn't ideal, and the waveform should be user-defined
    input. 

    I introduced the variable taper to play around with the 
    transition from one note to the other. 0% taper makes 
    the transition abrupt, while 5% makes it sound more discrete.
    In the future, I would like to define a function that smoothes
    out each transition to give a more analog feel.
    """
    # Defines waveform for a given duration and frequency
    
    wf=[]
    taper=0.00 # A 5% taper makes each note sound distinct.
    for i in range(int((1.0-taper)*d*float(sr))):
        wf.append(int(a*math.cos(freq*math.pi*float(i)/float(sr))))
    for i in range(int((taper)*d*float(sr))):
        wf.append(int(0))

    return wf

def play_soundfile(path):
    """
    This code is lifted directly from the PyAudio site.
    It seemes to be truncating the final beat??
    Ask @reckoner165 about how to fix this problem.
    """
    chunk = 100 # Does this affect performance?
    
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
    """
    Function to interpret the swar string.
    Checks to see if a prefix or suffix exists for a 
    given note/swar. Parses the input string and represents
    each beat as a list of notes contained in the beat.
    Note: Each beat is specified by a comma (',') in the input.
    """
    lower_scale_modifier='<'
    upper_scale_modifier='>'
    premodifiers=[lower_scale_modifier,upper_scale_modifier]
    postmodifiers=['^'] 
    translatedSwars=[]
    all_swars=[]
    single_swar=''
    beat=0
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
        beat+=1
    print("Number of beats=",beat)
    return translatedSwars 

    
def create_and_save(rawswars,m_duration=1,save_name='test_swars',base_freq=440,amplitude=32767,sample_rate=4410):
    """
    Function that takes a single input string and 
    converts it to list beats. This is accomplished
    by calling notationreader().
    Next, it calls wf_specifier() to generate the waveform,
    according to the frequency specified by swar2freq().
    Finally, it writes the .wav file using the wave module.
    """
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
    print("Writing to ", save_name+".wav")
    wavef = wave.open(save_name+'.wav','w')
    wavef.setnchannels(1) # mono
    wavef.setsampwidth(2) 
    wavef.setframerate(sample_rate)
    wavef.setnframes(int(bol_length * sample_rate))
    
    for w in waveform:
        data = struct.pack('<h', w)
        wavef.writeframesraw( data )
    wavef.close()

def convert(inf_p, outf_p, freq):
    """
    Reads an input text file, strips newlines,
    and calls create_and_save().
    Can skip this function is input is defined 
    as a single string.

    This also opens up possbilities for using 
    streams, where a continuous input of swars
    are converted played in real time.
    """
    swar_string=''
    with open(inf_p,'r') as infile:
        for line in infile.readlines():
            swar_string+=line.strip("\n")
    print("Input string processed as follows:")
    # print(SwarString)
    print("Will write to",outf_p)
    create_and_save(swar_string,save_name=outf_p,m_duration=0.5,base_freq=int(freq))
        

