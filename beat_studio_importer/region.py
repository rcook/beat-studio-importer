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

# pyright: reportAttributeAccessIssue=false

from beat_studio_importer.beat_studio_note_name import BeatStudioNoteName
from beat_studio_importer.beat_studio_velocity import BeatStudioVelocity
from beat_studio_importer.descriptor import Descriptor
from beat_studio_importer.beat_studio_pattern import BeatStudioPattern, Hits
from beat_studio_importer.midi_types import MidiVelocity
from beat_studio_importer.note import Note
from beat_studio_importer.note_name_map import NoteNameMap
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.region_builder import RegionBuilder, Tick
from beat_studio_importer.tempo_util import midi_tempo_to_qpm
from beat_studio_importer.time_signature import TimeSignature
from collections.abc import Iterable
from dataclasses import dataclass
from fractions import Fraction
from functools import cached_property
from mido import MidiTrack
from mido.messages import BaseMessage
from typing import cast


@dataclass(frozen=True)
class Region:
    region_id: int
    ticks_per_beat: int
    start_tick: Tick
    end_tick: Tick
    bars: int
    tempo: int
    time_signature: TimeSignature
    notes: list[tuple[Tick, Note]]

    @staticmethod
    def from_midi_messages(note_track: MidiTrack, metadata_track: MidiTrack, note_name_map: NoteNameMap, ticks_per_beat: int, silently_discard_hit_on_boundary: bool = True) -> "list[Region]":
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
                ticks_per_beat=ticks_per_beat,
                start_tick=start_tick,
                end_tick=end_tick,
                bars=bars,
                tempo=tempo,
                time_signature=time_signature,
                notes=builder.notes)

        # Compute regions based on time signature and tempo changes
        builders = RegionBuilder.from_midi_messages(
            metadata_track,
            ticks_per_beat)

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
            note = Note(
                name=note_name,
                velocity=MidiVelocity(cast(int, m.velocity)))
            builder.notes.append((tick - builder.start_tick, note))

        assert builder.end_tick is None
        assert builder.bars is None
        assert builder.notes[0][0] == 0
        assert len(builder.notes) > 0
        assert builder.time_signature is not None

        last_note_tick = builder.notes[-1][0]
        ticks_per_bar = builder.time_signature.ticks_per_bar(ticks_per_beat)

        # Handle note hit on boundary
        bars, r = divmod(last_note_tick, ticks_per_bar)
        assert bars >= 0 and r >= 0
        if r == 0 and silently_discard_hit_on_boundary:
            _ = builder.notes.pop()
        else:
            bars += 1

        builder.end_tick = builder.start_tick + bars * ticks_per_bar
        builder.bars = bars

        return [make_region(builder, region_id) for region_id, builder in enumerate(builders, 1)]

    @cached_property
    def descriptor(self) -> Descriptor:
        return Descriptor(
            name=None,
            description=f"{self.start_tick}-{self.end_tick}: {self.qpm:.1f}qpm, {self.bpm:.1f}bpm, {self.time_signature}, {self.bars} bars")

    @cached_property
    def ticks(self) -> int:
        return self.end_tick - self.start_tick

    # Tempo as quarter notes per minute
    @cached_property
    def qpm(self) -> Fraction:
        return midi_tempo_to_qpm(self.tempo)

    # Tempo as basis beats per minute
    @cached_property
    def bpm(self) -> Fraction:
        return self.time_signature.basis.midi_tempo_to_bpm(self.tempo)

    def render(self, name: str, quantize: NoteValue, override_tempo: int | None = None) -> BeatStudioPattern:
        ticks_per_step, r = divmod(self.ticks_per_beat * 4, quantize.value[0])
        assert r == 0

        steps, r = divmod(self.ticks, ticks_per_step)
        assert r == 0

        all_hits: Hits = {
            member: [None] * steps
            for member in BeatStudioNoteName
        }

        for (tick, note) in self.notes:
            step, r = divmod(tick, ticks_per_step)
            assert r == 0
            _, note_name, = note.name.value
            hits = all_hits[note_name]
            hits[step] = BeatStudioVelocity.from_midi_velocity(note.velocity)

        qpm = round(midi_tempo_to_qpm(self.tempo)) \
            if override_tempo is None \
            else override_tempo

        return BeatStudioPattern(
            name=name,
            qpm=qpm,
            time_signature=self.time_signature,
            quantize=quantize,
            steps=steps,
            hits=all_hits)
