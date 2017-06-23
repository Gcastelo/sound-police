import argparse
import audioop
import math
import pyaudio
import thread
import pygame


class Sensor(object):
    CHUNK_SIZE = 1024
    RATE = 48000
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    WIDTH = 2

    def __init__(self, threshold, duration, reset_after):
        self.threshold = threshold
        self.threshold_limit_seconds = duration
        self.reset_after = reset_after

        self.threshold_sample_size = (self.RATE / self.CHUNK_SIZE) * self.threshold_limit_seconds
        self.reset_sample_size = (self.RATE / self.CHUNK_SIZE) * self.reset_after

        self.reset_samples = 0
        self.threshold_samples = 0
        self.playing = False

    def detect(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(format=self.FORMAT,
                            channels=self.CHANNELS,
                            rate=self.RATE,
                            input=True,
                            frames_per_buffer=self.CHUNK_SIZE,
                            input_device_index=2,
                            output=False)
        print "* recording"

        while stream.is_active:
            data = stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
            rms = audioop.rms(data, 2)
            if rms == 0:
                continue
            dec = self._to_decibel(rms)
            print dec
            if dec >= self.threshold:
                if not self.playing:
                    if self.threshold_samples >= self.threshold_sample_size:
                        thread.start_new_thread(self._play_sound, ())
                    else:
                        self.threshold_samples += 1
            else:
                self.reset_samples += 1
                if self.reset_samples >= self.reset_sample_size:
                    self.threshold_samples = 0
                    self.reset_samples = 0
                    print 'RESETTING'

    def _play_sound(self):
        self.playing = True
        sound = pygame.mixer.Sound('alert.wav')
        sound.play(loops=0)

        self.threshold_samples = 0
        self.reset_samples = 0
        self.playing = False

    @staticmethod
    def _to_decibel(rms):
        return math.ceil(20 * math.log10(rms))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default=50, type=int, help='threshold value in dB')
    parser.add_argument('--ts', default=3, type=int, help='threshold duration in seconds')
    parser.add_argument('--rs', default=10, type=int, help='reset after how many seconds')
    args = parser.parse_args()

    print ('args')
    print (args)

    pygame.mixer.init()
    sensor = Sensor(args.db, args.ts, args.rs)
    sensor.detect()
