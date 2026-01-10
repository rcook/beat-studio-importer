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

from beat_studio_importer.tempos import Bpm, MidiTempo, midi_tempo_to_qpm
from enum import Enum, auto, unique
from fractions import Fraction
from typing import Literal, overload


# https://music.stackexchange.com/questions/44197/how-to-convert-a-dotted-quarter-note-tempo-to-bpm
@unique
class Pulse(Enum):
    SIXTY_FOURTH = auto(), Fraction(1, 16), "64th note"
    DOTTED_SIXTY_FOURTH = auto(), Fraction(3, 32), "dotted 32nd note"
    THIRTY_SECOND = auto(), Fraction(1, 8), "32nd note"
    DOTTED_THIRTY_SECOND = auto(), Fraction(3, 16), "dotted 32nd note"
    SIXTEENTH = auto(), Fraction(1, 4), "16th note"
    DOTTED_SIXTEENTH = auto(), Fraction(3, 8), "dotted 16th note"
    EIGHTH = auto(), Fraction(1, 2), "8th note"
    DOTTED_EIGHTH = auto(), Fraction(3, 4), "dotted 8th note"
    QUARTER = auto(), Fraction(1), "quarter note"
    DOTTED_QUARTER = auto(), Fraction(3, 2), "dotted quarter note"
    HALF = auto(), Fraction(2), "half-note"
    DOTTED_HALF = auto(), Fraction(3, 1), "dotted half-note"
    WHOLE = auto(), Fraction(4), "whole note"
    DOTTED_WHOLE = auto(), Fraction(6, 1), "dotted whole note"

    @overload
    @staticmethod
    def from_multiplier(value: Fraction) -> "Pulse":
        ...

    @overload
    @staticmethod
    def from_multiplier(value: Fraction, allow_fraction: Literal[False]) -> "Pulse":
        ...

    @overload
    @staticmethod
    def from_multiplier(value: Fraction, allow_fraction: Literal[True]) -> "Pulse | Fraction":
        ...

    @overload
    @staticmethod
    def from_multiplier(value: Fraction, allow_fraction: bool) -> "Pulse | Fraction":
        ...

    @staticmethod
    def from_multiplier(value: Fraction, allow_fraction: bool = False) -> "Pulse | Fraction":
        for member in Pulse:
            if member.multiplier == value:
                return member
        if allow_fraction:
            return value
        raise NotImplementedError(f"Unsupported fraction {value}")

    # Tempo as beats (pulses) per minute
    def midi_tempo_to_bpm(self, tempo: MidiTempo) -> Bpm:
        qpm = midi_tempo_to_qpm(tempo)
        return Bpm(qpm / self.multiplier)

    @property
    def multiplier(self) -> Fraction: return self.value[1]

    @property
    def display(self) -> str: return self.value[2]

    @overload
    def dotted(self) -> "Pulse":
        ...

    @overload
    def dotted(self, allow_fraction: Literal[False]) -> "Pulse":
        ...

    @overload
    def dotted(self, allow_fraction: Literal[True]) -> "Pulse | Fraction":
        ...

    @overload
    def dotted(self, allow_fraction: bool) -> "Pulse | Fraction":
        ...

    def dotted(self, allow_fraction: bool = False) -> "Pulse | Fraction":
        return self.__class__.from_multiplier(Fraction(3, 2) * self.multiplier, allow_fraction=allow_fraction)

    @overload
    def compound(self) -> "Pulse":
        ...

    @overload
    def compound(self, allow_fraction: Literal[False]) -> "Pulse":
        ...

    @overload
    def compound(self, allow_fraction: Literal[True]) -> "Pulse | Fraction":
        ...

    @overload
    def compound(self, allow_fraction: bool) -> "Pulse | Fraction":
        ...

    def compound(self, allow_fraction: bool = False) -> "Pulse | Fraction":
        return self.__class__.from_multiplier(Fraction(3, 1) * self.multiplier, allow_fraction=allow_fraction)
