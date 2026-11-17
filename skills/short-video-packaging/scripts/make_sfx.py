#!/usr/bin/env python3
"""Generate small, original UI sound starters; use an editor for cue timing and mix."""
import argparse
import math
import random
import struct
import wave
from pathlib import Path

RATE = 48000

def write(output, name, samples):
    with wave.open(str(output / name), 'wb') as file:
        file.setparams((1, 2, RATE, 0, 'NONE', 'not compressed'))
        file.writeframes(b''.join(struct.pack('<h', int(max(-.95, min(.95, v)) * 32767)) for v in samples))

def click(seed, duration, body, freq):
    rng = random.Random(seed)
    result = []
    for i in range(int(duration * RATE)):
        t = i / RATE
        noise = rng.uniform(-1, 1) * math.exp(-t * 105)
        tone = math.sin(2 * math.pi * freq * t) * math.exp(-t * 68)
        result.append(.33 * noise + body * tone)
    return result

def generate(output):
    output.mkdir(parents=True, exist_ok=True)
    write(output, 'mouse-click.wav', click(11, .12, .18, 1250))
    rng = random.Random(83)
    state = 0.0
    whoosh = []
    for i in range(int(.38 * RATE)):
        t = i / RATE
        state += .14 * (rng.uniform(-1, 1) - state)
        envelope = math.sin(math.pi * t / .38) ** 1.5
        whoosh.append(.55 * state * envelope)
    write(output, 'zoom-whoosh.wav', whoosh)
    print('Generated mouse-click.wav and zoom-whoosh.wav in', output)


def main(default_output=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path,
                        default=default_output or Path(__file__).resolve().parents[1] / 'assets')
    generate(parser.parse_args().output_dir)


if __name__ == '__main__':
    main()
