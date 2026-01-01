# pyright: reportAttributeAccessIssue=false

from beat_studio_importer.descriptor import Descriptor
from beat_studio_importer.note import Note, Velocity
from beat_studio_importer.note_name_map import NoteNameMap
from beat_studio_importer.region_builder import RegionBuilder, Tick
from beat_studio_importer.time_signature import TimeSignature
from beat_studio_importer.util import midi_tempo_to_qpm
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property
from mido import MidiFile, MidiTrack
from mido.messages import BaseMessage
from typing import cast


@dataclass(frozen=True)
class Region:
    region_id: int
    start_tick: Tick
    end_tick: Tick
    bars: int
    tempo: int  # microseconds per quarter note
    time_signature: TimeSignature
    notes: list[tuple[Tick, Note]]

    @staticmethod
    def from_midi_messages(f: MidiFile, note_track: MidiTrack, metadata_track: MidiTrack, note_name_map: NoteNameMap) -> "list[Region]":
        def make_region(builder: RegionBuilder, region_id: int) -> Region:
            start_tick = builder.start_tick

            end_tick = builder.end_tick
            assert end_tick is not None

            bars = builder.bars
            assert bars is not None

            tempo = builder.tempo
            assert tempo is not None

            time_signature = builder.time_signature
            assert time_signature is not None

            return Region(
                region_id=region_id,
                start_tick=start_tick,
                end_tick=end_tick,
                bars=bars,
                tempo=tempo,
                time_signature=time_signature,
                notes=builder.notes)

        # Compute regions based on time signature and tempo changes
        builders = RegionBuilder.from_midi_messages(f, metadata_track)

        # Add notes to regions
        i = iter(builders)
        builder = next(i)
        tick = 0
        for m in cast(Iterable[BaseMessage], note_track):
            delta = cast(int, m.time)
            tick += delta
            if cast(str, m.type) != "note_on":
                continue

            if builder.end_tick is not None and tick >= builder.end_tick:
                builder = next(i)

            note_name = note_name_map[cast(int, m.note)]
            note = Note(name=note_name, velocity=cast(Velocity, m.velocity))
            builder.notes.append((tick - builder.start_tick, note))

        assert builder.end_tick is None
        assert builder.bars is None
        assert builder.notes[0][0] == 0
        assert len(builder.notes) > 0
        assert builder.time_signature is not None

        temp = builder.notes[-1][0]
        ticks_per_bar = builder.time_signature.ticks_per_bar(f.ticks_per_beat)
        bars, r = divmod(temp, ticks_per_bar)
        if r > 0:
            bars += 1
        builder.end_tick = builder.start_tick + bars * ticks_per_bar
        builder.bars = bars

        return [make_region(builder, region_id) for region_id, builder in enumerate(builders, 1)]

    @cached_property
    def descriptor(self) -> Descriptor:
        qpm = midi_tempo_to_qpm(self.tempo)
        bpm = self.time_signature.tempo_to_bpm(self.tempo)
        return Descriptor(
            name=None,
            description=f"{self.start_tick}-{self.end_tick}: {qpm}qpm, {bpm}bpm, {self.time_signature}, {self.bars} bars")

    @cached_property
    def ticks(self) -> int:
        return self.end_tick - self.start_tick
