# beat-studio-importer

_Experimental_: Generate patterns compatible with [Beat Studio][beat-studio]
from Standard MIDI files

## Example usage

```bash
python \
    ./beat-studio-importer.py \
    import \
    samples/example-1.mid \
    --channel 10 \
    --region 2 \
    --quantum 16 \
    --tempo 100 \
    --repeat 1 \
    --add
```

Will produce output in the following format:

```text
["example-1 region 2" - 28 - 100 - 16 - 7/8]
CRASH     : ............................
CRASH2    : ............................
HI-HAT    : 5.5.5.5.5.5.5.5.5.5.5.......
HI-TOM    : ........................55..
KICK      : 5.....5.5...5.5.....5.......
LOW-TOM   : ............................
MED-TOM   : ..........................55
OPEN-HIHAT: ............................
RIDE      : ............................
SNARE     : ....5.............5...55....
```

It will also add this pattern to your `%LOCALAPPDATA%\Beat Studio\patterns.beat`
file if it is not already present.

All switches are optional and the script will choose sensible defaults if
possible.

## Caveat emptor

This script is highly experimental. I haven't tested its handling of
MIDI tempos terribly thoroughly, so expect this kind of thing to break.
[Beat Studio][beat-studio]'s pattern syntax will probably change over
time too. This program was tested against Beat Studio version
0.3.3-ALPHA-PRO.

## Type-check and install in dev mode

```bash
python -m pip install --upgrade pip
python -m pip install -e .[dev]
mypy .
basedpyright
pytest
```

## Specification

According to the comment at the top of `patterns.beat` from Beat Studio
0.3.3-ALPHA-PRO, the format of this file is as follows:

```
# MIDI Drum Patterns Collection
# Format: ["PATTERN_NAME" - LENGTH - TEMPO - NOTE_LENGTH - TIME_SIGNATURE] followed by drum lines
# Each line represents one drum type, each character represents one note beat
# Numbers 1-9 = velocity levels, . = rest
# Drums: CRASH, CRASH2, RIDE, HI-HAT, OPEN-HIHAT, KICK, SNARE, HI-TOM, MED-TOM, LOW-TOM
# Length can be 4-8192 beats, Tempo in BPM (60-200)
# Note Length: 16 (default), 32, 64, 8, 4, etc.
# Time Signature: 4/4 (default), 3/4, 6/8, 5/4, 7/8, etc.
```

## Licence

[MIT License](LICENSE)

[beat-studio]: https://beatstudio.io/
