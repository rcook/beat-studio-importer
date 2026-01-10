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

from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.pulse import Pulse
from beat_studio_importer.tempos import Bpm, MidiTempo
from dataclasses import dataclass
from functools import cached_property
from typing import NewType, override


Numerator = NewType("Numerator", int)


@dataclass(frozen=True)
class TimeSignature:
    numerator: Numerator
    denominator: NoteValue

    @override
    def __repr__(self) -> str:
        return f"{self.numerator}/{self.denominator.int_value}"

    # Reference: https://en.wikipedia.org/wiki/Time_signature
    @cached_property
    def pulse(self) -> Pulse:
        is_simple_metre = self.numerator in [1, 2, 3, 4]
        if is_simple_metre:
            return self.denominator.pulse

        is_compound_metre = self.numerator % 3 == 0
        if is_compound_metre:
            return self.denominator.pulse.compound()

        # Complex metre
        return self.denominator.pulse

    def ticks_per_bar(self, ticks_per_beat: int) -> int:
        n = 4 * ticks_per_beat * self.numerator
        q, r = divmod(n, self.denominator.int_value)
        if r != 0:
            raise ValueError(f"Invalid PPQN {ticks_per_beat}")
        return q

    # Tempo as beats (pulses) per minute
    def midi_tempo_to_bpm(self, tempo: MidiTempo) -> Bpm:
        return self.pulse.midi_tempo_to_bpm(tempo)
