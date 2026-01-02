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
from enum import Enum, auto, unique


# Names derived from General MIDI Drums Level 1 spec
# https://midi.org/general-midi-level-1
# This enum maps GM MIDI drum notes to the equivalent Beat Studio
# note names
@unique
class NoteName(Enum):
    # GM Key 35
    ACOUSTIC_BASS_DRUM = auto(), BeatStudioNoteName.KICK
    # GM Key 36
    BASS_DRUM_1 = auto(), BeatStudioNoteName.KICK
    # GM Key 38
    ACOUSTIC_SNARE = auto(), BeatStudioNoteName.SNARE
    # GM Key 42
    CLOSED_HI_HAT = auto(), BeatStudioNoteName.HI_HAT
    # GM Key 47
    LOW_MID_TOM = auto(), BeatStudioNoteName.MED_TOM
    # GM Key 48
    HI_MID_TOM = auto(), BeatStudioNoteName.HI_TOM
