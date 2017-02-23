"""Sound sensor: Triggers a sound when over a certain dB value"""

import wave
import pyaudio
import audioop
import math
import thread
import sys

if len(sys.argv) < 2:
    print("Triggers a sound over a dB threshold.\n\nUsage: %s <dB>" % sys.argv[0])
    sys.exit(-1)

THRESHOLD = int(sys.argv[1])
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44000
RECORD_SECONDS = 10
WIDTH = 2

playing = False
p = pyaudio.PyAudio()

def play_sound():
    global playing
    playing = True
    CHUNK_WAV = 1024
    wf = wave.open('alert.wav', 'rb')
    streamWave = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(CHUNK)
    while data != '':
        streamWave.write(data)
        data = wf.readframes(CHUNK)
    streamWave.stop_stream()
    streamWave.close()
    playing = False

def to_decibel( rms ):
    return 20 * math.log10(rms)

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print "* recording"

frames = []
while stream.is_active:
    data = stream.read(CHUNK, exception_on_overflow=False)
    rms = audioop.rms(data, 2)
    if rms == 0:
        continue
    dec = to_decibel(rms)
    #print dec
    #print THRESHOLD
    #print playing
    if dec >= THRESHOLD and not playing:
        thread.start_new_thread(play_sound, ())
