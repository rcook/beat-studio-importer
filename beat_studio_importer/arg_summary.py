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

from bisect import insort_left
from dataclasses import dataclass
from typing import Self, cast


@dataclass(frozen=True)
class ArgSummary:
    attrs: list[tuple[str, str]]

    @classmethod
    def summarize(cls: type[Self], args: object) -> Self:
        def render_value(value: object) -> str:
            match value:
                case bool() as x: return str(x).lower()
                case _: return str(value)

        attrs: list[tuple[str, str]] = []

        for name in dir(args):
            if name.startswith("_") or name in ["add", "all", "handler", "level"]:
                continue
            value = cast(object, getattr(args, name))
            if value is None:
                continue

            attrs.append((name, render_value(value)))

        return cls(attrs=sorted(attrs))

    def append(self, name: str, value: str) -> "ArgSummary":
        attrs = self.attrs.copy()
        insort_left(attrs, (name, value))
        return self.__class__(attrs=attrs)
