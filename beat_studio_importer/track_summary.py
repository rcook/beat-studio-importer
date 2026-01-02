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

from beat_studio_importer.descriptor import Descriptor
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property
from mido import MidiTrack
from mido.messages import BaseMessage
from typing import Self, cast


@dataclass(frozen=True)
class TrackSummary:
    track: MidiTrack
    name: str
    all_events: int
    note_events: int
    metadata_events: int

    @classmethod
    def summarize(cls: type[Self], track: MidiTrack) -> Self:
        events = list(map(
            lambda t: t.is_meta,
            cast(Iterable[BaseMessage], track)))
        metadata_events = sum(1 for e in events if e)
        all_events = len(events)
        note_events = all_events - metadata_events
        return cls(
            track=track,
            name=cast(str, track.name),
            all_events=all_events,
            note_events=note_events,
            metadata_events=metadata_events)

    @cached_property
    def descriptor(self) -> Descriptor:
        is_probably_metadata_track = self.metadata_events > self.note_events
        s = "probable metadata track" \
            if is_probably_metadata_track \
            else "probable note track"
        return Descriptor(
            name=self.name,
            description=f"{self.all_events} events in total, {self.note_events} note events and {self.metadata_events} metadata events, {s}")
