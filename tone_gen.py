import math

def _linspace(a, b, n=100):
    """Function emulating Matlab/numpy's linspace, which generates a
       linearly-spaced list of 'n' numbers from 'a' to 'b'."""
    if n < 2:
        return b
    diff = (float(b) - a)/(n - 1)
    return [diff * i + a  for i in range(n)]

def generate_tone(freq_hz, length_seconds, rate=16000, amplitude=1.0):
    """Generates a 16-bit tone of 'length' seconds at the given
       frequency, amplitude, and rate."""
    time_series = _linspace(0, length_seconds, int(length_seconds*rate) + 1)[:-1]
    data = []
    for t in time_series:
        data.append(int(math.sin(2 * math.pi * freq_hz * t) * amplitude * 32767))
    return data

def generate_one_sine_cycle(freq_hz, rate=16000, amplitude=1.0):
    one_cycle_length = 1 / float(freq_hz)
    return generate_tone(freq_hz, one_cycle_length, rate=rate, amplitude=amplitude)

if __name__ == "__main__":
    _10ms_tone = generate_tone(1000, 0.01, amplitude=1.0)
    sine_cycle_data = generate_one_sine_cycle(1000, amplitude=1.0)
    print _10ms_tone == sine_cycle_data * int(0.01 / (1.0 / 1000))

