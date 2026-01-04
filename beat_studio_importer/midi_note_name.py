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

from beat_studio_importer.beat_studio_note_name import BeatStudioNoteName
from beat_studio_importer.misc import MidiNote
from enum import Enum, auto, unique


# Names derived from General MIDI Drums Level 1 spec
# https://midi.org/general-midi-level-1
# This enum maps GM MIDI drum notes to the equivalent Beat Studio
# note names
@unique
class MidiNoteName(Enum):
    ACOUSTIC_BASS_DRUM = \
        auto(), "acoustic_bass_drum", MidiNote(35), BeatStudioNoteName.KICK
    BASS_DRUM_1 = auto(), "bass_drum_1", MidiNote(36), BeatStudioNoteName.KICK
    SIDE_STICK = auto(), "side_stick", MidiNote(37), BeatStudioNoteName.SNARE
    ACOUSTIC_SNARE = auto(), "acoustic_snare", MidiNote(38), BeatStudioNoteName.SNARE
    # TBD: 39, 40 omitted
    LOW_FLOOR_TOM = auto(), "low_floor_tom", MidiNote(41), BeatStudioNoteName.LOW_TOM
    CLOSED_HI_HAT = auto(), "closed_hi_hat", MidiNote(42), BeatStudioNoteName.HI_HAT
    HIGH_FLOOR_TOM = auto(), "high_floor_tom", MidiNote(43), BeatStudioNoteName.LOW_TOM
    # TBD: 44, 45 omitted
    OPEN_HI_HAT = auto(), "open_hi_hat", MidiNote(46), BeatStudioNoteName.OPEN_HIHAT
    LOW_MID_TOM = auto(), "low_mid_tom", MidiNote(47), BeatStudioNoteName.MED_TOM
    HI_MID_TOM = auto(), "hi_mid_tom", MidiNote(48), BeatStudioNoteName.HI_TOM
    CRASH_CYMBAL_1 = auto(), "crash_cymbal_1", MidiNote(49), BeatStudioNoteName.CRASH
    HIGH_TOM = auto(), "high_tom", MidiNote(50), BeatStudioNoteName.HI_TOM
    RIDE_CYMBAL_1 = auto(), "ride_cymbal_1", MidiNote(51), BeatStudioNoteName.RIDE
    # TBD: 52, 53, 54, 55, 56, 57 omitted
    CRASH_CYMBAL_2 = auto(), "crash_cymbal_2", MidiNote(57), BeatStudioNoteName.CRASH2
    # TBD: 58 etc. omitted

    @staticmethod
    def parse(s: str) -> "MidiNoteName":
        for member in MidiNoteName:
            if member.display == s:
                return member
        raise ValueError(f"Invalid General MIDI drum note name {s}")

    @property
    def display(self) -> str: return self.value[1]

    @property
    def midi_note(self) -> MidiNote: return self.value[2]

    @property
    def beat_studio_note_name(self) -> BeatStudioNoteName: return self.value[3]
