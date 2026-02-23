from __future__ import annotations

from ._base import BasePathSequence, PathT_co
from ._loose_pure_path_sequence import LoosePurePathSequence


class LoosePathSequence(LoosePurePathSequence[PathT_co], BasePathSequence[PathT_co]):
    """A sequence of Path objects.

    Raises:
        ParseError: When the given path is not a valid path sequence.
    """
