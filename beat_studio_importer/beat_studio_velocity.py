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

from beat_studio_importer.misc import MidiVelocity
from beat_studio_importer.open_interval import OpenInterval
from typing import Self


MIDI_VELOCITY_RANGE: OpenInterval = OpenInterval(0, 127)
BEAT_STUDIO_VELOCITY_RANGE: OpenInterval = OpenInterval(1, 9)


class BeatStudioVelocity(int):
    def __new__(cls: type[Self], value: int) -> Self:
        if value not in BEAT_STUDIO_VELOCITY_RANGE:
            raise ValueError(f"Invalid Beat Studio velocity {value}")
        return super().__new__(cls, value)

    @classmethod
    def from_midi_velocity(cls: type[Self], velocity: MidiVelocity) -> Self:
        #  return cls(MIDI_VELOCITY_RANGE.downscale(BEAT_STUDIO_VELOCITY_RANGE, velocity))

        # Beat Studio seems to explicitly reject MIDI velocity of 0 and
        # treats this as a no-hit instead, so don't attempt to convert
        # values outside this range
        if not (1 <= velocity <= 127):
            raise ValueError(
                f"MIDI velocity {velocity} is outside range 1-127")

        # It seems that Beat Studio downscales based on a ratio of 14:1
        return cls(min((velocity - 1) // 14 + 1, 9))
