"""Sound sensor: Triggers a sound when over a certain dB value"""

import wave
import pyaudio
import audioop
import math
import thread
import sys

if len(sys.argv) < 2:
    print("Triggers a sound over a dB threshold.\n\nUsage: %s <dB>" %
          sys.argv[0])
    sys.exit(-1)

THRESHOLD_DB = int(sys.argv[1])
THRESHOLD_LIMIT_SECS = 3
RESET_AFTER_SECS = 10

CHUNK = 1024
RATE = 44100

RESET_SAMPLES = 0
THRESHOLD_SAMPLES = 0

THRESHOLD_SAMPLESIZE = (RATE / CHUNK) * THRESHOLD_LIMIT_SECS
RESET_SAMPLESIZE = (RATE / CHUNK) * RESET_AFTER_SECS

FORMAT = pyaudio.paInt16
CHANNELS = 2
WIDTH = 2
playing = False
p = pyaudio.PyAudio()

print THRESHOLD_SAMPLESIZE
print RESET_SAMPLESIZE


def play_sound():
    global playing
    global THRESHOLD_SAMPLES
    global RESET_SAMPLES
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
    THRESHOLD_SAMPLES = 0
    RESET_SAMPLES = 0
    playing = False


def to_decibel(rms):
    return math.ceil(20 * math.log10(rms))

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
    if dec >= THRESHOLD_DB:
        if not playing:
            if THRESHOLD_SAMPLES >= THRESHOLD_SAMPLESIZE:
                thread.start_new_thread(play_sound, ())
            else:
                THRESHOLD_SAMPLES += 1
        print THRESHOLD_SAMPLES
    else:
        RESET_SAMPLES += 1
        if RESET_SAMPLES >= RESET_SAMPLESIZE:
            THRESHOLD_SAMPLES = 0
            RESET_SAMPLES = 0
            print 'RESETTING'
