from beat_studio_importer.descriptor import Descriptor
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property
from mido import MidiTrack
from mido.messages import BaseMessage
from typing import TypeVar, cast


T = TypeVar("T", bound="TrackSummary")


@dataclass(frozen=True)
class TrackSummary:
    track: MidiTrack
    name: str
    all_events: int
    note_events: int
    metadata_events: int

    @classmethod
    def summarize(cls: type[T], track: MidiTrack) -> T:
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
