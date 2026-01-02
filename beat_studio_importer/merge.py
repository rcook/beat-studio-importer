# Copyright (c) 2026 Richard Cook
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

from beat_studio_importer.beat_studio_pattern import BeatStudioPattern
from os import getenv
from pathlib import Path


def default_patterns_beat_path() -> Path:
    s = getenv("LOCALAPPDATA")
    if s is None:
        raise RuntimeError("LOCALAPPDATA is not defined")

    path = Path(s).resolve() / "Beat Studio" / "patterns.beat"
    if not path.is_file():
        raise RuntimeError(f"Configuration file {path} not found")

    return path


def do_merge() -> None:
    new_pattern = BeatStudioPattern.parse("""[\"30-Day Odd Time Signatures region 2\" - 28 - 100 - 16 - 7/8]
        CRASH: ............................
        CRASH2: ............................
        HI-HAT: 7.7.7.7.7.7.7.7.7.7.7.......
        HI-TOM: ........................77..
        KICK: 7.....7.7...7.7.....7.......
        LOW-TOM: ............................
        MED-TOM: ..........................77
        OPEN-HIHAT: ............................
        RIDE: ............................
        SNARE: ....7.............7...77....
        """)
    path = default_patterns_beat_path()
    patterns = BeatStudioPattern.load(path)
    for pattern in patterns:
        print(pattern.name)
        if new_pattern == pattern:
            print("Same as new pattern")
