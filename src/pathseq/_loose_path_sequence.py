from __future__ import annotations

import pathlib
from typing import ClassVar, overload, TypeVar

from typing_extensions import (
    Self,  # PY311+
)

from ._from_disk import find_on_disk
from ._loose_pure_path_sequence import LoosePurePathSequence
from ._parse_loose_path_sequence import parse_path_sequence

PathT = TypeVar("PathT", bound=pathlib.Path, default=pathlib.Path)
PathT_co = TypeVar("PathT_co", covariant=True, bound=pathlib.Path, default=pathlib.Path)


class LoosePathSequence(LoosePurePathSequence[PathT_co]):
    """blah

    TODO: Note that path sequences are not filesystem paths and therefore
    only a subset of filesystem operations are available.
    """

    _pathlib_type: ClassVar[type[pathlib.Path]] = pathlib.Path
    _path: PathT_co

    @overload
    def __init__(self: LoosePathSequence[pathlib.Path], path: str) -> None: ...

    @overload
    def __init__(self: LoosePathSequence[PathT_co], path: PathT_co) -> None: ...

    def __init__(self, path: PathT_co | str) -> None:
        super().__init__(path)

    def expanduser(self) -> Self:
        return self.__class__(self._path.expanduser())

    def absolute(self) -> Self:
        return self.__class__(self._path.absolute())

    def with_existing_paths(self) -> Self:
        """Create a sequence using the ranges of files that exist on disk.

        Each file number sequence in the path sequence will be ordered numerically.

        Raises:
            IncompleteDimensionError: When one or more dimensions in
            a multi-dimension sequence does not have a consistent number of
            files in each other dimension.
        """
        seqs = find_on_disk(self._path, self._parsed)
        return self.with_file_num_seqs(seqs)
