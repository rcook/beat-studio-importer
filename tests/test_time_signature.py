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

from beat_studio_importer.misc import MidiTempo, Numerator
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.pulse import Pulse
from beat_studio_importer.time_signature import TimeSignature
from tests.util import is_close_tempo
import pytest


class TestTimeSignature:
    def test_three_four(self) -> None:
        time_signature = TimeSignature(Numerator(3), NoteValue.QUARTER)
        assert is_close_tempo(
            120,
            time_signature.midi_tempo_to_bpm(MidiTempo(500_000)))
        assert is_close_tempo(
            60,
            time_signature.midi_tempo_to_bpm(MidiTempo(1_000_000)))

    def test_four_four(self) -> None:
        time_signature = TimeSignature(Numerator(4), NoteValue.QUARTER)
        assert is_close_tempo(
            120,
            time_signature.midi_tempo_to_bpm(MidiTempo(500_000)))
        assert is_close_tempo(
            60,
            time_signature.midi_tempo_to_bpm(MidiTempo(1_000_000)))

    def test_seven_eight(self) -> None:
        time_signature = TimeSignature(Numerator(7), NoteValue.EIGHTH)
        assert is_close_tempo(
            240,
            time_signature.midi_tempo_to_bpm(MidiTempo(500_000)))
        assert is_close_tempo(
            120,
            time_signature.midi_tempo_to_bpm(MidiTempo(1_000_000)))

    def test_twelve_eight(self) -> None:
        time_signature = TimeSignature(Numerator(7), NoteValue.EIGHTH)
        assert is_close_tempo(
            240,
            time_signature.midi_tempo_to_bpm(MidiTempo(500_000)))
        assert is_close_tempo(
            120,
            time_signature.midi_tempo_to_bpm(MidiTempo(1_000_000)))

    # Reference: https://en.wikipedia.org/wiki/Time_signature
    @pytest.mark.parametrize("numerator, denominator, expected", [
        # Simple metre
        (1, NoteValue.WHOLE, Pulse.WHOLE),
        (1, NoteValue.SIXTEENTH, Pulse.SIXTEENTH),
        (2, NoteValue.HALF, Pulse.HALF),
        (2, NoteValue.EIGHTH, Pulse.EIGHTH),
        (3, NoteValue.WHOLE, Pulse.WHOLE),
        (3, NoteValue.QUARTER, Pulse.QUARTER),
        # Compound metre
        (6, NoteValue.EIGHTH, Pulse.DOTTED_QUARTER),
        (9, NoteValue.EIGHTH, Pulse.DOTTED_QUARTER),
        (12, NoteValue.EIGHTH, Pulse.DOTTED_QUARTER),
        (15, NoteValue.EIGHTH, Pulse.DOTTED_QUARTER),
        (6, NoteValue.SIXTEENTH, Pulse.DOTTED_EIGHTH),
        (9, NoteValue.SIXTEENTH, Pulse.DOTTED_EIGHTH),
        (12, NoteValue.SIXTEENTH, Pulse.DOTTED_EIGHTH),
        (15, NoteValue.SIXTEENTH, Pulse.DOTTED_EIGHTH),
        # Complex metre
        (5, NoteValue.QUARTER, Pulse.QUARTER),
        (8, NoteValue.EIGHTH, Pulse.EIGHTH),
        (7, NoteValue.SIXTEENTH, Pulse.SIXTEENTH)
    ])
    def test_pulse(self, numerator: Numerator, denominator: NoteValue, expected: Pulse) -> None:
        time_signature = TimeSignature(
            numerator=numerator,
            denominator=denominator)
        assert time_signature.pulse is expected
