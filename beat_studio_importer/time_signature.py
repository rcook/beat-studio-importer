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

# pyright: reportAttributeAccessIssue=false
# pyright: reportUnknownVariableType=false

from beat_studio_importer.basis import Basis
from beat_studio_importer.note_value import NoteValue
from dataclasses import dataclass
from fractions import Fraction
from functools import cached_property
from mido import MetaMessage
from typing import TypeVar, cast, override


DEFAULT_CLOCKS_PER_CLICK: int = 24
DEFAULT_NOTATED_32ND_NOTES_PER_BEAT: int = 8


T = TypeVar("T", bound="TimeSignature")


@dataclass(frozen=True)
class TimeSignature:
    numerator: int
    denominator: NoteValue
    clocks_per_click: int = DEFAULT_CLOCKS_PER_CLICK
    notated_32nd_notes_per_beat: int = DEFAULT_NOTATED_32ND_NOTES_PER_BEAT

    @classmethod
    def from_midi_message(cls: type[T], message: MetaMessage) -> T:
        if cast(str, message.type) != "time_signature":
            raise ValueError(f"Invalid MIDI time signature message {message}")

        numerator = cast(int, message.numerator)
        if numerator < 1:
            raise ValueError(f"Invalid numerator {numerator}")

        denominator = NoteValue.from_int(
            cast(int, message.denominator))

        # What do I do if this isn't 24?
        clocks_per_tick = cast(int, message.clocks_per_click)
        assert clocks_per_tick == DEFAULT_CLOCKS_PER_CLICK

        # What do I do if this isn't 8?
        notated_32nd_notes_per_beat = cast(
            int,
            message.notated_32nd_notes_per_beat)
        assert notated_32nd_notes_per_beat == DEFAULT_NOTATED_32ND_NOTES_PER_BEAT

        return cls(
            numerator=numerator,
            denominator=denominator,
            clocks_per_click=clocks_per_tick,
            notated_32nd_notes_per_beat=notated_32nd_notes_per_beat)

    @override
    def __repr__(self) -> str:
        return f"{self.numerator}/{self.denominator.value[0]}"

    # Reference: https://en.wikipedia.org/wiki/Time_signature
    @cached_property
    def basis(self) -> Basis:
        is_simple_metre = self.numerator in [1, 2, 3, 4]
        if is_simple_metre:
            return self.denominator.value[1]

        is_compound_metre = self.numerator % 3 == 0
        if is_compound_metre:
            match self.denominator:
                case NoteValue.EIGHTH: return Basis.DOTTED_QUARTER
                case NoteValue.SIXTEENTH: return Basis.DOTTED_EIGHTH
                case _: raise NotImplementedError(f"Unimplemented time signature {self}")

        # Complex metre
        return self.denominator.value[1]

    def ticks_per_bar(self, ticks_per_beat: int) -> int:
        n = 4 * ticks_per_beat * self.numerator
        q, r = divmod(n, self.denominator.value[0])
        if r != 0:
            raise ValueError(f"Invalid PPQN {ticks_per_beat}")
        return q

    # Tempo as basis beats per minute
    def midi_tempo_to_bpm(self, tempo: int) -> Fraction:
        return self.basis.midi_tempo_to_bpm(tempo)


DEFAULT_TIME_SIGNATURE: TimeSignature = TimeSignature(
    numerator=4,
    denominator=NoteValue.QUARTER)
