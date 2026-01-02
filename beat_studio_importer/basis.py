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

from beat_studio_importer.util import midi_tempo_to_qpm
from enum import Enum, auto, unique


@unique
class Basis(Enum):
    SIXTEENTH = auto(), 0.25, "sixteenth"
    EIGHTH = auto(), 0.5, "eighth"
    DOTTED_EIGHTH = auto(), 0.7, "dotted eight"
    QUARTER = auto(), 1.0, "quarter"
    DOTTED_QUARTER = auto(), 1.5, "dotted quarter"
    HALF = auto(), 2.0, "half"
    WHOLE = auto(), 4.0, "whole"

    # Tempo as basis beats per minute
    def midi_tempo_to_bpm(self, tempo: int) -> float:
        qpm = midi_tempo_to_qpm(tempo)
        multiplier = self.value[1]
        return qpm / multiplier
