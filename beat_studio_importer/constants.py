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
from beat_studio_importer.tempos import BeatStudioTempo
from beat_studio_importer.time_signature import Numerator, TimeSignature


PROGRAM_NAME: str = "beat-studio-importer"

PROGRAM_URL: str = "https://github.com/rcook/beat-studio-importer"

BEAT_STUDIO_TEMPO_RANGE: tuple[BeatStudioTempo, BeatStudioTempo] = (
    BeatStudioTempo(60),
    BeatStudioTempo(200)
)

BEAT_STUDIO_STEP_COUNT_RANGE: tuple[int, int] = (4, 8192)

BEAT_STUDIO_DEFAULT_TIME_SIGNATURE: TimeSignature = TimeSignature(
    Numerator(4),
    NoteValue.QUARTER)
