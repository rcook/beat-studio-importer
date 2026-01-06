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
from beat_studio_importer.beat_studio_pattern import BeatStudioPattern, Hits
from beat_studio_importer.beat_studio_tempo import BeatStudioTempo
from beat_studio_importer.beat_studio_velocity import BeatStudioVelocity
from beat_studio_importer.descriptor import Descriptor
from beat_studio_importer.events import NoteEvent, TempoEvent, TimeSignatureEvent
from beat_studio_importer.misc import MidiNote, Ppqn, RegionId, Tick
from beat_studio_importer.midi_note_name_map import MidiNoteNameMap
from beat_studio_importer.note_value import NoteValue
from beat_studio_importer.quantize_util import quantize
from beat_studio_importer.tempos import Bpm, MidiTempo, Qpm, midi_tempo_to_qpm, qpm_to_midi_tempo
from beat_studio_importer.time_signature import Numerator, TimeSignature
from beat_studio_importer.timeline import Timeline
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from fractions import Fraction
from functools import cached_property
from logging import Logger
from typing import Self, cast
import logging


LOGGER: Logger = logging.getLogger(__name__)


DEFAULT_MIDI_TEMPO: MidiTempo = qpm_to_midi_tempo(Qpm(Fraction(120)))
DEFAULT_TIME_SIGNATURE: TimeSignature = TimeSignature(
    numerator=Numerator(4),
    denominator=NoteValue.QUARTER)


@dataclass(frozen=True)
class Region:
    id: RegionId
    ppqn: Ppqn  # ticks per beat, ppqn, tpqn etc.
    start_tick: Tick
    end_tick: Tick
    tempo: MidiTempo
    time_signature: TimeSignature
    notes: list[NoteEvent]
    bar_count: int

    @classmethod
    def build_all(cls: type[Self], timeline: Timeline, discard_boundary_hits: bool = True) -> list[Self]:
        def partition[K, T](func: Callable[[T], K], items: Iterable[T]) -> dict[K, list[T]]:
            d: dict[K, list[T]] = {}
            for item in items:
                key = func(item)
                d.setdefault(key, []).append(item)
            return d

        state = RegionBuildState(
            region_cls=cls,
            timeline=timeline,
            discard_boundary_hits=discard_boundary_hits)
        for tick, events in state.timeline.events:
            assert all(map(lambda e: e.tick == tick, events))

            d = partition(type, events)
            tempo_events = cast(list[TempoEvent], d.get(TempoEvent, []))
            time_signature_events = cast(
                list[TimeSignatureEvent],
                d.get(TimeSignatureEvent, []))
            note_events = cast(list[NoteEvent], d.get(NoteEvent, []))

            tempo_event_count = len(tempo_events)
            time_signature_event_count = len(time_signature_events)
            if tempo_event_count > 0 or time_signature_event_count > 0:
                assert tempo_event_count <= 1, "conflicting tempo events"
                assert time_signature_event_count <= 1, "conflicting time signature events"

                state.close_region(tick)
                assert state.start_tick == tick

                if tempo_event_count > 0:
                    state.tempo_event = tempo_events[0]
                if time_signature_event_count > 0:
                    state.time_signature_event = time_signature_events[0]

            if state.start_tick is None:
                state.start_tick = tick

            state.note_events.extend(note_events)

        state.close_region(None)
        return state.regions

    @cached_property
    def descriptor(self) -> Descriptor:
        return Descriptor(
            name=None,
            description=f"{self.start_tick}-{self.end_tick}: {self.qpm:.1f}qpm, {self.bpm:.1f}bpm, {self.time_signature}, {self.bar_count} bars")

    # Tempo as quarter notes per minute
    @cached_property
    def qpm(self) -> Qpm:
        return midi_tempo_to_qpm(self.tempo)

    # Tempo as beats (pulses) per minute
    @cached_property
    def bpm(self) -> Bpm:
        return self.time_signature.pulse.midi_tempo_to_bpm(self.tempo)

    def render(self, name: str, note_name_map: MidiNoteNameMap, quantum: NoteValue, tempo: BeatStudioTempo | None = None, repeat: int | None = None) -> BeatStudioPattern:
        ignored_notes: set[MidiNote] = set()

        tempo = tempo or BeatStudioTempo.from_midi_tempo(self.tempo)

        ticks_per_step = quantum.ticks(self.ppqn)

        tick_count = self.end_tick - self.start_tick
        step_count, r = divmod(tick_count, ticks_per_step)
        assert r == 0

        total_step_count = step_count if repeat is None else step_count * repeat

        all_hits: Hits = {
            member: [None] * total_step_count
            for member in BeatStudioNoteName
        }

        is_empty = True

        for e in self.notes:
            note_name = note_name_map.get(e.note)
            if note_name is None:
                if e.note not in ignored_notes:
                    ignored_notes.add(e.note)
                    if note_name_map.path is None:
                        LOGGER.warning(
                            f"MIDI note {e.note} ignored since it is not in default mapping")
                    else:
                        LOGGER.warning(
                            f"MIDI note {e.note} ignored since it has no mapping in file {note_name_map.path}")
                continue

            # TBD: Combine the quantize and divmod calls into a
            # single operation
            quantized_tick = quantize(
                Tick(e.tick - self.start_tick),
                self.ppqn,
                quantum)
            step, r = divmod(quantized_tick, ticks_per_step)
            assert r == 0

            # Ensure that quantization doesn't push the note
            # beyond the end of the pattern
            step = min(step, step_count - 1)

            hits = all_hits[note_name.beat_studio_note_name]
            velocity = BeatStudioVelocity.from_midi_velocity(e.velocity)
            hits[step] = velocity
            if repeat is None:
                hits[step] = velocity
            else:
                for i in range(repeat):
                    hits[step + i * step_count] = velocity

            is_empty = False

        return BeatStudioPattern(
            name=name,
            tempo=tempo,
            time_signature=self.time_signature,
            quantum=quantum,
            step_count=total_step_count,
            hits=all_hits,
            is_empty=is_empty)


@dataclass(frozen=False)
class RegionBuildState[R: Region]:
    region_cls: type[R]
    timeline: Timeline
    discard_boundary_hits: bool
    tempo: MidiTempo = DEFAULT_MIDI_TEMPO
    time_signature: TimeSignature = DEFAULT_TIME_SIGNATURE
    start_tick: Tick | None = None
    tempo_event: TempoEvent | None = None
    time_signature_event: TimeSignatureEvent | None = None
    note_events: list[NoteEvent] = field(default_factory=list)
    regions: list[R] = field(default_factory=list)

    def close_region(self, end_tick: Tick | None) -> None:
        has_events = self.tempo_event is not None or \
            self.time_signature_event is not None or \
            len(self.note_events) > 0
        if self.start_tick is not None and has_events:
            self._make_region(self.start_tick, end_tick)

        self.start_tick = end_tick
        self.tempo_event = None
        self.time_signature_event = None
        self.note_events = []

    def _make_region(self, start_tick: Tick, end_tick: Tick | None) -> None:
        if self.tempo_event is not None:
            assert self.tempo_event.tick == start_tick
            self.tempo = self.tempo_event.tempo

        if self.time_signature_event is not None:
            assert self.time_signature_event.tick == start_tick
            self.time_signature = self.time_signature_event.time_signature

        ticks_per_bar = self.time_signature.ticks_per_bar(
            self.timeline.ppqn)

        # Handle note hit on boundary: note hit boundary belongs to the
        # next bar so we either discard the hit or extend the region by
        # a whole extra bar to accommodate the hit
        if len(self.note_events) > 0:
            last_tick = self.note_events[-1].tick \
                if end_tick is None \
                else end_tick
            length = last_tick - start_tick

            bar_count, r = divmod(length, ticks_per_bar)
            assert bar_count >= 0 and r >= 0
            if r == 0 and self.discard_boundary_hits:
                e = self.note_events[-1]
                assert e.tick <= last_tick
                if e.tick >= last_tick:
                    e = self.note_events.pop()
            else:
                bar_count += 1
        else:
            bar_count = 1

        adjusted_end_tick = Tick(start_tick + bar_count * ticks_per_bar)

        self.regions.append(
            self.region_cls(
                id=RegionId(len(self.regions)+1),
                ppqn=self.timeline.ppqn,
                start_tick=start_tick,
                end_tick=adjusted_end_tick,
                tempo=self.tempo,
                time_signature=self.time_signature,
                notes=self.note_events,
                bar_count=bar_count))
