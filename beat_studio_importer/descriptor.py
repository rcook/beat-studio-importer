from dataclasses import dataclass
from functools import cached_property
from typing import Protocol


@dataclass(frozen=True)
class Descriptor:
    name: str | None
    description: str


class HasDescriptor(Protocol):
    @cached_property
    def descriptor(self) -> Descriptor: raise NotImplementedError()
