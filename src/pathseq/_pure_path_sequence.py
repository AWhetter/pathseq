from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from decimal import Decimal
import os
import pathlib
from typing import overload, Union

import lark
from typing_extensions import (
    Self,  # PY311+
    TypeAlias,  # PY310+
)

from ._file_num_set import FileNumSet, GRAMMAR as RANGE_GRAMMAR, SequenceReducer

Segment: TypeAlias = Union[str, os.PathLike[str], "PurePathSequence"]


# Frame number formats:
# Blender: https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html#render-options
# * "#" and "@" are both a single character of digits.
# Houdini: https://www.sidefx.com/docs/houdini/render/expressions.html
# * "$Fd", where "d" is the number of digits.
# * Also "$FF" but not recommended.
# * Plus more complex expressions.
# Katana: https://learn.foundry.com/katana/3.0/Content/ug/viewing_renders/importing_exporting_catalog.html
# * "#" is a single character of digits.
# Maya: https://help.autodesk.com/view/MAYAUL/2022/ENU/?guid=GUID-25A1CE65-0C66-4114-B8F1-51FE5A638218
# * Not clear...but seems to be "#" is a single character of digits.
# Nuke: Read: https://learn.foundry.com/nuke/content/reference_guide/image_nodes/read.html
#       Write: https://learn.foundry.com/nuke/content/reference_guide/image_nodes/write.html
# * "#" is a single character of digits.
# * "%04d" is printf-style formatting.
# USD value clips: https://openusd.org/release/api/_usd__page__value_clips.html#Usd_ValueClips_Metadata
# * "#" is a single character of digits.

# UDIM formats:
# Arnold: https://help.autodesk.com/view/ARNOL/ENU/?guid=arnold_user_guide_ac_filename_tokens_ac_token_udim_html
# Blender: https://docs.blender.org/manual/en/latest/modeling/meshes/uv/workflows/udims.html#file-substitution-tokens
# Houdini: https://www.sidefx.com/docs/houdini/vex/functions/expand_udim.html
# Mari: https://learn.foundry.com/mari/Content/tutorials/tutorial_5/tutorial_exporting_importing.html
# USD: https://openusd.org/docs/UsdPreviewSurface-Proposal.html#UsdPreviewSurfaceProposal-TextureReader
# All match MaterialX spec: https://materialx.org/Specification.html (Arnold only supports <UDIM>)
# * <UDIM>: UDIM = 1001 + U + V*10
# * <UVTILE>: uU_vV
# Houdini additionally uses:
# * %(UDIM)d: Same as <UDIM> but with user specified padding
# * %(U)d: The UVTILE style u-coordinate (int(u)+1), with user specified padding
# * %(V)d: The UVTILE style v-coordinate (int(v)+1), with user specified padding
# * %(UVTILE)d: Same as <UVTILE> but with user specified padding


_GRAMMAR = r"""
    path_seq: ranges PAD_FORMAT path_seq
        | PATH_CHAR [path_seq] -> unroll

    PATH_CHAR: /./

    PAD_FORMAT: /#+(\.#+)?/
        | "<UDIM>"
        | "<UVTILE>"
""" + RANGE_GRAMMAR + r"\n%override start: path_seq"

@lark.v_args(inline=True)
class PathSeqReducer(SequenceReducer):
    def unroll(self, char, seq):
        if not seq:
            return [char]

        if isinstance(seq[0], str):
            return [char + seq[0]] + seq[1:]

        return [char] + seq

    def path_seq(self, ranges, format_, seq):
        # TODO: Normalise all ranges to the same type
        return [PaddedRange(FileNumSet(ranges), str(format_))] + seq


@dataclass
class PaddedRange:
    file_num_set: FileNumSet | None
    padding: str

_PARSER = lark.Lark(_GRAMMAR, parser="lalr", transformer=PathSeqReducer())


@dataclass
class _PurePathPart:
    path: str
    file_num_set: FileNumSet | None


# TODO: What about sequences that do not have the range baked into the string?
class PurePathSequence:
    """A generic class that represents a path sequence in the system's path flavour.

    Instantiating this class creates either a :class:`PurePosixPathSequence`
    or a :class:`PureWindowsPathSequence`.

    Differences:
    * No __bytes__ because not a filesystem path.
    * No __fspath__ because not a filesystem path.
    * No as_uri because not a filesystem path.
    """
    def __new__(cls, *args, **kwargs):
        if cls is PurePathSequence:
            cls = PureWindowsPathSequence if os.name == "nt" else PurePosixPathSequence
        return object.__new__(cls)

    def __init__(self, *pathsegments: Segment) -> None:
        self._path = pathlib.PurePath(*pathsegments)
        parts = self._path.parts
        parsed_parts = tuple(_PARSER.parse(part) for part in parts)
        # TODO: Parse each part

    # General properties
    # TODO: Sequences with the same range should match.
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self._path == other._path

    # TODO: Ranges don't have these so maybe sequences shouldn't either
    def __lt__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self._path < other._path

    def __le__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self._path <= other._path

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self._path > other._path

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self._path >= other._path

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.as_posix())

    def __str__(self):
        return str(self._path)

    def __hash__(self):
        return hash((type(self), self._path))

    # Path operations
    def __truediv__(self, key):
        try:
            return self.with_segments(self, key)
        except TypeError:
            return NotImplemented

    def __rtruediv__(self, key):
        try:
            return self.with_segments(key, self)
        except TypeError:
            return NotImplemented

    @property
    def parts(self) -> tuple[str]:
        return self._path.parts

    @property
    def drive(self) -> str:
        return self._path.drive

    @property
    def root(self) -> str:
        return self._path.root

    @property
    def anchor(self) -> str:
        return self._path.anchor

    @property
    def name(self) -> str:
        return self._path.name

    @property
    def suffix(self) -> str:
        return self._path.suffix

    @property
    def suffixes(self) -> list[str]:
        """Everything after the padding?"""
        raise NotImplementedError

    @property
    def stem(self) -> str:
        raise NotImplementedError

    @property
    def parents(self) -> Sequence[Self]:
        raise NotImplementedError

    @property
    def parent(self) -> Self | pathlib.PurePath:
        raise NotImplementedError

    def as_posix(self) -> str:
        return self._path.as_posix()

    def is_reserved(self) -> bool:
        return self._path.is_reserved()

    def is_relative_to(self, other: Segment) -> bool:
        raise NotImplementedError

    def match(self, path_pattern: str, *, case_sensitive: bool | None = None) -> bool:
        pass

    def relative_to(self, other: Segment, *, walk_up: bool = False) -> Self:
        pass

    def with_name(self, name: str) -> Self:
        pass

    def with_stem(self, stem: str) -> Self:
        pass

    def with_suffix(self, suffix: str) -> Self:
        pass

    def joinpath(self, *other: Segment) -> Self:
        pass

    def with_segments(self, *other: Segment) -> Self:
        pass

    # Sequence specific methods
    def as_path(self) -> pathlib.PurePath:
        """blah

        Raises:
            ValueError: If there is more than one path in this sequence,
                and therefore it cannot be represented as a single path object.
        """

    # TODO: Should we inherit from Sequence or similar?
    @overload
    def __getitem__(self, index: int) -> pathlib.PurePath:
        ...

    @overload
    def __getitem__(self, index: slice) -> Self:
        ...

    def __getitem__(self, index):
        pass

    def __iter__(self) -> Iterable[pathlib.PurePath]:
        pass

    def __len__(self) -> int:
        pass

    # TODO: Document how 'name' is constructed (stem, padding, suffix)
    @property
    def padding(self) -> str:
        """The right-most padding of the final path component.

        Returns:
            The empty string when there is no padding.
        """

    @property
    def paddings(self) -> tuple[str]:
        """All padding string in the final path component."""

    def with_paddings(self, *paddings: str) -> Self:
        """Set new pads.

        Raises:
            ValueError: When the number of provided padding strings does not match
                the number of padding strings in the final path component.
        """

    @classmethod
    def from_paths(self, paths: Iterable[os.PathLike[str]]) -> Iterable[Self | pathlib.PurePath]:
        """Create one or more path sequences from a list of paths."""

    def path(self, *numbers: int | Decimal | None) -> Self | pathlib.PurePath:
        """Return a path for the given file number(s) in the sequence.

        None means don't fill in this range.
        """

    def file_num_set(self) -> FileNumSet | None:
        """The right-most file numbers of the final path component."""

    def file_num_sets(self) -> tuple[FileNumSet] | None:
        """All file number sets in the final path component."""

    def with_file_num_sets(self, sets: Iterable[FileNumSet]) -> Self:
        pass


class PurePosixPathSequence(PurePathSequence):
    pass


class PureWindowsPathSequence(PurePathSequence):
    pass
