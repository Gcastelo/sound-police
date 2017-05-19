"""Sound sensor: Triggers a sound when over a certain dB value"""

import wave
import audioop
import math
import thread
import argparse
import pyaudio

THRESHOLD_DB = None
THRESHOLD_LIMIT_SECS = None
RESET_AFTER_SECS = None
THRESHOLD_SAMPLESIZE = None
RESET_SAMPLESIZE = None

CHUNK_SIZE = 1024
RATE = 44100
FORMAT = pyaudio.paInt16
CHANNELS = 2
WIDTH = 2

_reset_samples = 0
_threshold_samples = 0
_playing = False
_p = pyaudio.PyAudio()


def parse_opts():
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("db", help="Decibel threshold", type=int)
    PARSER.add_argument("-ts", "--threshold-secs",
                        help="Threshold limit in secs", type=int)
    PARSER.add_argument("-rs", "--reset-secs", help="Reset after secs", type=int)

    ARGS = PARSER.parse_args()
    print ARGS

    global THRESHOLD_DB
    global THRESHOLD_LIMIT_SECS
    global RESET_AFTER_SECS
    global THRESHOLD_SAMPLESIZE
    global RESET_SAMPLESIZE

    THRESHOLD_DB = ARGS.db if ARGS.db else 50
    THRESHOLD_LIMIT_SECS = ARGS.threshold_secs if ARGS.threshold_secs else 3
    RESET_AFTER_SECS = ARGS.reset_secs if ARGS.reset_secs else 10
    THRESHOLD_SAMPLESIZE = (RATE / CHUNK_SIZE) * THRESHOLD_LIMIT_SECS
    RESET_SAMPLESIZE = (RATE / CHUNK_SIZE) * RESET_AFTER_SECS


def play_sound():
    global _playing
    global _threshold_samples
    global _reset_samples
    _playing = True
    wave_file = wave.open('alert.wav', 'rb')
    stream_wave = _p.open(format=_p.get_format_from_width(wave_file.getsampwidth()),
                          channels=wave_file.getnchannels(),
                          rate=wave_file.getframerate(),
                          output=True)
    data = wave_file.readframes(CHUNK_SIZE)
    while data != '':
        stream_wave.write(data)
        data = wave_file.readframes(CHUNK_SIZE)
    stream_wave.stop_stream()
    stream_wave.close()
    _threshold_samples = 0
    _reset_samples = 0
    _playing = False


def to_decibel(rms):
    return math.ceil(20 * math.log10(rms))


def main():
    parse_opts()
    print "THRESHOLD_DB: ", THRESHOLD_DB
    print "THRESHOLD_LIMIT_SECS: ", THRESHOLD_LIMIT_SECS
    print "RESET_AFTER_SECS: ", RESET_AFTER_SECS
    print "THRESHOLD_SAMPLESIZE: ", THRESHOLD_SAMPLESIZE
    print "RESET_SAMPLESIZE: ", RESET_SAMPLESIZE
    global _reset_samples
    global _threshold_samples

    stream = _p.open(format=FORMAT,
                     channels=CHANNELS,
                     rate=RATE,
                     input=True,
                     frames_per_buffer=CHUNK_SIZE)

    print "* recording"

    while stream.is_active:
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        rms = audioop.rms(data, 2)
        if rms == 0:
            continue
        dec = to_decibel(rms)
        # print dec
        if dec >= THRESHOLD_DB:
            if not _playing:
                if _threshold_samples >= THRESHOLD_SAMPLESIZE:
                    thread.start_new_thread(play_sound, ())
                else:
                    _threshold_samples += 1
            print _threshold_samples
        else:
            _reset_samples += 1
            if _reset_samples >= RESET_SAMPLESIZE:
                _threshold_samples = 0
                _reset_samples = 0
                print 'RESETTING'


if __name__ == "__main__":
    main()
