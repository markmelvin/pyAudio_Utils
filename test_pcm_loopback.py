import pyaudio
import time
import math
import wave

from tone_gen import *

def _list_to_byte_array(l):
    ints = [[w & 0xFF, (w & 0xFF00) >> 8] for w in l]
    return str(bytearray([a for a in ints for a in a]))

def get_USBStreamer_devices(audio_ss):
    """Returns a tuple of the USBStreamer playback and recording device
       info dicts (playback, recording).
       If they do not exist, a RuntimeError is raised."""
    playback = None
    recording = None
    for i in range(audio_ss.get_device_count()):
        info = audio_ss.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0 and \
                    info['name'].startswith('Line (USBStreamer'):
            recording = info
        elif info['maxOutputChannels'] > 0 and \
                    info['name'].startswith('Speakers (USBStreamer'):
            playback = info

    if playback is None or recording is None:
        raise RuntimeError('Failed to find USBStreamer device.')

    return (playback, recording)

if __name__ == "__main__":
    AUDIO = None
    TONE_HZ = 2000
    TONE_RATE = 16000
    TONE_LENGTH_SECONDS = 5.0
    TONE_AMPLITUDE = 0.8
    TOTAL_FRAMES = TONE_RATE * TONE_LENGTH_SECONDS

    try:

        AUDIO = pyaudio.PyAudio()
        pcmout, pcmin = get_USBStreamer_devices(AUDIO)

        sine_data = generate_one_sine_cycle(TONE_HZ, TONE_RATE, TONE_AMPLITUDE)
        # The default frame count (samples per buffer) is 1024.  We want an
        # even number of sine cycles per buffer, so let's choose a value
        # close to 1024, but divisible by len(sine_data)
        sine_cycles_per_buffer = int(math.floor(1024 / len(sine_data)))
        sine_byte_data = _list_to_byte_array(sine_data * sine_cycles_per_buffer)
        framesPerBuffer = sine_cycles_per_buffer * len(sine_data)
        _gFramesLeft = TOTAL_FRAMES

        recorded_frames = []
        def audio_callback(in_data, frame_count, time_info, status):
            global _gFramesLeft
            _gFramesLeft -= frame_count
            recorded_frames.append(in_data)
            return (sine_byte_data, pyaudio.paContinue)

        stream = AUDIO.open(format=pyaudio.paInt16,
                        input_device_index = pcmin['index'],
                        output_device_index = pcmout['index'],
                        channels=1,
                        frames_per_buffer=framesPerBuffer,
                        rate=TONE_RATE,
                        input=True,
                        output=True,
                        stream_callback=audio_callback)
        stream.start_stream()

        while stream.is_active() and _gFramesLeft > 0:
            time.sleep(0.01)
        stream.stop_stream()
        stream.close()

        wf = wave.open('recorded_sine.wav', 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(AUDIO.get_sample_size(pyaudio.paInt16))
        wf.setframerate(TONE_RATE)
        wf.writeframes(b''.join(recorded_frames))
        wf.close()
    finally:
        if AUDIO is not None:
            AUDIO.terminate()
