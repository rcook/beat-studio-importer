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


from fractions import Fraction
from typing import NewType


# Various different measures of tempo

# Tempo as indicated by Beat Studio (quarter notes per minute?)
BeatStudioTempo = NewType("BeatStudioTempo", int)

# Beats (pulses) per minute
# Stored as a fraction to maintain accuracy
Bpm = NewType("Bpm", Fraction)

# MIDI tempo in microseconds per quarter note
MidiTempo = NewType("MidiTempo", int)

# Quarter notes per minute
# Stored as a fraction to maintain accuracy
Qpm = NewType("Qpm", Fraction)


def midi_tempo_to_qpm(tempo: MidiTempo) -> Qpm:
    """
    Convert MIDI tempo to QPM tempo. Conversion to BPM tempo
    requires knowledge of the song's pulse. See Pulse class.

    :param tempo: MIDI tempo in microseconds per quarter note
    :type tempo: int
    :return: Tempo in quarter notes per minute
    :rtype: Fraction
    """
    return Qpm(Fraction(60_000_000, tempo))


# Tempo as indicated by Beat Studio (quarter notes per minute?)
def midi_tempo_to_beat_studio_tempo(tempo: MidiTempo) -> BeatStudioTempo:
    return BeatStudioTempo(round(midi_tempo_to_qpm(tempo)))
