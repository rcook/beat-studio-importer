from beat_studio_importer.note_name import NoteName
from dataclasses import dataclass


type Velocity = int


@dataclass(frozen=True)
class Note:
    name: NoteName
    velocity: Velocity
