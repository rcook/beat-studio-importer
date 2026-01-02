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

from colorama import Style
from types import TracebackType
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from _typeshed import SupportsWrite


type Colour = object


class Table:
    def __init__(self, *columns: str | None | tuple[str | None, Colour, str, Colour], column_sep: str = "|") -> None:
        self._column_sep: str = column_sep

        # (header, header_colour, value_format, value_colour, width)
        self._meta: list[tuple[str | None, Colour, str, Colour, int]] = []
        for column in columns:
            match column:
                case None:
                    header = None
                    header_colour = None
                    value_format = "{}"
                    value_colour = None
                case str(header_temp):
                    header = header_temp
                    header_colour = None
                    value_format = "{}"
                    value_colour = None
                case (header_temp, header_colour_temp, value_format_temp, value_colour_temp):
                    header = header_temp
                    header_colour = header_colour_temp
                    value_format = value_format_temp
                    value_colour = value_colour_temp
            self._meta.append((
                header,
                header_colour,
                value_format,
                value_colour,
                0 if header is None else len(header)))
        self._rows: list[list[str]] = []

    def __enter__(self) -> "Table":
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None) -> None:
        pass

    def add_row(self, *values: object) -> None:
        value_count = len(values)
        column_count = len(self._meta)
        if value_count > column_count:
            self._meta += [(None, None,  "{}", None, 0)] * \
                (value_count - column_count)

        row: list[str] = []
        for i, value in enumerate(values):
            header, header_colour, value_format, value_colour, width = self._meta[i]
            s = value_format.format(value)
            s_len = len(s)
            if s_len > width:
                self._meta[i] = (
                    header,
                    header_colour,
                    value_format,
                    value_colour,
                    s_len
                )
            row.append(s)
        self._rows.append(row)

    def print(self, file: "SupportsWrite[str] | None" = None) -> None:
        def pad(values: list[str]) -> list[str]:
            def render(meta: tuple[str | None, Colour, str, Colour, int], value: str) -> str:
                _, _, _, value_colour, width = meta
                s = value.ljust(width)
                if value_colour is None:
                    return s
                else:
                    return str(value_colour) + s + Style.RESET_ALL

            value_count = len(values)
            temp_values = values
            if value_count < column_count:
                temp_values += [""] * (column_count - value_count)

            return [
                render(meta, value)
                for meta, value in zip(self._meta, temp_values)
            ]

        column_count = len(self._meta)

        has_headers = any(map(lambda meta: meta[0] is not None, self._meta))
        if has_headers:
            headers: list[str] = []
            for meta in self._meta:
                header, header_colour, _, _, width = meta
                s = ("" if header is None else header).ljust(width)
                if header_colour is not None:
                    s = str(header_colour) + s + Style.RESET_ALL
                headers.append(s.ljust(width))
            print(*headers, sep=self._column_sep, file=file)

        for row in self._rows:
            print(*pad(row), sep=self._column_sep, file=file)
