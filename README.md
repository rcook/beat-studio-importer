# beat-studio-importer

_Experimental_: Generate patterns compatible with [Beat Studio][beat-studio]
from Standard MIDI files

## Example usage

```bash
python \
    ./beat-studio-importer.py \
    import \
    MyPattern.mid \
    --track 2 \
    --metadata-track 1 \
    --region 2 \
    --quantize 16
```

Will produce output in the following format:

```text
["MyPattern region 2" - 28 - 100 - 16 - 7/8]
CRASH     : ............................
CRASH2    : ............................
HI-HAT    : 7.7.7.7.7.7.7.7.7.7.7.......
HI-TOM    : ........................77..
KICK      : 7.....7.7...7.7.....7.......
LOW-TOM   : ............................
MED-TOM   : ..........................77
OPEN-HIHAT: ............................
RIDE      : ............................
SNARE     : ....7.............7...77....
```

## Caveat emptor

This script is highly experimental. I haven't tested its handling of
MIDI tempos terribly thoroughly, so expect this kind of thing to break.
[Beat Studio][beat-studio]'s pattern syntax will probably change over
time too. This program was tested against Beat Studio version
0.3.2-ALPHA-PRO.

## Type-check and install in dev mode

```bash
python -m pip install --upgrade pip
python -m pip install -e .[dev]
pytest
mypy .
basedpyright
```

## Licence

[MIT License](LICENSE)

[beat-studio]: https://beatstudio.io/
