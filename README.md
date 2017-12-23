The goal is to attempt to synthesize tones from a defined sequence of swars, while retaining as simple a notation as possible.

# Requirements

I had to install python3-pyaudio to get PyAudio to work.

On Fedora and similar:
`sudo dnf build-depx python3-pyaudio`

# Preliminaries

Each swar defines a note. A collection of swars sound melodic when they are destributed across beats, with one or more swars to a beat, also known as a matra. In this project, each beat is separated by a ','.

The seven basic swars (Sa,Re,Ga,Ma,Pa,Dha,Ni) are represented a (s,r,g,m,p,d,n). A swar on the immediate lower octave is represented by prefixing a '<', and that on the immediate higher octave with a '>'. Example, `<n,s,g,m,d,n,>s` start from the lower Ni and ends on the upper Sa.

The above seven swars are all shuddh. The non-shuddh swars are represented by suffixing any single character. I typically use '^'. So komal Re is 'r^'.

# Usage

Call the swar_synthesizer.convert() function with the path to the input file, and optionally the base frequency, which will define your scale. (Default=440Hz)

I have a main.py function that allows me to call the script from the command line as follows:

`python main.py -i "PATH/TO/INPUT"` 