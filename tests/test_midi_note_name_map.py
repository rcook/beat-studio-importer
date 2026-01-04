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
from beat_studio_importer.midi_note_name import MidiNoteName
from beat_studio_importer.midi_note_name_map import DEFAULT_MIDI_NOTE_NAME_MAP
from beat_studio_importer.misc import MidiNote


class TestMidiNoteNameMap:
    def test_basics(self) -> None:
        note_name = DEFAULT_MIDI_NOTE_NAME_MAP[MidiNote(48)]
        assert note_name is MidiNoteName.HI_MID_TOM
        assert note_name.display == "hi_mid_tom"
        assert note_name.midi_note == MidiNote(48)
        assert note_name.beat_studio_note_name is BeatStudioNoteName.HI_TOM
