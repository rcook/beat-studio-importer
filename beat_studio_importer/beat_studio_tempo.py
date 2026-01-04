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

from beat_studio_importer.tempos import MidiTempo, Qpm, midi_tempo_to_qpm
from typing import Self


BEAT_STUDIO_TEMPO_MIN: int = 60
BEAT_STUDIO_TEMPO_MAX: int = 200


# What is the tempo measure in Beat Studio?
# We assume it's quarter notes per minute (QPM) for now
class BeatStudioTempo(int):
    def __new__(cls: type[Self], value: int) -> Self:
        if not (BEAT_STUDIO_TEMPO_MIN <= value <= BEAT_STUDIO_TEMPO_MAX):
            raise ValueError(f"Invalid Beat Studio velocity {value}")
        return super().__new__(cls, value)

    @classmethod
    def from_qpm(cls: type[Self], tempo: Qpm) -> Self:
        return cls(round(tempo))

    @classmethod
    def from_midi_tempo(cls: type[Self], tempo: MidiTempo) -> Self:
        return cls(round(midi_tempo_to_qpm(tempo)))
