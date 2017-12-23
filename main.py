import os
import sys
PATH=os.path.abspath("./")
sys.path.append(PATH+"/swar-synthesizer/src/")
#print(sys.path)
import src.swar_synthesizer as synth
from optparse import OptionParser

parser=OptionParser()

parser.add_option('-i','--infile',dest='infilename',metavar='I')
#parser.add_option('-o','--outfile',dest='outfilename',metavar='O')
parser.add_option('-f','--basefreq',dest='basefreq')


(options,args)=parser.parse_args()
outfilename=options.infilename.split('.')[0]
synth.convert(options.infilename,outfilename,options.basefreq)
# synth.play_soundfile(options.outfilename+'.wav')
